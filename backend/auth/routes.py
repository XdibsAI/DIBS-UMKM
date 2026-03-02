from utils.errors import handle_errors, AuthError, ValidationError
"""Authentication Routes"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import logging

from .models import UserCreate, UserLogin, LoginResponse
from .utils import hash_password, verify_password, create_access_token, get_current_user, TokenData

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
logger = logging.getLogger('DIBS1')

# Database will be injected
db = None

def set_database(database):
    global db
    db = database

@router.post("/register")
@handle_errors
async def register(user: UserCreate):
    """Register new user"""
    try:
        # Check if user exists
        existing = await db.fetch_one("SELECT * FROM users WHERE email = ?", (user.email,))
        if existing:
            raise HTTPException(400, "Email already registered")

        # Hash password
        password_hash = hash_password(user.password)

        # Insert user with gender
        import uuid
        user_id = str(uuid.uuid4())
        await db.execute(
            "INSERT INTO users (id, email, password_hash, display_name, gender, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, user.email, password_hash, user.display_name, user.gender, datetime.utcnow().isoformat())
        )

        # Create token
        token = create_access_token({"user_id": user_id, "email": user.email})

        logger.info(f"✅ User registered: {user.email} (Gender: {user.gender})")
        return {
            "status": "success",
            "data": LoginResponse(
                token=token,
                user_id=user_id,
                email=user.email,
                display_name=user.display_name,
                gender=user.gender  # TAMBAH
            )
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
        # Get user
        user = await db.fetch_one("SELECT * FROM users WHERE email = ?", (credentials.email,))
        if not user:
            raise HTTPException(401, "Invalid credentials")

        # Verify password
        if not verify_password(credentials.password, user['password_hash']):
            raise HTTPException(401, "Invalid credentials")

        # Create token
        token = create_access_token({"user_id": user['id'], "email": user['email']})

        # Convert Row to dict agar bisa akses dengan .get()
        user_dict = dict(user)
        
        logger.info(f"✅ Login: {credentials.email}")
        return {
            "status": "success",
            "data": LoginResponse(
                token=token,
                user_id=user_dict['id'],
                email=user_dict['email'],
                display_name=user_dict.get('display_name', 'User'),
                gender=user_dict.get('gender', 'unknown')  # AMAN karena pakai .get() dari dict
            )
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(500, str(e))

@router.post("/reset-password")
async def reset_password(email: str, old_password: str, new_password: str):
    """Reset password"""
    try:
        user = await db.fetch_one("SELECT * FROM users WHERE email = ?", (email,))
        if not user:
            raise HTTPException(401, "Invalid credentials")

        if not verify_password(old_password, user['password_hash']):
            raise HTTPException(401, "Old password incorrect")

        new_hash = hash_password(new_password)
        await db.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, email))

        logger.info(f"✅ Password reset: {email}")
        return {"status": "success", "message": "Password updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(500, str(e))

@router.get("/me")
async def get_current_user_info(current_user: TokenData = Depends(get_current_user)):
    """Get current user info"""
    user = await db.fetch_one("SELECT * FROM users WHERE id = ?", (current_user.user_id,))
    if not user:
        raise HTTPException(404, "User not found")
    return {
        "status": "success",
        "data": {
            "id": user['id'],
            "email": user['email'],
            "display_name": user['display_name'],
            "gender": user.get('gender', '')  # TAMBAH
        }
    }


@router.get("/verify")
async def verify_token(current_user: TokenData = Depends(get_current_user)):
    """Verify if token is valid"""
    return {
        "status": "success",
        "data": {
            "user_id": current_user.user_id,
            "email": current_user.email
        }
    }

