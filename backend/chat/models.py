"""Chat Models"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: Optional[datetime] = None

class ChatSession(BaseModel):
    session_id: str
    name: str
    created_at: datetime
    message_count: int = 0

class SendMessageRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    session_id: str
    user_message: ChatMessage
    assistant_message: ChatMessage
