"""
Compatibility Check - No Streamlit
"""
import sys
import platform
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def check_python_version() -> Dict[str, Any]:
    """Check Python version compatibility"""
    version = sys.version_info
    return {
        'compatible': version.major == 3 and version.minor >= 8,
        'version': f"{version.major}.{version.minor}.{version.micro}",
        'required': '3.8+',
        'message': 'OK' if version.major == 3 and version.minor >= 8 else 'Upgrade ke Python 3.8+'
    }

def check_platform() -> Dict[str, Any]:
    """Check platform compatibility"""
    system = platform.system()
    return {
        'system': system,
        'release': platform.release(),
        'compatible': True,  # All platforms supported
        'message': f'Running on {system}'
    }

def check_disk_space(path: str = '.', required_gb: float = 1.0) -> Dict[str, Any]:
    """Check available disk space"""
    import shutil
    
    try:
        usage = shutil.disk_usage(path)
        free_gb = usage.free / (1024**3)
        
        return {
            'compatible': free_gb >= required_gb,
            'free_gb': round(free_gb, 2),
            'required_gb': required_gb,
            'message': f'Free: {free_gb:.2f}GB, Required: {required_gb}GB'
        }
    except Exception as e:
        return {
            'compatible': False,
            'error': str(e),
            'message': f'Gagal cek disk space: {e}'
        }

def get_system_info() -> Dict[str, Any]:
    """Get complete system information"""
    import psutil
    
    try:
        return {
            'python': check_python_version(),
            'platform': check_platform(),
            'disk': check_disk_space(),
            'memory': {
                'total_gb': round(psutil.virtual_memory().total / (1024**3), 2),
                'available_gb': round(psutil.virtual_memory().available / (1024**3), 2),
                'percent_used': psutil.virtual_memory().percent
            },
            'cpu': {
                'count': psutil.cpu_count(),
                'percent': psutil.cpu_percent(interval=1)
            }
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {
            'python': check_python_version(),
            'platform': check_platform(),
            'error': str(e)
        }
