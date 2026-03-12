from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from auth.utils import get_current_user
from dependencies import get_db_manager
from services.customer_service import CustomerService

router = APIRouter(prefix="/api/v1/customers", tags=["customers"])


class CustomerCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    phone: str = ""
    store_name: str = ""
    address: str = ""
    customer_type: str = ""
    notes: str = ""
    extra: Dict[str, Any] = {}


class CustomerUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    store_name: Optional[str] = None
    address: Optional[str] = None
    customer_type: Optional[str] = None
    notes: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


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


@router.post("/draft")
async def create_customer_draft(
    payload: CustomerCreateRequest,
    current_user=Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    try:
        draft = await service.prepare_customer_create(
            user_id=_user_id_of(current_user),
            data=payload.model_dump(),
        )
        return {
            "status": "success",
            "data": draft,
            "message": draft["summary_text"],
            "needs_confirmation": True,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/draft/latest")
async def get_latest_customer_draft(
    current_user=Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    draft = await service.get_latest_pending_draft(
        user_id=_user_id_of(current_user),
    )
    if not draft:
        return {"status": "success", "data": None, "message": "Tidak ada draft pending"}
    return {
        "status": "success",
        "data": draft,
        "message": draft["summary_text"],
        "needs_confirmation": True,
    }


@router.post("/draft/{draft_id}/confirm")
async def confirm_customer_draft(
    draft_id: int,
    current_user=Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    try:
        result = await service.confirm_draft(
            draft_id=draft_id,
            user_id=_user_id_of(current_user),
        )
        return {
            "status": "success",
            "data": result,
            "message": "Draft berhasil disimpan ke database",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/draft/{draft_id}/cancel")
async def cancel_customer_draft(
    draft_id: int,
    current_user=Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    try:
        result = await service.cancel_draft(
            draft_id=draft_id,
            user_id=_user_id_of(current_user),
        )
        return {
            "status": "success",
            "data": result,
            "message": "Draft dibatalkan",
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("")
async def create_customer(
    payload: CustomerCreateRequest,
    current_user=Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    item = await service.create_customer(
        user_id=_user_id_of(current_user),
        name=payload.name,
        phone=payload.phone,
        store_name=payload.store_name,
        address=payload.address,
        customer_type=payload.customer_type,
        notes=payload.notes,
        extra=payload.extra,
    )
    return {"status": "success", "data": item}


@router.put("/{customer_id}")
async def update_customer(
    customer_id: int,
    payload: CustomerUpdateRequest,
    current_user=Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    item = await service.update_customer(
        customer_id=customer_id,
        user_id=_user_id_of(current_user),
        data=payload.model_dump(exclude_unset=True),
    )
    if not item:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"status": "success", "data": item}


@router.get("")
async def list_customers(
    q: str = Query("", description="Search keyword"),
    limit: int = Query(50, ge=1, le=200),
    current_user=Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    rows = await service.list_customers(
        user_id=_user_id_of(current_user),
        q=q,
        limit=limit,
    )
    return {"status": "success", "data": rows, "count": len(rows)}


@router.get("/{customer_id}")
async def get_customer(
    customer_id: int,
    current_user=Depends(get_current_user),
    service: CustomerService = Depends(get_customer_service),
):
    item = await service.get_customer(
        customer_id=customer_id,
        user_id=_user_id_of(current_user),
    )
    if not item:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"status": "success", "data": item}
