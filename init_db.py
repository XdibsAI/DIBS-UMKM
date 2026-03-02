#!/usr/bin/env python3
"""
Inisialisasi database dengan tabel yang diperlukan
"""
import aiosqlite
import asyncio
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_database():
    db_path = Path.home() / "dibs1" / "data" / "dibs.db"
    
    # Buat folder data jika belum ada
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"📁 Inisialisasi database: {db_path}")
    
    async with aiosqlite.connect(db_path) as db:
        # Buat tabel users
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                display_name TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # Buat tabel chat_sessions
        await db.execute('''
            CREATE TABLE IF NOT EXISTS chat_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Buat tabel chat_messages
        await db.execute('''
            CREATE TABLE IF NOT EXISTS chat_messages (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
            )
        ''')
        
        # Buat tabel knowledge
        await db.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        # Buat tabel video_projects
        await db.execute('''
            CREATE TABLE IF NOT EXISTS video_projects (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                niche TEXT NOT NULL,
                duration INTEGER DEFAULT 30,
                style TEXT DEFAULT 'engaging',
                language TEXT DEFAULT 'id',
                script TEXT,
                video_path TEXT,
                status TEXT DEFAULT 'pending',
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        
        await db.commit()
        
        # Cek tabel yang sudah dibuat
        async with db.execute("SELECT name FROM sqlite_master WHERE type='table'") as cursor:
            tables = await cursor.fetchall()
            logger.info("✅ Tabel yang tersedia:")
            for table in tables:
                logger.info(f"   - {table[0]}")
    
    logger.info("✅ Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_database())
