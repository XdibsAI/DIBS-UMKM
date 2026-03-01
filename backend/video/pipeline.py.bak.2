"""
Video Pipeline with proper status tracking
"""
import asyncio
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from video.core.video_editor import video_editor
from video.core.tts_handler import tts_handler

logger = logging.getLogger(__name__)

class VideoStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
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

    async def create_project(self, user_id: str, niche: str, duration: int = 30) -> str:
        """Create new video project"""
        import uuid
        project_id = str(uuid.uuid4())
        
        await self.db.execute("""
            INSERT INTO video_projects 
            (id, user_id, niche, duration, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            project_id, user_id, niche, duration, 
            VideoStatus.PENDING.value,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        logger.info(f"✅ Project created: {project_id}")
        return project_id

    async def process_project(self, project_id: str, script: str, 
                            language: str = 'id', duration: int = 30):
        """Process video project with full pipeline"""
        try:
            # Update status
            await self._update_status(project_id, VideoStatus.PROCESSING)
            
            # Step 1: Generate audio
            await self._update_status(project_id, VideoStatus.AUDIO_GENERATING)
            audio_path = await self._generate_audio(script, language)
            
            if not audio_path:
                raise Exception("Audio generation failed")
            
            # Step 2: Generate video
            await self._update_status(project_id, VideoStatus.VIDEO_RENDERING)
            output_filename = f"video_{project_id[:8]}.mp4"
            video_path = await video_editor.create_video_from_script(
                script=script,
                audio_path=audio_path,
                output_filename=output_filename,
                duration=duration
            )
            
            # Step 3: Update success
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
        """Generate audio with retry"""
        for attempt in range(3):
            try:
                audio_path = await tts_handler.generate(script, language)
                if audio_path:
                    return audio_path
                await asyncio.sleep(1 * (attempt + 1))
            except Exception as e:
                logger.warning(f"Audio attempt {attempt+1} failed: {e}")
        return None

    async def _update_status(self, project_id: str, status: VideoStatus, 
                            **kwargs):
        """Update project status in database"""
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
