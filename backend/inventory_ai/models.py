from pydantic import BaseModel
from typing import Optional, List


class InventoryIntentResult(BaseModel):
    matched: bool
    intent: str = "unknown"
    product_query: str = ""
    size_value: Optional[float] = None
    size_unit: Optional[str] = None
    keywords: List[str] = []
    raw_text: str = ""
