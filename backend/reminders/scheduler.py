"""Background scheduler for reminder notifications"""
import asyncio
import aiosqlite
from datetime import datetime
import logging

logger = logging.getLogger('DIBS1.Scheduler')

class ReminderScheduler:
    """Check and send due reminders"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.running = False
    
    async def start(self):
        """Start background scheduler"""
        self.running = True
        logger.info("🔔 Reminder scheduler started - checking every 60s")
        
        while self.running:
            logger.info(f"⏰ Scheduler loop running... ({datetime.now().strftime('%H:%M:%S')})")
            try:
                await self._check_reminders()
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def _check_reminders(self):
        """Check for due reminders"""
        logger.info("🔍 Checking for due reminders...")
        from reminders.models import get_reminder_manager
        
        reminder_mgr = get_reminder_manager()
        due_reminders = await reminder_mgr.get_due_reminders()
        
        for reminder in due_reminders:
            await self._send_notification(reminder)
            await reminder_mgr.mark_notified(reminder['id'])
    
    async def _send_notification(self, reminder: dict):
        """Send reminder notification to chat"""
        try:
            # Insert notification message into chat
            import uuid
            msg_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            notification_text = f"""🔔 **Pengingat!**

📌 {reminder['title']}

⏰ Jadwal: {reminder['due_date']}

{reminder['description'] or ''}
"""
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO chat_messages 
                    (id, session_id, role, content, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    msg_id,
                    reminder['session_id'],
                    'assistant',
                    notification_text,
                    now
                ))
                await db.commit()
            
            logger.info(f"📨 Notification sent: {reminder['title']}")
            
        except Exception as e:
            logger.error(f"Send notification error: {e}")
    
    def stop(self):
        """Stop scheduler"""
        self.running = False
        logger.info("🛑 Reminder scheduler stopped")

# Global instance
scheduler = None

def get_scheduler() -> ReminderScheduler:
    global scheduler
    if scheduler is None:
        scheduler = ReminderScheduler('/home/dibs/dibs1/dibs1.db')
    return scheduler
