"""
Dependency Injection untuk DIBS AI
Single source of truth untuk semua dependencies
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, AsyncGenerator
import logging

from config.settings import settings
from database.manager import DatabaseManager
from chat.language.language_detector import LanguageDetector
from utils.errors import AuthError

logger = logging.getLogger(__name__)

# ===== SECURITY =====
security = HTTPBearer()

# ===== DATABASE =====
_db_manager: Optional[DatabaseManager] = None

async def get_db() -> AsyncGenerator[DatabaseManager, None]:
    """Dependency untuk database connection"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(str(settings.DB_PATH))
        await _db_manager.connect()
        logger.info("✅ Database connected via dependency")
    
    try:
        yield _db_manager
    finally:
        # Don't close here - let lifespan handle it
        pass

# ===== TOKO DATABASE =====
_toko_db = None

async def get_toko_db():
    """Dependency untuk toko database"""
    global _toko_db
    if _toko_db is None:
        from toko.database import TokoDatabase
        _toko_db = TokoDatabase(str(settings.BACKEND_DIR / "toko.db"))
        await _toko_db.connect()
        await _toko_db.init_db()
        logger.info("✅ Toko database connected via dependency")
    
    return _toko_db

# ===== LANGUAGE DETECTOR =====
_language_detector: Optional[LanguageDetector] = None

def get_language_detector() -> LanguageDetector:
    """Dependency untuk language detector"""
    global _language_detector
    if _language_detector is None:
        _language_detector = LanguageDetector()
        logger.info("✅ Language detector initialized via dependency")
    
    return _language_detector

# ===== AI CLIENT =====
_ai_client = None

async def get_ai_client():
    """Dependency untuk AI client (NVIDIA/Ollama)"""
    global _ai_client
    if _ai_client is None:
        from chat.core import AIProvider
        _ai_client = AIProvider()
        logger.info("✅ AI client initialized via dependency")
    
    return _ai_client

# ===== VIDEO AGENT =====
_video_agent = None

async def get_video_agent(db: DatabaseManager = Depends(get_db)):
    """Dependency untuk video agent"""
    global _video_agent
    if _video_agent is None:
        from video_agent import initialize_video_agent
        _video_agent = initialize_video_agent(db, settings.OLLAMA_URL)
        logger.info("✅ Video agent initialized via dependency")
    
    return _video_agent

# ===== CURRENT USER =====
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Dependency untuk mendapatkan current user dari token"""
    from auth.utils import verify_token
    
    token = credentials.credentials
    user = await verify_token(token)
    
    if not user:
        raise AuthError("Token tidak valid atau expired")
    
    return user

# ===== OPTIONAL USER =====
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """Dependency untuk optional user (boleh tidak login)"""
    if not credentials:
        return None
    
    from auth.utils import verify_token
    return await verify_token(credentials.credentials)

# ===== SETTINGS =====
def get_settings():
    """Dependency untuk settings"""
    return settings


async def get_db_manager():
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(str(settings.DB_PATH))
        await _db_manager.connect()
    try:
        yield _db_manager
    finally:
        pass
