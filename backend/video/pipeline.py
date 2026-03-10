"""
Video Pipeline with prompt planning support + thumbnails
"""
import asyncio
import os
import json
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
import logging
import uuid

from video.core import video_editor, tts_handler, story_generator
from video.video_planner import video_planner
from video.image_generator import scene_image_generator
from video.serper_image_search import search_product_image, build_visual_search_query

logger = logging.getLogger(__name__)


def assign_images_to_scenes(plan, uploaded_image_paths=None, fallback_image=None):
    scenes = plan.get("scenes") or []
    clean_paths = []

    for path in (uploaded_image_paths or []):
        if isinstance(path, str) and path.strip():
            clean_paths.append(path.strip())

    if not clean_paths and fallback_image:
        clean_paths = [fallback_image]

    if not clean_paths:
        return plan

    total = len(clean_paths)
    for idx, scene in enumerate(scenes):
        assigned = clean_paths[idx % total]
        scene["assigned_image_path"] = assigned
        scene["product_image_url"] = assigned

    plan["uploaded_image_paths"] = clean_paths
    plan["product_image_url"] = clean_paths[0]
    return plan


def resolve_visual_image(uploaded_image_path, uploaded_image_paths, product_image_url, product_name, prompt, plan):
    try:
        if uploaded_image_paths:
            for item in uploaded_image_paths:
                if item and isinstance(item, str) and os.path.exists(item):
                    return item

        if uploaded_image_path and isinstance(uploaded_image_path, str) and os.path.exists(uploaded_image_path):
            return uploaded_image_path

        if product_image_url and isinstance(product_image_url, str) and product_image_url.strip():
            return product_image_url.strip()

        from video.serper_image_search import search_product_image, build_visual_search_query

        query = build_visual_search_query(
            prompt=prompt or "",
            subject=(plan or {}).get("subject") or "",
            product_name=product_name or (plan or {}).get("product_name") or "",
            video_type=(plan or {}).get("type") or "general",
            style=(plan or {}).get("style") or "",
            scene_kind="product",
        )
        return search_product_image(query)
    except Exception:
        return None


def resolve_visual_image(uploaded_image_path, product_image_url, product_name, prompt, plan):
    try:
        if uploaded_image_path and isinstance(uploaded_image_path, str) and os.path.exists(uploaded_image_path):
            return uploaded_image_path

        if product_image_url and isinstance(product_image_url, str) and product_image_url.strip():
            return product_image_url.strip()

        from video.serper_image_search import search_product_image, build_visual_search_query

        query = build_visual_search_query(
            prompt=prompt or "",
            subject=(plan or {}).get("subject") or "",
            product_name=product_name or (plan or {}).get("product_name") or "",
            video_type=(plan or {}).get("type") or "general",
            style=(plan or {}).get("style") or "",
            scene_kind="product",
        )
        return search_product_image(query)
    except Exception:
        return None



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
        if "thumbnail_path" not in existing:
            await self.db.execute("ALTER TABLE video_projects ADD COLUMN thumbnail_path TEXT")

    async def create_project(
        self,
        user_id: str,
        prompt: str,
        niche: str,
        product_name: Optional[str] = None,
        price_text: Optional[str] = None,
        cta_text: Optional[str] = None,
        brand_name: Optional[str] = None,
        product_image_url: Optional[str] = None,
        uploaded_image_path: Optional[str] = None,
        uploaded_image_paths: Optional[List[str]] = None,
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
            product_image_url=product_image_url,
        )

        final_type = plan.get("type", "general")
        final_duration = int(plan.get("duration", duration) or duration)

        await self.db.execute("""
            INSERT INTO video_projects
            (id, user_id, niche, duration, style, language, status, prompt, type, plan_json, thumbnail_path, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            None,
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
                product_image_url=product_image_url,
                uploaded_image_path=uploaded_image_path,
                uploaded_image_paths=uploaded_image_paths,
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
        product_image_url: Optional[str],
        uploaded_image_path: Optional[str],
        uploaded_image_paths: Optional[List[str]],
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
                product_image_url=product_image_url,
            )

            resolved_product_image_url = resolve_visual_image(
                uploaded_image_path=uploaded_image_path,
                uploaded_image_paths=uploaded_image_paths,
                product_image_url=product_image_url,
                product_name=product_name,
                prompt=prompt,
                plan=plan,
            )

            plan = assign_images_to_scenes(
                plan=plan,
                uploaded_image_paths=uploaded_image_paths,
                fallback_image=resolved_product_image_url,
            )

            # Auto-find product image via Serper if none provided
            resolved_product_image_url = product_image_url
            if not resolved_product_image_url:
                search_query = (
                    product_name
                    or plan.get("product_name")
                    or plan.get("subject")
                    or niche
                    or prompt
                )
                resolved_product_image_url = search_product_image(search_query or "")

            if resolved_product_image_url:
                plan["product_image_url"] = resolved_product_image_url
                for scene in plan.get("scenes", []):
                    if not scene.get("product_image_url"):
                        scene["product_image_url"] = resolved_product_image_url

            # Generate image asset per scene
            scenes = plan.get("scenes") or []
            brand_name_for_assets = plan.get("brand_name") or "DIBS AI"

            for idx, scene in enumerate(scenes, start=1):
                try:
                    image_path = scene_image_generator.generate_scene_image(
                        project_id=project_id,
                        scene_index=idx,
                        scene_data=scene,
                        brand_name=brand_name_for_assets,
                    )
                    scene["image_path"] = image_path
                except Exception as image_error:
                    logger.warning(
                        f"Scene image generation failed for {project_id} scene {idx}: {image_error}"
                    )

            plan["scenes"] = scenes

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

            scenes = plan.get("scenes") or []
            narration_parts = []
            for scene in scenes:
                title = str(scene.get("title") or "").strip()
                text = str(scene.get("text") or "").strip()
                kind = str(scene.get("kind") or "").strip().lower()

                if kind == "cta" and scene.get("cta_text"):
                    text = str(scene.get("cta_text") or "").strip()

                chunk = " ".join([x for x in [title, text] if x]).strip()
                if chunk:
                    narration_parts.append(chunk)

            script = "\n".join(narration_parts[:8]).strip()

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

            thumbnail_filename = f"thumb_{project_id[:8]}.jpg"
            thumbnail_path = await video_editor.create_thumbnail_from_video(
                video_path=video_path,
                output_filename=thumbnail_filename,
                second=1.0,
            )

            await self.db.execute(
                """
                UPDATE video_projects
                SET thumbnail_path = ?, updated_at = ?
                WHERE id = ?
                """,
                (thumbnail_path, datetime.now().isoformat(), project_id)
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

        if result.get('thumbnail_path'):
            filename = str(result['thumbnail_path']).split('/')[-1]
            result['thumbnail_url'] = f"{PUBLIC_URL}/api/v1/video/thumbnail/{filename}"

        return result
