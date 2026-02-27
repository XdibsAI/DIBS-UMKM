"""Database Manager"""
import aiosqlite
import logging

logger = logging.getLogger('DIBS1')

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db = None
    
    async def connect(self):
        self.db = await aiosqlite.connect(self.db_path)
        self.db.row_factory = aiosqlite.Row
        logger.info(f"✅ Database connected: {self.db_path}")
    
    async def close(self):
        if self.db:
            await self.db.close()
    
    async def execute(self, query: str, params: tuple = ()):
        async with self.db.execute(query, params) as cursor:
            await self.db.commit()
            return cursor
    
    async def fetch_one(self, query: str, params: tuple = ()):
        async with self.db.execute(query, params) as cursor:
            return await cursor.fetchone()
    
    async def fetch_all(self, query: str, params: tuple = ()):
        async with self.db.execute(query, params) as cursor:
            return await cursor.fetchall()

