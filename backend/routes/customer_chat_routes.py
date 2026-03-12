from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from auth.utils import get_current_user
from dependencies import get_db_manager
from services.customer_service import CustomerService
from chat.customer_intents import execute_customer_intent

router = APIRouter(prefix="/api/v1/customer-chat", tags=["customer-chat"])


class CustomerChatRequest(BaseModel):
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


def get_customer_service(db_manager=Depends(get_db_manager)) -> CustomerService:
    return CustomerService(db_manager)


@router.post("")
async def customer_chat_action(
    payload: CustomerChatRequest,
    current_user=Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    result = await execute_customer_intent(
        user_id=_user_id_of(current_user),
        message=payload.message,
        service=service,
    )
    return {"status": "success", **result}
