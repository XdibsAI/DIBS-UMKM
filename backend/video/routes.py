from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from pathlib import Path
import logging

from auth.utils import get_current_user, TokenData
from config.settings import ENABLE_VIDEO_GENERATION, PUBLIC_URL
from video.pipeline import VideoPipeline, VideoStatus

logger = logging.getLogger("DIBS1")

router = APIRouter(prefix="/api/v1/video", tags=["Video"])

db = None
video_agent = None


def set_database(database):
    global db
    db = database


def set_video_agent(agent):
    global video_agent
    video_agent = agent


class VideoCreateRequest(BaseModel):
    prompt: Optional[str] = None
    niche: Optional[str] = None
    product_name: Optional[str] = None
    price_text: Optional[str] = None
    cta_text: Optional[str] = None
    brand_name: Optional[str] = None
    product_image_url: Optional[str] = None
    duration: int = Field(default=30, ge=5, le=180)
    style: str = "engaging"
    language: str = "id"


async def ensure_video_projects_table():
    if db is None:
        raise RuntimeError("Database belum diinisialisasi")

    await db.execute(
        """
        CREATE TABLE IF NOT EXISTS video_projects (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            niche TEXT NOT NULL,
            duration INTEGER NOT NULL DEFAULT 30,
            style TEXT NOT NULL DEFAULT 'engaging',
            language TEXT NOT NULL DEFAULT 'id',
            status TEXT NOT NULL DEFAULT 'pending',
            video_path TEXT,
            error_message TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )


def _user_id(current_user: TokenData) -> str:
    return str(getattr(current_user, "user_id", getattr(current_user, "id", "")))


def _resolve_video_file(video_path: str) -> Optional[Path]:
    if not video_path:
        return None

    raw = Path(video_path)
    candidates = [
        raw,
        Path("/home/dibs/dibs1/videos") / raw.name,
        Path("/home/dibs/dibs1/backend/videos") / raw.name,
    ]

    for p in candidates:
        if p.exists() and p.is_file():
            return p

    return None


def _serialize_project(project: Dict[str, Any]) -> Dict[str, Any]:
    project_id = str(project.get("id", ""))
    status = project.get("status", VideoStatus.PENDING.value)
    download_url = None
    video_url = None

    if status == VideoStatus.COMPLETED.value and project.get("video_path"):
        download_url = f"{PUBLIC_URL}/api/v1/video/download/{project_id}"
        video_url = download_url

    thumbnail_url = None
    if project.get("thumbnail_path"):
        thumb_name = str(project.get("thumbnail_path")).split("/")[-1]
        thumbnail_url = f"{PUBLIC_URL}/api/v1/video/thumbnail/{thumb_name}"

    return {
        "id": project_id,
        "project_id": project_id,
        "prompt": project.get("prompt"),
        "type": project.get("type"),
        "plan_json": project.get("plan_json"),
        "niche": project.get("niche"),
        "duration": project.get("duration"),
        "style": project.get("style"),
        "language": project.get("language"),
        "status": status,
        "video_path": project.get("video_path"),
        "video_url": video_url,
        "download_url": download_url,
        "thumbnail_url": thumbnail_url,
        "error_message": project.get("error_message"),
        "created_at": project.get("created_at"),
        "updated_at": project.get("updated_at"),
    }


@router.post("/create")
async def create_video_project(
    request: VideoCreateRequest,
    current_user: TokenData = Depends(get_current_user),
):
    if not ENABLE_VIDEO_GENERATION:
        raise HTTPException(503, "Video generation is currently disabled")

    if db is None:
        raise HTTPException(500, "Database belum siap")

    await ensure_video_projects_table()

    user_id = _user_id(current_user)
    pipeline = VideoPipeline(db)

    effective_prompt = (request.prompt or request.niche or "").strip()
    if len(effective_prompt) < 3:
        raise HTTPException(400, "Prompt atau niche minimal 3 karakter")

    project_id = await pipeline.create_project(
        user_id=user_id,
        prompt=effective_prompt,
        niche=request.niche or effective_prompt,
        product_name=request.product_name,
        price_text=request.price_text,
        cta_text=request.cta_text,
        brand_name=request.brand_name,
        product_image_url=request.product_image_url,
        duration=request.duration,
        style=request.style,
        language=request.language,
    )

    project = await pipeline.get_project(project_id, user_id)
    payload = _serialize_project(project) if project else {
        "id": project_id,
        "project_id": project_id,
        "prompt": effective_prompt,
        "type": "general",
        "status": VideoStatus.PENDING.value,
    }

    return {
        "status": "success",
        "data": payload,
    }


@router.get("/status/{project_id}")
async def get_video_status(
    project_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    if db is None:
        raise HTTPException(500, "Database belum siap")

    await ensure_video_projects_table()

    user_id = _user_id(current_user)

    project = await db.fetch_one(
        """
        SELECT id, user_id, prompt, type, plan_json, niche, duration, style, language, status,
               video_path, thumbnail_path, error_message, created_at, updated_at
        FROM video_projects
        WHERE id = ? AND user_id = ?
        """,
        (project_id, user_id),
    )

    if not project:
        raise HTTPException(404, "Project not found")

    return {
        "status": "success",
        "data": _serialize_project(dict(project)),
    }


@router.get("/list")
async def list_videos(
    limit: int = 10,
    offset: int = 0,
    current_user: TokenData = Depends(get_current_user),
):
    if db is None:
        raise HTTPException(500, "Database belum siap")

    await ensure_video_projects_table()

    user_id = _user_id(current_user)

    rows = await db.fetch_all(
        """
        SELECT id, user_id, prompt, type, plan_json, niche, duration, style, language, status,
               video_path, thumbnail_path, error_message, created_at, updated_at
        FROM video_projects
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
        """,
        (user_id, limit, offset),
    )

    return {
        "status": "success",
        "data": [_serialize_project(dict(r)) for r in rows],
    }


@router.get("/download/{project_id}")
async def download_video(
    project_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    if db is None:
        raise HTTPException(500, "Database belum siap")

    await ensure_video_projects_table()

    user_id = _user_id(current_user)

    project = await db.fetch_one(
        """
        SELECT id, status, video_path
        FROM video_projects
        WHERE id = ? AND user_id = ?
        """,
        (project_id, user_id),
    )

    if not project:
        raise HTTPException(404, "Project not found")

    project = dict(project)

    if project.get("status") != VideoStatus.COMPLETED.value:
        raise HTTPException(409, "Video belum selesai dibuat")

    resolved = _resolve_video_file(project.get("video_path") or "")
    if not resolved:
        raise HTTPException(404, "File video tidak ditemukan")

    return FileResponse(
        path=str(resolved),
        media_type="video/mp4",
        filename=resolved.name,
    )


@router.delete("/delete/{project_id}")
async def delete_video_project(
    project_id: str,
    current_user: TokenData = Depends(get_current_user),
):
    if db is None:
        raise HTTPException(500, "Database belum siap")

    await ensure_video_projects_table()

    user_id = _user_id(current_user)

    project = await db.fetch_one(
        """
        SELECT id, video_path
        FROM video_projects
        WHERE id = ? AND user_id = ?
        """,
        (project_id, user_id),
    )

    if not project:
        raise HTTPException(404, "Project not found")

    project = dict(project)

    resolved = _resolve_video_file(project.get("video_path") or "")
    if resolved and resolved.exists():
        try:
            resolved.unlink()
        except Exception as e:
            logger.warning(f"Gagal hapus file video {resolved}: {e}")

    await db.execute(
        "DELETE FROM video_projects WHERE id = ? AND user_id = ?",
        (project_id, user_id),
    )

    return {
        "status": "success",
        "message": "Video project deleted",
    }


@router.get("/thumbnail/{filename}")
async def get_video_thumbnail(filename: str):
    from fastapi.responses import FileResponse
    thumb_path = Path("videos") / filename
    if not thumb_path.exists():
        raise HTTPException(404, "Thumbnail not found")
    return FileResponse(str(thumb_path), media_type="image/jpeg")
