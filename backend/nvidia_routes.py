from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

from nvidia_wrapper import ask_nvidia

router = APIRouter(prefix="/api/v1/nvidia", tags=["NVIDIA"])
logger = logging.getLogger('DIBS1.NVIDIA')

class ChatRequest(BaseModel):
    message: str
    temperature: float = 1.0
    max_tokens: int = 16384

@router.post("/chat")
async def chat_with_nvidia(request: ChatRequest):
    """Chat dengan NVIDIA Nemotron"""
    try:
        response = ask_nvidia(request.message)
        return {
            "status": "success",
            "data": {
                "response": response
            }
        }
    except Exception as e:
        logger.error(f"NVIDIA chat error: {e}")
        raise HTTPException(500, str(e))

@router.get("/models")
async def get_models():
    """List available models"""
    return {
        "status": "success",
        "data": {
            "models": [
                {
                    "name": "Nemotron-3-Nano-30B",
                    "provider": "NVIDIA",
                    "description": "30B parameter model untuk chat umum"
                }
            ]
        }
    }
