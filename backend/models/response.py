"""
Standard Response Models untuk DIBS AI
"""
from pydantic import BaseModel
from typing import Optional, Any, Dict, List, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """Standard API Response"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None
    error: Optional[str] = None
    timestamp: datetime = datetime.now()
    version: str = "2.0.0"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PaginatedResponse(ApiResponse[List[T]]):
    """Response dengan pagination"""
    total: int
    page: int
    per_page: int
    total_pages: int

class ErrorResponse(BaseModel):
    """Error Response"""
    success: bool = False
    error: str
    code: int
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()

# Specific response models
class HealthResponse(BaseModel):
    status: str
    version: str
    architecture: str
    components: Dict[str, str]
    system: Dict[str, Any]

class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    created_at: datetime

class SessionResponse(BaseModel):
    session_id: str
    name: str
    created_at: datetime
    message_count: int

class MessageResponse(BaseModel):
    role: str
    content: str
    created_at: datetime
