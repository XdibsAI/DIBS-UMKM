from utils.errors import handle_errors
"""Authentication Routes"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import logging
from pydantic import BaseModel

from .models import UserCreate, UserLogin, LoginResponse
from .utils import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    TokenData,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
logger = logging.getLogger('DIBS1')

# Database will be injected
db = None


def set_database(database):
    global db
    db = database


class ResetPasswordRequest(BaseModel):
    email: str
    old_password: str
    new_password: str


@router.post("/register")
@handle_errors
async def register(user: UserCreate):
    """Register new user"""
    try:
        existing = await db.fetch_one(
            "SELECT * FROM users WHERE email = ?",
            (user.email,),
        )
        if existing:
            raise HTTPException(400, "Email already registered")

        password_hash = hash_password(user.password)

        import uuid
        user_id = str(uuid.uuid4())

        await db.execute(
            """
            INSERT INTO users (id, email, password_hash, display_name, gender, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                user.email,
                password_hash,
                user.display_name,
                user.gender,
                datetime.utcnow().isoformat(),
            ),
        )

        token = create_access_token({"user_id": user_id, "email": user.email})

        logger.info(f"✅ User registered: {user.email} (Gender: {user.gender})")
        return {
            "status": "success",
            "data": LoginResponse(
                token=token,
                user_id=user_id,
                email=user.email,
                display_name=user.display_name,
                gender=user.gender,
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Register error: {e}")
        raise HTTPException(500, str(e))


@router.post("/login")
@handle_errors
async def login(credentials: UserLogin):
    """User login"""
    try:
        user = await db.fetch_one(
            "SELECT * FROM users WHERE email = ?",
            (credentials.email,),
        )
        if not user:
            raise HTTPException(401, "Invalid credentials")

        if not verify_password(credentials.password, user['password_hash']):
            raise HTTPException(401, "Invalid credentials")

        token = create_access_token({"user_id": user['id'], "email": user['email']})
        user_dict = dict(user)

        logger.info(f"✅ Login: {credentials.email}")
        return {
            "status": "success",
            "data": LoginResponse(
                token=token,
                user_id=user_dict['id'],
                email=user_dict['email'],
                display_name=user_dict.get('display_name', 'User'),
                gender=user_dict.get('gender', 'unknown'),
            ),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(500, str(e))


@router.post("/reset-password")
@handle_errors
async def reset_password(payload: ResetPasswordRequest):
    """Reset password via JSON body"""
    try:
        email = payload.email.strip().lower()
        old_password = payload.old_password
        new_password = payload.new_password

        if not email or not old_password or not new_password:
            raise HTTPException(400, "Email, password lama, dan password baru wajib diisi")

        if old_password == new_password:
            raise HTTPException(400, "Password baru harus berbeda dari password lama")

        if len(new_password) < 6:
            raise HTTPException(400, "Password baru minimal 6 karakter")

        user = await db.fetch_one(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        )
        if not user:
            raise HTTPException(404, "User tidak ditemukan")

        if not verify_password(old_password, user['password_hash']):
            raise HTTPException(401, "Password lama salah")

        new_hash = hash_password(new_password)

        await db.execute(
            "UPDATE users SET password_hash = ? WHERE email = ?",
            (new_hash, email),
        )

        logger.info(f"✅ Password reset: {email}")
        return {
            "status": "success",
            "message": "Password berhasil diperbarui",
            "data": {
                "email": email,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(500, str(e))


@router.get("/me")
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user info"""
    user = await db.fetch_one(
        "SELECT * FROM users WHERE id = ?",
        (current_user.user_id,),
    )
    if not user:
        raise HTTPException(404, "User not found")

    user_dict = dict(user)

    return {
        "status": "success",
        "data": {
            "id": user_dict['id'],
            "email": user_dict['email'],
            "display_name": user_dict.get('display_name', ''),
            "gender": user_dict.get('gender', ''),
        },
    }


@router.get("/verify")
async def verify_token(current_user: TokenData = Depends(get_current_user)):
    """Verify if token is valid"""
    return {
        "status": "success",
        "data": {
            "user_id": current_user.user_id,
            "email": current_user.email,
        },
    }
