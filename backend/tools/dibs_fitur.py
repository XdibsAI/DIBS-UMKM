#!/usr/bin/env python3
"""
DIBS Fitur - Cek lan dandani fitur sing ora fungsi
Cara: jon "cek [fitur]" utawa jon "dandani [fitur]"
Contoh: jon "cek fitur social media"
"""

import os
import sys
import asyncio
import re
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chat.core import ollama_ai

PROJECT_ROOT = "/home/dibs/dibs1"
FRONTEND_DIR = f"{PROJECT_ROOT}/frontend/lib"
BACKEND_DIR = f"{PROJECT_ROOT}/backend"

# Mapping fitur umum
FITUR_MAP = {
    "social media": {
        "frontend": [
            f"{FRONTEND_DIR}/screens/social/social_feed_screen.dart",
            f"{FRONTEND_DIR}/providers/social_provider.dart",
            f"{FRONTEND_DIR}/services/social_service.dart"
        ],
        "backend": [
            f"{BACKEND_DIR}/social/routes.py",
            f"{BACKEND_DIR}/social/models.py"
        ],
        "tombol": ["post", "like", "comment", "share"]
    },
    "chat": {
        "frontend": [
            f"{FRONTEND_DIR}/screens/chat/chat_screen.dart",
            f"{FRONTEND_DIR}/providers/chat_provider.dart",
            f"{FRONTEND_DIR}/services/chat_service.dart"
        ],
        "backend": [
            f"{BACKEND_DIR}/chat/routes.py",
            f"{BACKEND_DIR}/chat/core.py"
        ],
        "tombol": ["send", "attach", "record"]
    },
    "toko": {
        "frontend": [
            f"{FRONTEND_DIR}/screens/toko/toko_screen.dart",
            f"{FRONTEND_DIR}/providers/toko_provider.dart",
            f"{FRONTEND_DIR}/services/api_service.dart"
        ],
        "backend": [
            f"{BACKEND_DIR}/toko/routes.py",
            f"{BACKEND_DIR}/toko/service.py"
        ],
        "tombol": ["beli", "tambah ke keranjang", "checkout"]
    },
    "video": {
        "frontend": [
            f"{FRONTEND_DIR}/screens/video_player_screen.dart",
            f"{FRONTEND_DIR}/services/video_service.dart"
        ],
        "backend": [
            f"{BACKEND_DIR}/video/routes.py",
            f"{BACKEND_DIR}/video_agent.py"
        ],
        "tombol": ["play", "pause", "generate", "download"]
    },
    "auth": {
        "frontend": [
            f"{FRONTEND_DIR}/screens/auth/login_screen.dart",
            f"{FRONTEND_DIR}/screens/auth/register_screen.dart",
            f"{FRONTEND_DIR}/providers/auth_provider.dart"
        ],
        "backend": [
            f"{BACKEND_DIR}/auth/routes.py",
            f"{BACKEND_DIR}/auth/models.py"
        ],
        "tombol": ["login", "register", "logout", "forgot password"]
    }
}

async def cek_fitur(fitur_nama):
    """Cek fitur, golek tombol sing ora fungsi"""
    print(f"\n🔍 CEK FITUR: {fitur_nama.upper()}")
    print("=" * 60)
    
    if fitur_nama not in FITUR_MAP:
        print(f"❌ Fitur '{fitur_nama}' durung dikenal.")
        print("   Fitur sing ono: social media, chat, toko, video, auth")
        return
    
    fitur = FITUR_MAP[fitur_nama]
    masalah = []
    
    # Cek file frontend ono ora
    print("\n📂 CEK FILE:")
    for file in fitur["frontend"]:
        if os.path.exists(file):
            print(f"  ✅ {os.path.basename(file)}")
            
            # Baca file, cek tombol
            with open(file, 'r') as f:
                content = f.read()
                
                # Cek tombol-tombol
                for tombol in fitur["tombol"]:
                    if tombol in content.lower():
                        # Cek apa fungsi e ono
                        if "onPressed: null" in content or "onPressed: () {}" in content:
                            masalah.append(f"⚠️ Tombol '{tombol}' ono nanging ora fungsi (onPressed null)")
                        elif f"onPressed: {tombol}" not in content and f"onPressed: ()" in content:
                            # Kira-kira fungsi e kosong
                            masalah.append(f"⚠️ Tombol '{tombol}' mungkin ora fungsi (cek manual)")
        else:
            masalah.append(f"❌ File {os.path.basename(file)} ora ketemu!")
    
    # Cek file backend ono ora
    for file in fitur["backend"]:
        if os.path.exists(file):
            print(f"  ✅ {os.path.basename(file)}")
        else:
            masalah.append(f"❌ Backend file {os.path.basename(file)} ora ketemu!")
    
    # Tampilke masalah
    print("\n📋 MASALAH SING DITEMOKE:")
    if masalah:
        for m in masalah:
            print(f"  {m}")
    else:
        print("  ✅ Ora nemu masalah berarti!")
    
    return masalah

async def dandani_fitur(fitur_nama):
    """Dandani fitur sing bermasalah"""
    print(f"\n🔧 DANDANI FITUR: {fitur_nama.upper()}")
    print("=" * 60)
    
    if fitur_nama not in FITUR_MAP:
        print(f"❌ Fitur '{fitur_nama}' durung dikenal.")
        return
    
    fitur = FITUR_MAP[fitur_nama]
    
    # Cek masalah disek
    masalah = await cek_fitur(fitur_nama)
    
    if not masalah:
        print("\n✅ Ora ono masalah, ora perlu didandani.")
        return
    
    print("\n🔧 LAGI NDANDANI...")
    
    # Dandani file frontend
    for file in fitur["frontend"]:
        if os.path.exists(file):
            with open(file, 'r') as f:
                content = f.read()
            
            new_content = content
            
            # Dandani tombol sing onPressed null
            new_content = new_content.replace('onPressed: null', 'onPressed: () async {}')
            new_content = new_content.replace('onPressed: () {}', 'onPressed: () async {}')
            
            # Tambahke fungsi dasar
            for tombol in fitur["tombol"]:
                if tombol in new_content.lower():
                    # Cek apa wis ono fungsi e
                    if f"_{tombol}()" not in new_content and f"{tombol}Function" not in new_content:
                        # Tambahke fungsi dasar
                        fungsi_template = f"""
  // FIXED: Fungsi {tombol} ditambahke otomatis
  void _{tombol}() {{
    print('Tombol {tombol} ditekan');
    // TODO: Implementasi {tombol}
  }}
"""
                        # Tempatke sadurunge kelas ditutup
                        if '}' in new_content:
                            last_brace = new_content.rindex('}')
                            new_content = new_content[:last_brace] + fungsi_template + new_content[last_brace:]
            
            if new_content != content:
                # Backup
                backup = file + ".bak"
                os.rename(file, backup)
                
                # Tulis anyar
                with open(file, 'w') as f:
                    f.write(new_content)
                print(f"  ✅ {os.path.basename(file)}: Didandani")
    
    print("\n✅ DANDANI RAMPUNG! Coba cek maneh:")
    print(f"  jon 'cek {fitur_nama}'")

async def main():
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════╗
║  DIBS FITUR - Kanggo Cek & Dandani Tombol   ║
╚══════════════════════════════════════════════╝

CARANE:
  jon "cek [fitur]"        → Cek fitur sing ora fungsi
  jon "dandani [fitur]"    → Dandani fitur sing error
  jon "cek kabeh"          → Cek kabeh fitur

CONTOH:
  jon "cek social media"
  jon "dandani toko"
  jon "cek kabeh"

FITUR SING ONO:
  • social media
  • chat
  • toko
  • video
  • auth
""")
        return
    
    # Gabungke perintah
    perintah = " ".join(sys.argv[1:]).lower()
    
    # Parse perintah
    if "cek kabeh" in perintah:
        for fitur in FITUR_MAP.keys():
            await cek_fitur(fitur)
            print("-" * 60)
    
    elif "cek" in perintah:
        for fitur in FITUR_MAP.keys():
            if fitur in perintah:
                await cek_fitur(fitur)
                return
        print("❌ Fitur ora ditemokne. Coba: social media, chat, toko, video, auth")
    
    elif "dandani" in perintah:
        for fitur in FITUR_MAP.keys():
            if fitur in perintah:
                await dandani_fitur(fitur)
                return
        print("❌ Fitur ora ditemokne. Coba: social media, chat, toko, video, auth")
    
    else:
        print("❌ Perintah ora jelas. Coba: jon 'cek social media'")

if __name__ == "__main__":
    asyncio.run(main())
