import aiosqlite
import asyncio
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def fix():
    email = "admin@dibs.com"
    new_password = "Dibs123"
    
    async with aiosqlite.connect("data/dibs.db") as db:
        # Hash password baru
        password_hash = pwd_context.hash(new_password)
        
        # Update user
        await db.execute(
            "UPDATE users SET password_hash = ? WHERE email = ?",
            (password_hash, email)
        )
        await db.commit()
        
        # Cek hasil
        cursor = await db.execute("SELECT email, password_hash FROM users WHERE email = ?", (email,))
        user = await cursor.fetchone()
        
        if user:
            print(f"✅ Password untuk {user[0]} berhasil direset")
            print(f"🔐 Password baru: {new_password}")
        else:
            print(f"❌ User {email} tidak ditemukan")

asyncio.run(fix())
