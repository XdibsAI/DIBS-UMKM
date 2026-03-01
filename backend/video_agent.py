"""
DIBS Video Agent - Uses new core modules
"""
import logging
from video.pipeline import VideoPipeline

logger = logging.getLogger(__name__)

# Global instance
video_agent = None

def initialize_video_agent(db_manager, ollama_url: str):
    global video_agent
    video_agent = VideoPipeline(db_manager, ollama_url)
    logger.info("🎬 Video Agent initialized with core modules")
    return video_agent
