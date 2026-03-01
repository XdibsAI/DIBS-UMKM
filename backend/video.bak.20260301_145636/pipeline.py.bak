import asyncio
from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
import logging

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
    
    def __init__(self, db_manager, video_generator):
        self.db = db_manager
        self.generator = video_generator
        self.active_tasks: Dict[str, asyncio.Task] = {}
    
    async def create_project(self, script_data: Dict[str, Any]) -> str:
        """Create new video project with proper initialization"""
        from utils.id_generator import id_gen
        
        project_id = id_gen.generate_project_id()
        
        # Save to DB with transaction
        def _save():
            with self.db.transaction() as cursor:
                cursor.execute("""
                    INSERT INTO video_projects 
                    (id, script, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    project_id, 
                    script_data.get('script', ''),
                    VideoStatus.PENDING.value,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
        
        await asyncio.get_event_loop().run_in_executor(None, _save)
        
        logger.info(f"✅ Project created: {project_id}")
        return project_id
    
    async def process_project(self, project_id: str, script_data: Dict[str, Any]):
        """Process video project with full pipeline"""
        try:
            # Update status
            await self._update_status(project_id, VideoStatus.PROCESSING)
            
            # Step 1: Generate audio
            await self._update_status(project_id, VideoStatus.AUDIO_GENERATING)
            audio_result = await self._generate_audio_with_retry(
                project_id, 
                script_data
            )
            
            if not audio_result['success']:
                raise Exception(f"Audio generation failed: {audio_result.get('error')}")
            
            # Step 2: Generate video
            await self._update_status(project_id, VideoStatus.VIDEO_RENDERING)
            video_result = await self._generate_video_with_timeout(
                project_id,
                audio_result['path'],
                script_data
            )
            
            # Step 3: Update success
            await self._update_status(
                project_id, 
                VideoStatus.COMPLETED,
                video_path=video_result['path'],
                duration=video_result.get('duration')
            )
            
            logger.info(f"🎬 Project {project_id} completed successfully")
            
        except asyncio.CancelledError:
            await self._update_status(project_id, VideoStatus.CANCELLED)
            logger.warning(f"Project {project_id} cancelled")
            raise
            
        except Exception as e:
            await self._update_status(
                project_id, 
                VideoStatus.FAILED,
                error=str(e)
            )
            logger.error(f"❌ Project {project_id} failed: {e}", exc_info=True)
    
    async def _generate_audio_with_retry(self, project_id: str, script_data: Dict, max_retries=3):
        """Generate audio with automatic retry"""
        for attempt in range(max_retries):
            try:
                result = await self.generator.generate_audio_from_script(
                    script=script_data['script'],
                    language=self._validate_language(script_data.get('language', 'id')),
                    project_id=project_id
                )
                return {'success': True, 'path': result}
            except Exception as e:
                if attempt == max_retries - 1:
                    return {'success': False, 'error': str(e)}
                await asyncio.sleep(1 * (attempt + 1))
    
    async def _generate_video_with_timeout(self, project_id: str, audio_path: str, script_data: Dict, timeout=300):
        """Generate video with timeout"""
        try:
            result = await asyncio.wait_for(
                self.generator.create_video_with_text(
                    audio_path=audio_path,
                    text_effects=script_data.get('text_effects', {}),
                    project_id=project_id
                ),
                timeout=timeout
            )
            return {'success': True, 'path': result}
        except asyncio.TimeoutError:
            raise Exception(f"Video generation timeout after {timeout}s")
    
    async def _update_status(self, project_id: str, status: VideoStatus, **kwargs):
        """Update project status in database"""
        def _update():
            with self.db.transaction() as cursor:
                updates = ['status = ?', 'updated_at = ?']
                params = [status.value, datetime.now().isoformat()]
                
                if 'video_path' in kwargs:
                    updates.append('video_path = ?')
                    params.append(kwargs['video_path'])
                
                if 'error' in kwargs:
                    updates.append('error_message = ?')
                    params.append(kwargs['error'])
                
                if 'duration' in kwargs:
                    updates.append('duration = ?')
                    params.append(kwargs['duration'])
                
                params.append(project_id)
                
                cursor.execute(f"""
                    UPDATE video_projects 
                    SET {', '.join(updates)}
                    WHERE id = ?
                """, params)
        
        await asyncio.get_event_loop().run_in_executor(None, _update)
    
    def _validate_language(self, lang: str) -> str:
        """Validate and normalize language code"""
        SUPPORTED = {'id': 'id', 'en': 'en', 'ja': 'ja', 'ko': 'ko', 'zh': 'zh'}
        return SUPPORTED.get(lang, 'id')
