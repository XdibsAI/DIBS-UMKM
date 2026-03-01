"""
Cleanup utility - No Streamlit
Remove temporary files
"""
import os
import logging
import shutil
from pathlib import Path
from typing import List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CleanupManager:
    """Manage cleanup of temporary files"""
    
    def __init__(self, temp_dirs: List[str] = None):
        self.temp_dirs = temp_dirs or ['/tmp', './temp']
        
    def cleanup_old_files(self, max_age_hours: int = 24, 
                         pattern: str = '*.mp3', 
                         directory: str = None) -> int:
        """Remove files older than max_age_hours"""
        if directory is None:
            directory = '/tmp'
            
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        deleted = 0
        
        try:
            for file_path in Path(directory).glob(pattern):
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time < cutoff:
                    file_path.unlink()
                    deleted += 1
                    logger.debug(f"Deleted: {file_path}")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
            
        return deleted
    
    def cleanup_temp_files(self, prefix: str = 'tmp', 
                          max_age_minutes: int = 60) -> int:
        """Clean up temporary files with prefix"""
        import tempfile
        
        temp_dir = tempfile.gettempdir()
        deleted = 0
        
        try:
            for file_path in Path(temp_dir).glob(f"{prefix}*"):
                file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age.total_seconds() > max_age_minutes * 60:
                    file_path.unlink()
                    deleted += 1
        except Exception as e:
            logger.error(f"Temp cleanup error: {e}")
            
        return deleted
    
    def cleanup_directory(self, directory: str, 
                         max_age_days: int = 7) -> int:
        """Clean up entire directory contents older than max_age_days"""
        cutoff = datetime.now() - timedelta(days=max_age_days)
        deleted = 0
        
        try:
            for item in Path(directory).glob('*'):
                item_time = datetime.fromtimestamp(item.stat().st_mtime)
                if item_time < cutoff:
                    if item.is_file():
                        item.unlink()
                    elif item.is_dir():
                        shutil.rmtree(item)
                    deleted += 1
        except Exception as e:
            logger.error(f"Directory cleanup error: {e}")
            
        return deleted


cleanup_manager = CleanupManager()
