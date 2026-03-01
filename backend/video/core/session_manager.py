"""
Session Manager - No Streamlit
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class SessionManager:
    """Manage user sessions without Streamlit"""
    
    def __init__(self, storage_dir: str = "session_data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, Dict] = {}
        
    def create_session(self, user_id: str) -> str:
        """Create new session"""
        import uuid
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat(),
            'data': {}
        }
        
        self._save_session(session_id)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        if session_id in self.sessions:
            return self.sessions[session_id]
            
        # Try to load from file
        return self._load_session(session_id)
    
    def update_session(self, session_id: str, data: Dict[str, Any]):
        """Update session data"""
        if session_id in self.sessions:
            self.sessions[session_id]['data'].update(data)
            self.sessions[session_id]['last_active'] = datetime.now().isoformat()
            self._save_session(session_id)
    
    def delete_session(self, session_id: str):
        """Delete session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            
        session_file = self.storage_dir / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
    
    def _save_session(self, session_id: str):
        """Save session to file"""
        if session_id in self.sessions:
            session_file = self.storage_dir / f"{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump(self.sessions[session_id], f, indent=2)
    
    def _load_session(self, session_id: str) -> Optional[Dict]:
        """Load session from file"""
        session_file = self.storage_dir / f"{session_id}.json"
        if session_file.exists():
            with open(session_file, 'r') as f:
                data = json.load(f)
                self.sessions[session_id] = data
                return data
        return None
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Remove old sessions"""
        now = datetime.now()
        to_delete = []
        
        for session_id, data in self.sessions.items():
            last_active = datetime.fromisoformat(data['last_active'])
            age = (now - last_active).total_seconds() / 3600
            
            if age > max_age_hours:
                to_delete.append(session_id)
                
        for session_id in to_delete:
            self.delete_session(session_id)
            
        logger.info(f"Cleaned up {len(to_delete)} old sessions")


session_manager = SessionManager()
