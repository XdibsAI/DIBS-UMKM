"""Authentication Models"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: str
    gender: str  # TAMBAH - wajib diisi saat register

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str
    email: str
    display_name: str
    gender: Optional[str] = None  # TAMBAH - optional untuk kompatibilitas
    created_at: datetime

class LoginResponse(BaseModel):
    token: str
    user_id: str
    email: str
    display_name: str
    gender: Optional[str] = None  # TAMBAH - optional untuk kompatibilitas

class TokenData(BaseModel):
    user_id: str
    email: str
