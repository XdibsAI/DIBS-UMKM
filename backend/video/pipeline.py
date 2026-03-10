"""
Video Pipeline with prompt planning support
"""
import asyncio
import json
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import uuid

from video.core import video_editor, tts_handler, story_generator
from video.video_planner import video_planner

logger = logging.getLogger(__name__)


class VideoStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    PROCESSING = "processing"
    SCRIPT_GENERATING = "script_generating"
    AUDIO_GENERATING = "audio_generating"
    VIDEO_RENDERING = "video_rendering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class VideoPipeline:
    """Manage video generation pipeline with proper status tracking"""

    def __init__(self, db_manager, ollama_url: str = None):
        self.db = db_manager
        self.ollama_url = ollama_url
        self.active_tasks: Dict[str, asyncio.Task] = {}

    async def _ensure_columns(self):
        columns = await self.db.fetch_all("PRAGMA table_info(video_projects)")
        existing = {dict(c)["name"] for c in columns}

        if "prompt" not in existing:
            await self.db.execute("ALTER TABLE video_projects ADD COLUMN prompt TEXT")
        if "type" not in existing:
            await self.db.execute("ALTER TABLE video_projects ADD COLUMN type TEXT")
        if "plan_json" not in existing:
            await self.db.execute("ALTER TABLE video_projects ADD COLUMN plan_json TEXT")

    async def create_project(
        self,
        user_id: str,
        prompt: str,
        niche: str,
        product_name: Optional[str] = None,
        price_text: Optional[str] = None,
        cta_text: Optional[str] = None,
        brand_name: Optional[str] = None,
        duration: int = 30,
        style: str = "engaging",
        language: str = "id"
    ) -> str:
        await self._ensure_columns()

        project_id = str(uuid.uuid4())
        plan = video_planner.build_plan(
            prompt=prompt,
            duration=duration,
            style=style,
            language=language,
            product_name=product_name,
            price_text=price_text,
            cta_text=cta_text,
            brand_name=brand_name,
        )

        final_type = plan.get("type", "general")
        final_duration = int(plan.get("duration", duration) or duration)

        await self.db.execute("""
            INSERT INTO video_projects
            (id, user_id, niche, duration, style, language, status, prompt, type, plan_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id,
            user_id,
            niche,
            final_duration,
            style,
            language,
            VideoStatus.PENDING.value,
            prompt,
            final_type,
            json.dumps(plan, ensure_ascii=False),
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))

        logger.info(f"✅ Video project created: {project_id}")

        asyncio.create_task(
            self.process_project(
                project_id=project_id,
                prompt=prompt,
                niche=niche,
                product_name=product_name,
                price_text=price_text,
                cta_text=cta_text,
                brand_name=brand_name,
                duration=final_duration,
                style=style,
                language=language,
            )
        )

        return project_id

    async def process_project(
        self,
        project_id: str,
        prompt: str,
        niche: str,
        product_name: Optional[str],
        price_text: Optional[str],
        cta_text: Optional[str],
        brand_name: Optional[str],
        duration: int,
        style: str,
        language: str,
    ):
        try:
            await self._update_status(project_id, VideoStatus.PLANNING)

            plan = video_planner.build_plan(
                prompt=prompt,
                duration=duration,
                style=style,
                language=language,
                product_name=product_name,
                price_text=price_text,
                cta_text=cta_text,
                brand_name=brand_name,
            )

            await self.db.execute(
                """
                UPDATE video_projects
                SET type = ?, plan_json = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    plan.get("type", "general"),
                    json.dumps(plan, ensure_ascii=False),
                    datetime.now().isoformat(),
                    project_id,
                )
            )

            await self._update_status(project_id, VideoStatus.PROCESSING)

            await self._update_status(project_id, VideoStatus.SCRIPT_GENERATING)
            script_seed = plan.get("subject") or niche
            if product_name:
                script_seed = f"{product_name} {plan.get('price_text') or ''}".strip()

            script_data = await story_generator.generate_script(
                niche=script_seed,
                style=style,
                duration=duration
            )
            script = script_data.get("full_script", "")

            if not script:
                raise Exception("Script generation failed")

            await self._update_status(project_id, VideoStatus.AUDIO_GENERATING)
            audio_path = await self._generate_audio(script, language)

            if not audio_path:
                raise Exception("Audio generation failed")

            await self._update_status(project_id, VideoStatus.VIDEO_RENDERING)
            output_filename = f"video_{project_id[:8]}.mp4"

            video_path = await video_editor.create_video_from_script(
                script=script,
                audio_path=audio_path,
                output_filename=output_filename,
                duration=duration,
                text_effects={"plan": plan},
            )

            await self._update_status(
                project_id,
                VideoStatus.COMPLETED,
                video_path=video_path
            )

            logger.info(f"🎬 Project {project_id} completed successfully")

        except Exception as e:
            await self._update_status(
                project_id,
                VideoStatus.FAILED,
                error=str(e)
            )
            logger.error(f"❌ Project {project_id} failed: {e}")

    async def _generate_audio(self, script: str, language: str) -> Optional[str]:
        for attempt in range(3):
            try:
                audio_path = await tts_handler.generate(script, language)
                if audio_path:
                    return audio_path
                await asyncio.sleep(1 * (attempt + 1))
            except Exception as e:
                logger.warning(f"Audio attempt {attempt+1} failed: {e}")
        return None

    async def _update_status(self, project_id: str, status: VideoStatus, **kwargs):
        updates = ['status = ?', 'updated_at = ?']
        params = [status.value, datetime.now().isoformat()]

        if 'video_path' in kwargs:
            updates.append('video_path = ?')
            params.append(kwargs['video_path'])

        if 'error' in kwargs:
            updates.append('error_message = ?')
            params.append(kwargs['error'])

        params.append(project_id)

        await self.db.execute(f"""
            UPDATE video_projects
            SET {', '.join(updates)}
            WHERE id = ?
        """, params)

    async def get_project(self, project_id: str, user_id: str) -> Optional[Dict]:
        from config.settings import PUBLIC_URL

        await self._ensure_columns()

        project = await self.db.fetch_one(
            "SELECT * FROM video_projects WHERE id = ? AND user_id = ?",
            (project_id, user_id)
        )

        if not project:
            return None

        result = dict(project)

        if result.get('video_path') and result['status'] == VideoStatus.COMPLETED.value:
            result['download_url'] = f"{PUBLIC_URL}/api/v1/video/download/{project_id}"

        return result
