"""
DIBS Video Agent - FULL VERSION
Orchestrates: Script → TTS → Video Rendering
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class VideoGenerationAgent:
    """Full video generation pipeline"""
    
    def __init__(self, db_manager, ollama_url: str):
        self.db = db_manager
        self.ollama_url = ollama_url
        
        # Import video generator
        from video_generator import video_generator
        self.generator = video_generator
    
    async def create_video_project(
        self,
        user_id: str,
        niche: str,
        duration: int,
        style: str = "engaging",
        language: str = "id"
    ) -> Dict:
        """Create video project & start generation"""
        try:
            project_id = str(uuid.uuid4())
            
            await self.db.execute(
                """INSERT INTO video_projects 
                (id, user_id, niche, duration, style, language, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (project_id, user_id, niche, duration, style, language, 
                 'pending', datetime.now().isoformat())
            )
            
            # Start full pipeline in background
            asyncio.create_task(self._generate_full_video(
                project_id, user_id, niche, duration, style, language
            ))
            
            return {
                "project_id": project_id,
                "status": "pending",
                "message": "Video generation started..."
            }
            
        except Exception as e:
            logger.error(f"Create project error: {e}")
            raise
    
    async def _generate_full_video(
        self,
        project_id: str,
        user_id: str,
        niche: str,
        duration: int,
        style: str,
        language: str
    ):
        """Full pipeline: Script → Audio → Video"""
        try:
            # STEP 1: Generate script (dummy for now, can use Ollama)
            await self.db.execute(
                "UPDATE video_projects SET status = ? WHERE id = ?",
                ('generating_script', project_id)
            )
            
            script_data = {
                "title": f"{niche.title()} - Tips & Tricks",
                "hook": f"Hai! Ini cara mudah untuk {niche}",
                "body": f"Langkah pertama, pahami dasarnya. Kedua, praktik konsisten. Ketiga, evaluasi progress. Dengan ketiga langkah ini, kamu pasti bisa menguasai {niche} dengan baik!",
                "cta": "Like dan subscribe untuk tips lainnya!"
            }
            
            await self.db.execute(
                """UPDATE video_projects 
                SET script = ?, status = ?, updated_at = ?
                WHERE id = ?""",
                (json.dumps(script_data), 'generating_audio', 
                 datetime.now().isoformat(), project_id)
            )
            
            # STEP 2: Generate audio
            audio_path = await self.generator.generate_audio_from_script(
                script_data, language
            )
            
            await self.db.execute(
                "UPDATE video_projects SET status = ? WHERE id = ?",
                ('rendering_video', project_id)
            )
            
            # STEP 3: Render video
            output_filename = f"video_{project_id[:8]}.mp4"
            video_path = await self.generator.create_video_with_text(
                audio_path, script_data, output_filename, duration
            )
            
            # STEP 4: Update completion
            await self.db.execute(
                """UPDATE video_projects 
                SET video_path = ?, status = ?, updated_at = ?
                WHERE id = ?""",
                (video_path, 'completed', 
                 datetime.now().isoformat(), project_id)
            )
            
            logger.info(f"✅ Video project {project_id} COMPLETED")
            
        except Exception as e:
            logger.error(f"Full pipeline error: {e}")
            await self.db.execute(
                "UPDATE video_projects SET status = ?, error = ? WHERE id = ?",
                ('failed', str(e), project_id)
            )
    
    async def get_project_status(self, project_id: str, user_id: str) -> Optional[Dict]:
        """Get project with download link"""
        project = await self.db.fetch_one(
            "SELECT * FROM video_projects WHERE id = ? AND user_id = ?",
            (project_id, user_id)
        )
        
        if not project:
            return None
        
        result = dict(project)
        
        # Parse script
        if result.get('script'):
            try:
                result['script'] = json.loads(result['script'])
            except:
                pass
        
        # Add download URL if completed
        if result.get('video_path') and result['status'] == 'completed':
            filename = result['video_path'].split('/')[-1]
            result['download_url'] = f"http://94.100.26.128:9091/videos/{filename}"
        
        return result

# Global instance
video_agent = None

def initialize_video_agent(db_manager, ollama_url: str):
    global video_agent
    video_agent = VideoGenerationAgent(db_manager, ollama_url)
    logger.info("🎬 Full Video Agent initialized")
    return video_agent
