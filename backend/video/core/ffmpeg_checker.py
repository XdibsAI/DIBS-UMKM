"""
FFmpeg Checker - No Streamlit
"""
import subprocess
import logging
import shutil
from typing import Tuple

logger = logging.getLogger(__name__)

def check_ffmpeg() -> Tuple[bool, str]:
    """Check if FFmpeg is installed and get version"""
    try:
        # Check if ffmpeg is in PATH
        ffmpeg_path = shutil.which('ffmpeg')
        if not ffmpeg_path:
            return False, "FFmpeg tidak ditemukan di PATH"
            
        # Get version
        result = subprocess.run(
            ['ffmpeg', '-version'], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        
        if result.returncode == 0:
            first_line = result.stdout.split('\n')[0]
            return True, first_line
        else:
            return False, "FFmpeg error saat dijalankan"
            
    except FileNotFoundError:
        return False, "FFmpeg tidak terinstall"
    except subprocess.TimeoutExpired:
        return False, "FFmpeg timeout"
    except Exception as e:
        return False, f"Error: {str(e)}"

def get_ffmpeg_path() -> str:
    """Get FFmpeg executable path"""
    return shutil.which('ffmpeg') or 'ffmpeg'

def check_ffprobe() -> bool:
    """Check if ffprobe is available"""
    return shutil.which('ffprobe') is not None
