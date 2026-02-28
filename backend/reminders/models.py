"""Reminder Models & Database"""
import aiosqlite
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger('DIBS1.Reminders')

class ReminderManager:
    """Manage user reminders and notifications"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    async def initialize(self):
        """Create reminders table"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    session_id TEXT,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT NOT NULL,
                    recurrence TEXT,
                    status TEXT DEFAULT 'pending',
                    related_table TEXT,
                    related_id TEXT,
                    created_at TEXT NOT NULL,
                    notified_at TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_reminders_user_due 
                ON reminders(user_id, due_date, status)
            """)
            
            await db.commit()
            logger.info("✅ Reminders table initialized")
    
    async def create_reminder(
        self,
        user_id: str,
        session_id: str,
        title: str,
        due_date: datetime,
        description: str = None,
        recurrence: str = None,
        related_table: str = None,
        related_id: str = None
    ) -> str:
        """Create new reminder"""
        import uuid
        
        reminder_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO reminders 
                (id, user_id, session_id, title, description, due_date, 
                 recurrence, status, related_table, related_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                reminder_id, user_id, session_id, title, description,
                due_date.isoformat(), recurrence, 'pending',
                related_table, related_id, now
            ))
            await db.commit()
        
        logger.info(f"✅ Reminder created: {title} for {due_date}")
        return reminder_id
    
    async def get_due_reminders(self, user_id: str = None) -> List[Dict]:
        """Get reminders that are due now"""
        now = datetime.now().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if user_id:
                query = """
                    SELECT * FROM reminders 
                    WHERE user_id = ? AND status = 'pending' 
                    AND due_date <= ?
                    ORDER BY due_date ASC
                """
                cursor = await db.execute(query, (user_id, now))
            else:
                query = """
                    SELECT * FROM reminders 
                    WHERE status = 'pending' AND due_date <= ?
                    ORDER BY due_date ASC
                """
                cursor = await db.execute(query, (now,))
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def mark_notified(self, reminder_id: str):
        """Mark reminder as notified"""
        now = datetime.now().isoformat()
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE reminders 
                SET status = 'notified', notified_at = ?
                WHERE id = ?
            """, (now, reminder_id))
            await db.commit()
    
    async def get_user_reminders(
        self, 
        user_id: str, 
        status: str = None,
        limit: int = 20
    ) -> List[Dict]:
        """Get user's reminders"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            
            if status:
                query = """
                    SELECT * FROM reminders 
                    WHERE user_id = ? AND status = ?
                    ORDER BY due_date ASC LIMIT ?
                """
                cursor = await db.execute(query, (user_id, status, limit))
            else:
                query = """
                    SELECT * FROM reminders 
                    WHERE user_id = ?
                    ORDER BY due_date ASC LIMIT ?
                """
                cursor = await db.execute(query, (user_id, limit))
            
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

# Singleton
reminder_manager = None

def get_reminder_manager() -> ReminderManager:
    global reminder_manager
    if reminder_manager is None:
        reminder_manager = ReminderManager('/home/dibs/dibs1/dibs1.db')
    return reminder_manager
