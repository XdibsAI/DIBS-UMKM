from routes.customer_routes import router as customer_router
from routes.customer_chat_routes import router as customer_chat_router
from routes.chatbot_routes import router as chatbot_router
"""
DIBS AI - Modular Architecture
Version 2.0.0
"""
import sys
import os

# Calculate project root (go up from backend/)
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent  # /home/dibs/dibs1
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "dibs.db"
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from config.settings import (
    DB_PATH, UPLOADS_DIR, VIDEOS_DIR, BACKEND_DIR,
    OLLAMA_URL, ENABLE_REMINDERS, DATA_DIR, HOST, PORT
)
# Import configurations
from config.settings import settings
from config.logging import logger

# Import database
from database.manager import DatabaseManager

# Import video agent & language intelligence
from video_agent import initialize_video_agent
from chat.language.language_detector import LanguageDetector

# Import routers
from auth.routes import router as auth_router, set_database as set_auth_db
from chat.routes import router as chat_router, set_database as set_chat_db
from knowledge.routes import router as knowledge_router, set_database as set_knowledge_db
from video.routes import router as video_router, set_database as set_video_db, set_video_agent
from video.upload_routes import router as video_upload_router
from video.vision_routes import router as vision_router

# ===== TOKO MODULE =====
# from toko.database import TokoDatabase
from toko.routes import router as toko_router, set_database as set_toko_db
from social.routes import router as social_router, set_database as set_social_db
from business_brain.routes import router as business_brain_router, set_database as set_business_brain_db
from inventory_ai.routes import router as inventory_ai_router
from inventory_ai.import_export_routes import router as inventory_import_export_router
from nvidia_routes import router as nvidia_router
# Try import dibs_routes, but don't fail if not exists
try:
    from dibs_routes import router as dibs_router
    dibs_router_available = True
except ImportError:
    dibs_router_available = False
    logger.warning("⚠️ dibs_routes.py not found, skipping import")

# Global instances
db = None
toko_db = None
video_agent = None
language_ai = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global db, toko_db, video_agent, language_ai

    logger.info("🚀 Starting DIBS AI v2.0.0 (Modular Architecture)")
    logger.info(f"📁 Using database: {str(DB_PATH)}")
    logger.info(f"📁 Uploads: {settings.UPLOADS_DIR}")
    logger.info(f"📁 Videos: {settings.VIDEOS_DIR}")

    # ===== INITIALIZE MAIN DATABASE =====
    db = DatabaseManager(str(str(DB_PATH)))
    await db.connect()
    logger.info("✅ Main database connected")

    # ===== TOKO MODULE (Centralized) =====
    toko_db = db  # Menggunakan database utama
    logger.info("✅ Toko module redirected to main database")

    # ===== INITIALIZE OTHER COMPONENTS =====
    video_agent = initialize_video_agent(db, settings.OLLAMA_URL)
    language_ai = LanguageDetector()

    # ===== INJECT DEPENDENCIES =====
    set_auth_db(db)
    set_chat_db(db)
    set_knowledge_db(db)
    set_video_db(db)
    set_video_agent(video_agent)
    set_toko_db(db)
    set_business_brain_db(db)

    logger.info("✅ All modules initialized")

    # === REMINDER SYSTEM ===
    if settings.ENABLE_REMINDERS:
        logger.info("🔔 Initializing reminder system...")
        from reminders.models import get_reminder_manager
        from reminders.scheduler import get_scheduler

        try:
            reminder_mgr = get_reminder_manager()
            await reminder_mgr.initialize()
            logger.info("✅ Reminder tables initialized")

            scheduler = get_scheduler()
            scheduler_task = asyncio.create_task(scheduler.start())
            logger.info("✅ Reminder scheduler task created")
        except Exception as e:
            logger.error(f"❌ Reminder system error: {e}")

    yield
    # ===== GRACEFUL SHUTDOWN =====
    
    async def shutdown_handler(sig, frame):
        """Handle shutdown gracefully"""
        
        # Close database connections
        if db:
            await db.close()
        
        # Cancel reminder scheduler
        from reminders.scheduler import get_scheduler
        scheduler = get_scheduler()
        scheduler.stop()
    
    loop = asyncio.get_event_loop()


    # ===== CLEANUP =====
    await db.close()
    # await toko_db.close() (Shared with main db)
    logger.info("👋 DIBS AI stopped")

# Create FastAPI app
app = FastAPI(
    title="DIBS AI - Modular",
    description="Digital Intelligent Business System - Modular Architecture",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static uploads
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOADS_DIR)), name="uploads")

# Include routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(knowledge_router)
app.include_router(video_router)
app.include_router(video_upload_router)
app.include_router(vision_router)
app.include_router(toko_router)
app.include_router(social_router)
app.include_router(business_brain_router)
app.include_router(inventory_ai_router)
app.include_router(inventory_import_export_router)
app.include_router(nvidia_router)
if dibs_router_available:
    app.include_router(dibs_router)
app.include_router(customer_router)
app.include_router(customer_chat_router)
app.include_router(chatbot_router)

# Health endpoint
@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "architecture": "modular",
        "components": {
            "database": "connected" if db else "disconnected",
            "toko_database": "connected" if toko_db and toko_db.db else "disconnected",
            "ai": "online",
            "video_agent": "ready" if video_agent else "not initialized"
        },
        "system": {
            "active_sessions": 0,
            "active_tasks": 0,
            "data_dir": str(settings.DATA_DIR),
            "uploads_dir": str(settings.UPLOADS_DIR)
        }
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "DIBS AI - Digital Intelligent Business System",
        "version": "2.0.0",
        "architecture": "modular",
        "docs": "/api/docs"
    }

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info"
    )

