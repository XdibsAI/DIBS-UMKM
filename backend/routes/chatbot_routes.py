from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth.utils import get_current_user
from dependencies import get_db_manager
from services.chatbot_service import ChatbotService

router = APIRouter(prefix="/api/v1/chatbot", tags=["chatbot"])


class IdentifyContactRequest(BaseModel):
    external_id: str = Field(..., min_length=1)
    channel: str = "chat"
    display_name: str = ""
    phone: str = ""


class InboundMessageRequest(BaseModel):
    external_id: str = Field(..., min_length=1)
    channel: str = "chat"
    display_name: str = ""
    phone: str = ""
    sender_role: str = "customer"
    message_text: str = Field(..., min_length=1)
    message_type: str = "text"


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


def get_chatbot_service(db_manager=Depends(get_db_manager)) -> ChatbotService:
    return ChatbotService(db_manager)


@router.post("/identify")
async def identify_contact(
    payload: IdentifyContactRequest,
    current_user=Depends(get_current_user),
    service: ChatbotService = Depends(get_chatbot_service),
):
    contact = await service.identify_contact(
        user_id=_user_id_of(current_user),
        external_id=payload.external_id,
        channel=payload.channel,
        display_name=payload.display_name,
        phone=payload.phone,
    )
    session = await service.get_or_create_open_session(
        user_id=_user_id_of(current_user),
        contact_id=contact["id"],
    )
    context = await service.get_contact_context(
        user_id=_user_id_of(current_user),
        contact_id=contact["id"],
    )
    return {
        "status": "success",
        "contact": contact,
        "session": session,
        "context": context,
    }


@router.post("/inbound")
async def inbound_message(
    payload: InboundMessageRequest,
    current_user=Depends(get_current_user),
    service: ChatbotService = Depends(get_chatbot_service),
):
    user_id = _user_id_of(current_user)

    contact = await service.identify_contact(
        user_id=user_id,
        external_id=payload.external_id,
        channel=payload.channel,
        display_name=payload.display_name,
        phone=payload.phone,
    )

    session = await service.get_or_create_open_session(
        user_id=user_id,
        contact_id=contact["id"],
    )

    message = await service.append_message(
        user_id=user_id,
        session_id=session["id"],
        contact_id=contact["id"],
        sender_role=payload.sender_role,
        message_text=payload.message_text,
        message_type=payload.message_type,
    )

    context = await service.get_contact_context(
        user_id=user_id,
        contact_id=contact["id"],
    )

    return {
        "status": "success",
        "contact": contact,
        "session": session,
        "message": message,
        "context": context,
    }
