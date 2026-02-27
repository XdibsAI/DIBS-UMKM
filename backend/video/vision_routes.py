"""Vision API Routes - Image Analysis & Script Generation"""
import os
import uuid
import base64
import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import aiofiles

from openai import OpenAI
from config.settings import settings
from auth.utils import get_current_user, TokenData

logger = logging.getLogger('DIBS1.VISION')

router = APIRouter(prefix="/api/video/vision", tags=["vision"])

# Konfigurasi
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Inisialisasi OpenAI client untuk NVIDIA - PASTI SAMA
client = OpenAI(
    api_key=settings.nvidia_api_key,
    base_url="https://integrate.api.nvidia.com/v1"
)

class ScriptResponse(BaseModel):
    success: bool
    image_id: Optional[str] = None
    product_name: Optional[str] = None
    script: Optional[str] = None
    video_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None

class VideoGenerateRequest(BaseModel):
    image_id: str
    custom_script: Optional[str] = None
    duration: int = 30

@router.post("/upload", response_model=ScriptResponse)
async def upload_image(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user)
):
    """Upload gambar"""
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(400, "File harus berupa gambar")
        
        image_id = str(uuid.uuid4())
        file_ext = os.path.splitext(file.filename)[1]
        file_path = UPLOAD_DIR / f"{image_id}{file_ext}"
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"✅ Gambar tersimpan: {file_path}")
        
        return ScriptResponse(
            success=True,
            image_id=image_id,
            message="Gambar berhasil diproses"
        )
        
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        return ScriptResponse(success=False, error=str(e))

@router.post("/analyze", response_model=ScriptResponse)
async def analyze_image(
    request: VideoGenerateRequest,
    current_user: TokenData = Depends(get_current_user)
):
    """Analisis gambar dan generate script"""
    try:
        image_files = list(UPLOAD_DIR.glob(f"{request.image_id}.*"))
        if not image_files:
            raise HTTPException(404, "Gambar tidak ditemukan")
        
        image_path = image_files[0]
        
        # Baca gambar
        with open(image_path, 'rb') as f:
            base64_image = base64.b64encode(f.read()).decode('utf-8')
        
        # Vision API - sama persis dengan test
        vision_response = client.chat.completions.create(
            model="meta/llama-3.2-11b-vision-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What product is this? Describe it briefly."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            max_tokens=100
        )
        
        product_desc = vision_response.choices[0].message.content
        
        # Generate script dengan Nemotron
        script_response = client.chat.completions.create(
            model="nvidia/nemotron-3-nano-30b-a3b",
            messages=[
                {
                    "role": "user",
                    "content": f"""Buatkan script video promosi 30 detik untuk produk ini.
Deskripsi: {product_desc}

Format:
HOOK: (kalimat pembuka)
BODY: (deskripsi produk, manfaat)
CTA: (ajakan membeli)"""
                }
            ],
            max_tokens=300
        )
        
        script = script_response.choices[0].message.content
        
        return ScriptResponse(
            success=True,
            image_id=request.image_id,
            product_name="Produk dari gambar",
            script=script,
            message="Analisis berhasil"
        )
        
    except Exception as e:
        logger.error(f"❌ Analyze error: {e}")
        return ScriptResponse(success=False, error=str(e))

@router.get("/image/{image_id}")
async def get_image(
    image_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Get uploaded image"""
    image_files = list(UPLOAD_DIR.glob(f"{image_id}.*"))
    if not image_files:
        raise HTTPException(404, "Image not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(image_files[0])
