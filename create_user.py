#!/usr/bin/env python3
"""
Buat user baru untuk testing
"""
import aiosqlite
import asyncio
import uuid
from datetime import datetime
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_user():
    email = "test@dibs.com"
    password = "password123"
    display_name = "Test User"
    
    db_path = "data/dibs.db"
    user_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    # Hash password
    password_hash = pwd_context.hash(password)
    
    async with aiosqlite.connect(db_path) as db:
        # Cek apakah user sudah ada
        cursor = await db.execute("SELECT id FROM users WHERE email = ?", (email,))
        existing = await cursor.fetchone()
        
        if existing:
            print(f"⚠️ User {email} sudah ada")
            return
        
        # Insert user baru
        await db.execute("""
            INSERT INTO users (id, email, password_hash, display_name, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, email, password_hash, display_name, now, now))
        
        await db.commit()
        print(f"✅ User created: {email} / {password}")
        print(f"   ID: {user_id}")

if __name__ == "__main__":
    asyncio.run(create_user())
