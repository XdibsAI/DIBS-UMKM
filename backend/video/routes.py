from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel, validator
from typing import Optional, List
import logging

from video_agent import initialize_video_agent
from utils.errors import with_error_handling, ValidationError
from config.settings import settings
from database.transaction import tx_manager


logger = logging.getLogger('DIBS1')

# Database & video_agent will be injected
db = None
video_agent = None

def set_database(database):
    global db
    db = database

def set_video_agent(agent):
    global video_agent
    video_agent = agent

router = APIRouter(prefix="/api/video", tags=["video"])
logger = logging.getLogger(__name__)

class ScriptData(BaseModel):
    """Validated script data model"""
    script: str
    language: str = "id"
    text_effects: dict = {}
    
    @validator('script')
    def script_not_empty(cls, v):
        if not v or len(v.strip()) < 10:
            raise ValueError('Script minimal 10 karakter')
        return v.strip()
    
    @validator('language')
    def validate_language(cls, v):
        supported = ['id', 'en', 'ja', 'ko', 'zh']
        if v not in supported:
            raise ValueError(f'Language must be one of: {supported}')
        return v

class VideoResponse(BaseModel):
    """Standardized video response"""
    success: bool
    project_id: Optional[str] = None
    status: Optional[str] = None
    video_url: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

# Mock user dependency (ganti karo auth asli)
async def get_current_user():
    return {"id": "user123", "name": "Test User"}

@router.post("/generate", response_model=VideoResponse)
@with_error_handling
async def generate_video(
    script_data: ScriptData,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """
    Generate video from script
    - Validates input
    - Creates project
    - Starts background processing
    - Returns project ID
    """
    logger.info(f"🎬 Video generation requested by user: {current_user['id']}")
    
    # Check feature flag
    if not settings.ENABLE_VIDEO_GENERATION:
        raise HTTPException(503, "Video generation is currently disabled")
    
    # Import here to avoid circular imports
    from video.generator import video_generator
    
    # Create pipeline with generator
    pipeline = VideoPipeline(tx_manager, video_generator)
    
    # Create project
    project_id = await pipeline.create_project(script_data.dict())
    
    # Start background processing
    background_tasks.add_task(
        pipeline.process_project,
        project_id,
        script_data.dict()
    )
    
    return VideoResponse(
        success=True,
        project_id=project_id,
        status=VideoStatus.PENDING.value,
        message="Video generation started"
    )

@router.get("/status/{project_id}", response_model=VideoResponse)
@with_error_handling
async def get_video_status(
    project_id: str,
    current_user = Depends(get_current_user)
):
    """Get video generation status"""
    # Query from database with transaction
    def _query():
        with tx_manager.transaction() as cursor:
            cursor.execute("""
                SELECT status, video_path, error_message, created_at, updated_at
                FROM video_projects WHERE id = ?
            """, (project_id,))
            return cursor.fetchone()
    
    import asyncio
    result = await asyncio.get_event_loop().run_in_executor(None, _query)
    
    if not result:
        raise HTTPException(404, "Project not found")
    
    status = result['status']
    video_url = None
    
    if status == VideoStatus.COMPLETED.value and result['video_path']:
        video_url = f"{settings.VIDEO_SERVER_URL}/videos/{result['video_path']}"
    
    return VideoResponse(
        success=True,
        project_id=project_id,
        status=status,
        video_url=video_url,
        error=result['error_message'] if status == VideoStatus.FAILED.value else None
    )

@router.get("/list", response_model=List[VideoResponse])
@with_error_handling
async def list_videos(
    limit: int = 10,
    offset: int = 0,
    current_user = Depends(get_current_user)
):
    """List user's videos"""
    def _query():
        with tx_manager.transaction() as cursor:
            cursor.execute("""
                SELECT id, status, video_path, created_at
                FROM video_projects 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (current_user['id'], limit, offset))
            return cursor.fetchall()
    
    import asyncio
    projects = await asyncio.get_event_loop().run_in_executor(None, _query)
    
    return [
        VideoResponse(
            success=True,
            project_id=p['id'],
            status=p['status'],
            video_url=f"{settings.VIDEO_SERVER_URL}/videos/{p['video_path']}" if p['video_path'] else None
        )
        for p in projects
    ]
