"""Database Manager with proper connection handling"""
import aiosqlite
import logging
import asyncio
from typing import Optional, Any, List, Dict

logger = logging.getLogger('DIBS1')

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()

    async def connect(self):
        """Connect to database with proper event loop handling"""
        async with self._lock:
            if self.db is None:
                try:
                    self.db = await aiosqlite.connect(self.db_path)
                    self.db.row_factory = aiosqlite.Row
                    logger.info(f"✅ Database connected: {self.db_path}")
                except Exception as e:
                    logger.error(f"❌ Database connection error: {e}")
                    raise

    async def close(self):
        """Close database connection safely"""
        async with self._lock:
            if self.db:
                try:
                    await self.db.close()
                    logger.info("👋 Database closed")
                except Exception as e:
                    logger.error(f"Error closing database: {e}")
                finally:
                    self.db = None

    async def execute(self, query: str, params: tuple = ()):
        """Execute query with proper connection handling"""
        await self.connect()
        try:
            async with self.db.execute(query, params) as cursor:
                await self.db.commit()
                return cursor
        except Exception as e:
            logger.error(f"Execute error: {e}")
            raise

    async def fetch_one(self, query: str, params: tuple = ()):
        """Fetch one row"""
        await self.connect()
        try:
            async with self.db.execute(query, params) as cursor:
                return await cursor.fetchone()
        except Exception as e:
            logger.error(f"Fetch one error: {e}")
            raise

    async def fetch_all(self, query: str, params: tuple = ()):
        """Fetch all rows"""
        await self.connect()
        try:
            async with self.db.execute(query, params) as cursor:
                return await cursor.fetchall()
        except Exception as e:
            logger.error(f"Fetch all error: {e}")
            raise

    async def execute_many(self, query: str, params_list: List[tuple]):
        """Execute many queries"""
        await self.connect()
        try:
            async with self.db.executemany(query, params_list) as cursor:
                await self.db.commit()
                return cursor
        except Exception as e:
            logger.error(f"Execute many error: {e}")
            raise
