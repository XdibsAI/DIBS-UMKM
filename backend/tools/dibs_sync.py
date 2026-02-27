#!/usr/bin/env python3
"""
DIBS Sync - Mbenahi sing durung sinkron lan fungsi sing durung nyambung
Cara: sync
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chat.core import ollama_ai

PROJECT_ROOT = "/home/dibs/dibs1"

async def cek_sinkron():
    """Cek file-file sing kudune sinkron"""
    print("\n🔍 CEK SINKRONISASI...")
    
    masalah = []
    
    # Cek backend-frontend connection
    api_service = f"{PROJECT_ROOT}/frontend/lib/services/api_service.dart"
    if os.path.exists(api_service):
        with open(api_service, 'r') as f:
            content = f.read()
            if "localhost" in content or "127.0.0.1" in content:
                masalah.append("⚠️ API Service: Pake localhost, kudune pake IP server")
    
    # Cek database path
    db_manager = f"{PROJECT_ROOT}/backend/database/manager.py"
    if os.path.exists(db_manager):
        with open(db_manager, 'r') as f:
            content = f.read()
            if "dibs1.db" not in content:
                masalah.append("⚠️ Database: Path database ra jelas")
    
    # Cek environment
    env_file = f"{PROJECT_ROOT}/backend/.env"
    if not os.path.exists(env_file):
        masalah.append("⚠️ Environment: .env file ora ono")
    
    if masalah:
        print("\n".join(masalah))
    else:
        print("✅ Kabeh sinkron!")
    
    return masalah

async def cek_nyambung():
    """Cek fungsi-fungsi sing kudune nyambung"""
    print("\n🔍 CEK KONEKSI FUNGSI...")
    
    masalah = []
    
    # Cek Nvidia API
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            r = await client.get("https://api.nvcf.nvidia.com/health", timeout=5)
            if r.status_code != 200:
                masalah.append("⚠️ Nvidia API: Ora konek")
    except:
        masalah.append("⚠️ Nvidia API: Gagal konek")
    
    # Cek Ollama
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get("http://localhost:11434/api/tags", timeout=2)
            if r.status_code != 200:
                masalah.append("⚠️ Ollama: Ora mlayu")
    except:
        masalah.append("⚠️ Ollama: Gagal konek")
    
    # Cek Supabase (Yen ono)
    env_file = f"{PROJECT_ROOT}/backend/.env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            if "SUPABASE" in f.read():
                masalah.append("⚠️ Supabase: Perlu cek manual")
    
    if masalah:
        print("\n".join(masalah))
    else:
        print("✅ Kabeh fungsi nyambung!")
    
    return masalah

async def betulin_semua():
    """Betulin kabeh sing durung sinkron"""
    print("\n🔧 MBENAHI KABEH...")
    
    # 1. Betulin API Service
    api_service = f"{PROJECT_ROOT}/frontend/lib/services/api_service.dart"
    if os.path.exists(api_service):
        with open(api_service, 'r') as f:
            content = f.read()
        
        # Ganti localhost karo IP server
        new_content = content.replace("localhost", "94.100.26.128")
        new_content = new_content.replace("127.0.0.1", "94.100.26.128")
        
        with open(api_service, 'w') as f:
            f.write(new_content)
        print("✅ API Service: Localhost diganti IP server")
    
    # 2. Gawe .env file yen durung ono
    env_file = f"{PROJECT_ROOT}/backend/.env"
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("""# DIBS Environment
NVIDIA_API_KEY=your_nvidia_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
""")
        print("✅ Environment: .env file digawe")
    
    # 3. Cek Ollama
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            r = await client.get("http://localhost:11434/api/tags")
            if r.status_code == 200:
                models = r.json().get("models", [])
                if not models:
                    print("⚠️ Ollama: Ora ono model, jalanne: ollama pull llama3.2")
    except:
        print("⚠️ Ollama: Ora mlayu, jalanne: ollama serve")
    
    print("\n✅ MBENAHI RAMPUNG!")

async def main():
    if len(sys.argv) < 2:
        print("""
╔════════════════════════════════════╗
║      DIBS SYNC - MBENAHI SING      ║
║      DURUNG SINKRON / NYAMBUNG     ║
╚════════════════════════════════════╝

CARANE:
  sync sinkron    → Cek sing durung sinkron
  sync nyambung   → Cek fungsi sing durung nyambung
  sync all        → Cek kabeh
  sync betulin    → Betulin otomatis

CONTOH:
  sync all        → Cek kabeh masalah
  sync betulin    → Betulin sing iso dibetulin
""")
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == "sinkron":
        await cek_sinkron()
    elif cmd == "nyambung":
        await cek_nyambung()
    elif cmd == "all":
        await cek_sinkron()
        await cek_nyambung()
    elif cmd == "betulin":
        await betulin_semua()
    else:
        print(f"❌ Perintah '{cmd}' ora dikenal")

if __name__ == "__main__":
    asyncio.run(main())
