import uuid
import hashlib
import time
from datetime import datetime

class IDGenerator:
    """Konsisten ID generator kanggo kabeh project"""
    
    @staticmethod
    def generate_project_id(length: int = 8, prefix: str = "vid") -> str:
        """
        Generate unique project ID
        Format: [prefix]_[timestamp]_[unique]
        Contoh: vid_20260226_1a2b3c4d
        """
        timestamp = datetime.now().strftime("%Y%m%d")
        unique = str(uuid.uuid4())[:length]
        return f"{prefix}_{timestamp}_{unique}"
    
    @staticmethod
    def generate_file_id(original_name: str) -> str:
        """Generate ID kanggo file upload"""
        ext = original_name.split('.')[-1] if '.' in original_name else 'mp4'
        hash_obj = hashlib.md5(f"{original_name}{time.time()}".encode())
        return f"file_{hash_obj.hexdigest()[:10]}.{ext}"
    
    @staticmethod
    def validate_project_id(project_id: str) -> bool:
        """Validasi format project ID"""
        import re
        pattern = r'^[a-z]+_\d{8}_[a-f0-9]{8}$'
        return bool(re.match(pattern, project_id))

# Singleton instance
id_gen = IDGenerator()
