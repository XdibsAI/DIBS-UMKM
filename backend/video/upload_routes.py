import os
import uuid
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/v1/video", tags=["Video Upload"])

UPLOAD_DIR = "/home/dibs/dibs1/uploads/video_assets"
os.makedirs(UPLOAD_DIR, exist_ok=True)


async def get_current_user():
    return {"id": "user123", "name": "Test User"}


@router.post("/upload-image")
async def upload_video_image(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename kosong")

    ext = file.filename.split(".")[-1].lower()
    if ext not in {"jpg", "jpeg", "png", "webp"}:
        raise HTTPException(status_code=400, detail="Format file harus jpg/jpeg/png/webp")

    filename = f"{uuid.uuid4()}.{ext}"
    save_path = os.path.join(UPLOAD_DIR, filename)

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="File kosong")

    with open(save_path, "wb") as f:
        f.write(content)

    return JSONResponse({
        "status": "success",
        "data": {
            "image_path": save_path,
            "filename": filename,
        }
    })
