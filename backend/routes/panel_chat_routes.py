from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth.utils import get_current_user
from dependencies import get_db_manager
from services.panel_chat_service import PanelChatService

router = APIRouter(prefix="/api/v1/panel-chat", tags=["panel-chat"])


class PanelChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


def _user_id_of(current_user) -> str:
    if isinstance(current_user, dict):
        for key in ("id", "user_id", "sub"):
            if key in current_user and current_user[key] is not None:
                return str(current_user[key])
    for key in ("id", "user_id", "sub"):
        if hasattr(current_user, key):
            value = getattr(current_user, key)
            if value is not None:
                return str(value)
    raise HTTPException(status_code=401, detail="Invalid current user payload")


def get_panel_chat_service(db_manager=Depends(get_db_manager)) -> PanelChatService:
    return PanelChatService(db_manager)


@router.post("")
async def panel_chat(
    payload: PanelChatRequest,
    current_user=Depends(get_current_user),
    service: PanelChatService = Depends(get_panel_chat_service),
):
    result = await service.handle_message(
        user_id=_user_id_of(current_user),
        message=payload.message,
    )
    return {
        "status": "success",
        "data": result,
    }
