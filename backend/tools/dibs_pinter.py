#!/usr/bin/env python3
"""
DIBS Pinter - Ngerti kabeh struktur project
Cara: jon "cek project screen"
      jon "dandani tombol like nang social media"
      jon "apa wae"
"""

import os
import sys
import asyncio
import json
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chat.core import ollama_ai

PROJECT_ROOT = "/home/dibs/dibs1"

async def main():
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════╗
║  DIBS PINTER - Ngerti Kabeh Struktur Project ║
╚══════════════════════════════════════════════╝

CARANE:
  jon "perintah mu"

CONTOH:
  jon "cek project screen"
  jon "dandani tombol like nang social media"
  jon "apa salah e fitur toko"
  jon "betulin video player"
""")
        return
    
    # Gabungke kabeh perintah
    perintah = " ".join(sys.argv[1:])
    
    print(f"\n🔍 DIBS: {perintah}")
    print("=" * 60)
    
    # KIRIM STRUKTUR PROJECT KE AI
    struktur = {
        "project_root": PROJECT_ROOT,
        "frontend": {
            "lib": f"{PROJECT_ROOT}/frontend/lib",
            "screens": [
                "auth/login_screen.dart",
                "auth/register_screen.dart",
                "chat/chat_screen.dart",
                "chat/chat_list_screen.dart",
                "home/home_screen.dart",
                "home/dashboard_screen.dart",
                "projects/projects_screen.dart",
                "projects/project_detail_screen.dart",
                "projects/create_project_screen.dart",
                "social/social_feed_screen.dart",
                "toko/toko_screen.dart",
                "toko/product_detail_screen.dart",
                "toko/cart_screen.dart",
                "toko/checkout_screen.dart",
                "settings/settings_screen.dart",
                "settings/profile_screen.dart",
                "video_player_screen.dart"
            ],
            "providers": [
                "auth_provider.dart",
                "chat_provider.dart",
                "project_provider.dart",
                "toko_provider.dart",
                "settings_provider.dart",
                "social_provider.dart"
            ],
            "services": [
                "api_service.dart",
                "chat_service.dart",
                "video_service.dart",
                "social_service.dart"
            ],
            "models": [
                "user.dart",
                "chat.dart",
                "project.dart",
                "video_project.dart",
                "knowledge.dart"
            ]
        },
        "backend": {
            "dir": f"{PROJECT_ROOT}/backend",
            "modules": [
                "auth/routes.py",
                "auth/models.py",
                "chat/core.py",
                "chat/routes.py",
                "database/manager.py",
                "knowledge/routes.py",
                "toko/routes.py",
                "toko/service.py",
                "video/routes.py",
                "video_agent.py",
                "video_generator.py",
                "nvidia_routes.py",
                "language_intelligence.py"
            ]
        },
        "ai_video": {
            "dir": f"{PROJECT_ROOT}/ai-video-generator",
            "apps": [
                "apps/effects_ui.py",
                "apps/video_generator_effects.py"
            ],
            "utils": [
                "utils/tts_handler.py",
                "utils/story_generator.py",
                "utils/video_editor.py",
                "utils/text_effects.py"
            ]
        }
    }
    
    # Gawe prompt
    prompt = f"""
KOWE iku DIBS, asisten pinter sing ngerti kabeh struktur project iki.

STRUKTUR PROJECT:
{json.dumps(struktur, indent=2)}

PERINTAH USER:
{perintah}

TUGAS:
1. Pahami perintah user
2. Temokne file/file sing relevan karo perintah
3. Analisa masalah (yen perintah "cek")
4. Kasi solusi / dandani (yen perintah "dandani")

TULISKAN:
- File sing dicek
- Masalah sing ditemokne
- Saran perbaikan
- Langkah konkret

Gawe bahasa campuran Indonesia-Jawa santai.
"""
    
    try:
        # Panggil AI
        hasil = await ollama_ai.generate(prompt)
        print("\n📋 HASIL:")
        print(hasil)
        print("=" * 60)
        
        # Simpen log
        log_dir = f"{PROJECT_ROOT}/logs"
        os.makedirs(log_dir, exist_ok=True)
        with open(f"{log_dir}/dibs_{perintah[:30]}.log", 'w') as f:
            f.write(f"Perintah: {perintah}\n")
            f.write(f"Waktu: {__import__('datetime').datetime.now()}\n")
            f.write("="*60 + "\n")
            f.write(hasil)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
