"""Application Settings - Complete"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file
load_dotenv()


# === PROJECT PATHS ===
PROJECT_ROOT = Path(__file__).parent.parent.parent  # /home/dibs/dibs1
BACKEND_DIR = Path(__file__).parent.parent  # /home/dibs/dibs1/backend
DATA_DIR = PROJECT_ROOT / "data"
UPLOADS_DIR = PROJECT_ROOT / "uploads"
VIDEOS_DIR = PROJECT_ROOT / "videos"

# === DATABASE ===
DB_PATH = DATA_DIR / "dibs.db"
DATABASE_PATH = str(DB_PATH)

# === JWT ===
jwt_secret_key = os.getenv("JWT_SECRET_KEY", "dibsai-secret-key-2024-production-32bytes-long")
jwt_algorithm = "HS256"

# === AI SERVICES ===
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")

# === MCP SERVER ===
MCP_URL = os.getenv("MCP_URL", "http://localhost:8765")
MCP_PORT = int(os.getenv("MCP_PORT", "8765"))

# === VIDEO ===
ENABLE_VIDEO_GENERATION = True
VIDEO_SERVER_URL = "http://localhost:8081"

# === REMINDERS ===
ENABLE_REMINDERS = True

# === FEATURE FLAGS ===
ENABLE_SOCIAL = True
ENABLE_TOKO = True

use_nvidia = os.getenv("USE_NVIDIA", "true").lower() == "true"  # Default TRUE

class Settings(BaseSettings):
    """Pydantic settings with all required fields"""
    # Paths
    BACKEND_DIR: str = str(BACKEND_DIR)
    DB_PATH: str = str(DB_PATH)
    UPLOADS_DIR: str = str(UPLOADS_DIR)
    VIDEOS_DIR: str = str(VIDEOS_DIR)
    DATA_DIR: str = str(DATA_DIR)
    
    # AI
    OLLAMA_URL: str = OLLAMA_URL
    NVIDIA_API_KEY: str = NVIDIA_API_KEY
    USE_NVIDIA: bool = True  # Will be overridden by env
    
    # MCP
    MCP_URL: str = MCP_URL
    MCP_PORT: int = MCP_PORT
    
    # Features
    ENABLE_VIDEO_GENERATION: bool = ENABLE_VIDEO_GENERATION
    ENABLE_REMINDERS: bool = ENABLE_REMINDERS
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"  # Allow extra fields from .env

settings = Settings()

# === SERVER ===
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8081"))

# === LEGACY ALIASES (for backward compatibility) ===
ollama_url = OLLAMA_URL
ollama_timeout = int(os.getenv("OLLAMA_TIMEOUT", "300"))
ai_model = os.getenv("AI_MODEL", "llama3.2:1b")
nvidia_api_key = NVIDIA_API_KEY
nvidia_model = os.getenv("NVIDIA_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct")
nvidia_max_tokens = int(os.getenv("NVIDIA_MAX_TOKENS", "1024"))
nvidia_temperature = float(os.getenv("NVIDIA_TEMPERATURE", "0.7"))

# Lowercase aliases
host = HOST
port = PORT
db_path = str(DB_PATH)
PUBLIC_URL = os.getenv("PUBLIC_URL", "http://94.100.26.128:8081")
