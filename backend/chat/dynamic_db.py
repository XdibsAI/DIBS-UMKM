"""Dynamic Database Manager - Auto-create tables"""
import aiosqlite
import re
import logging
from typing import Dict, List, Optional
from datetime import datetime

logger = logging.getLogger('DIBS1.DynamicDB')

class DynamicDBManager:
    """Manage dynamic user-created tables"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    async def ensure_table_exists(self, table_name: str, sample_data: Dict) -> bool:
        """Create table if doesn't exist, infer schema from data"""
        try:
            # Sanitize table name
            safe_table = self._sanitize_table_name(table_name)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Check if table exists
                cursor = await db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (safe_table,)
                )
                exists = await cursor.fetchone()
                
                if not exists:
                    # Create table with flexible schema
                    columns = self._infer_columns(sample_data)
                    
                    create_sql = f"""
                        CREATE TABLE {safe_table} (
                            id TEXT PRIMARY KEY,
                            user_id TEXT NOT NULL,
                            {columns},
                            created_at TEXT NOT NULL,
                            updated_at TEXT NOT NULL
                        )
                    """
                    
                    await db.execute(create_sql)
                    await db.commit()
                    
                    logger.info(f"✅ Created table: {safe_table}")
                    return True
                
                return True
                
        except Exception as e:
            logger.error(f"❌ Table creation error: {e}")
            return False
    
    async def insert(self, table_name: str, user_id: str, data: Dict) -> Optional[str]:
        """Insert data into dynamic table"""
        try:
            safe_table = self._sanitize_table_name(table_name)
            
            # Ensure table exists
            await self.ensure_table_exists(safe_table, data)
            
            # Generate ID
            import uuid
            record_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            # Build INSERT query dynamically
            columns = ['id', 'user_id'] + list(data.keys()) + ['created_at', 'updated_at']
            placeholders = ','.join(['?' for _ in columns])
            values = [record_id, user_id] + list(data.values()) + [now, now]
            
            insert_sql = f"""
                INSERT INTO {safe_table} ({','.join(columns)})
                VALUES ({placeholders})
            """
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(insert_sql, values)
                await db.commit()
            
            logger.info(f"✅ Inserted into {safe_table}: {record_id}")
            return record_id
            
        except Exception as e:
            logger.error(f"❌ Insert error: {e}")
            return None
    
    async def query(self, table_name: str, user_id: str, limit: int = 10) -> List[Dict]:
        """Query data from dynamic table"""
        try:
            safe_table = self._sanitize_table_name(table_name)
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    f"SELECT * FROM {safe_table} WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                    (user_id, limit)
                )
                rows = await cursor.fetchall()
                
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"❌ Query error: {e}")
            return []
    
    async def delete(self, table_name: str, user_id: str, record_id: str) -> bool:
        """Delete record from dynamic table"""
        try:
            safe_table = self._sanitize_table_name(table_name)
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    f"DELETE FROM {safe_table} WHERE id = ? AND user_id = ?",
                    (record_id, user_id)
                )
                await db.commit()
            
            logger.info(f"🗑️ Deleted from {safe_table}: {record_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Delete error: {e}")
            return False
    
    def _sanitize_table_name(self, name: str) -> str:
        """Sanitize table name for SQL safety"""
        # Remove special chars, keep alphanumeric and underscore
        safe = re.sub(r'[^a-zA-Z0-9_]', '', name)
        
        # Ensure starts with letter
        if not safe[0].isalpha():
            safe = 'tbl_' + safe
        
        # Add prefix for user tables
        return f"user_{safe}"
    
    def _infer_columns(self, data: Dict) -> str:
        """Infer column definitions from sample data"""
        columns = []
        
        for key, value in data.items():
            safe_key = re.sub(r'[^a-zA-Z0-9_]', '', key)
            
            # Infer type from value
            if isinstance(value, int):
                col_type = 'INTEGER'
            elif isinstance(value, float):
                col_type = 'REAL'
            else:
                col_type = 'TEXT'
            
            columns.append(f"{safe_key} {col_type}")
        
        return ',\n            '.join(columns)

# Singleton
dynamic_db = None

def get_dynamic_db() -> DynamicDBManager:
    """Get or create DynamicDBManager instance"""
    global dynamic_db
    if dynamic_db is None:
        dynamic_db = DynamicDBManager('/home/dibs/dibs1/dibs1.db')
    return dynamic_db
