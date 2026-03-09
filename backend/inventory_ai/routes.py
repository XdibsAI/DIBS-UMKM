from fastapi import APIRouter
from inventory_ai.router import detect_inventory_intent

router = APIRouter(prefix="/api/v1/inventory-ai", tags=["Inventory AI"])


@router.post("/detect")
async def detect_inventory(data: dict):
    text = str(data.get("text", "")).strip()
    result = detect_inventory_intent(text)
    return {
        "status": "success",
        "data": result.model_dump()
    }
