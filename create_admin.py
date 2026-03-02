import aiosqlite
import asyncio
import uuid
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create():
    email = "admin@dibs.com"
    password = "Dibs123"
    display_name = "Admin"
    
    async with aiosqlite.connect("data/dibs.db") as db:
        # Cek dulu tabel users
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = await cursor.fetchone()
        
        if not table_exists:
            print("📦 Membuat tabel users...")
            await db.execute("""
                CREATE TABLE users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    display_name TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
        
        # Hash password
        password_hash = pwd_context.hash(password)
        user_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Insert user
        await db.execute("""
            INSERT INTO users (id, email, password_hash, display_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, email, password_hash, display_name, now, now))
        
        await db.commit()
        print(f"✅ User {email} / {password} created")
        print(f"📧 Email: {email}")
        print(f"🔑 Password: {password}")
        print(f"🆔 ID: {user_id}")

asyncio.run(create())
