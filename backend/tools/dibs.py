#!/usr/bin/env python3
"""
DIBS - Developer Intelligent Buddy System
Siji tool kanggo kabeh kabutuhan coding-mu
Cara nganggo: dibs "perintah mu nang kene"
"""

import os
import sys
import asyncio
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

# Setup path biar bisa import module backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chat.core import ollama_ai

# ==================== KONFIGURASI ====================
PROJECT_ROOT = os.path.expanduser("~/dibs1")
FRONTEND_DIR = f"{PROJECT_ROOT}/frontend"
BACKEND_DIR = f"{PROJECT_ROOT}/backend"
LIB_DIR = f"{FRONTEND_DIR}/lib"
AI_VIDEO_DIR = f"{PROJECT_ROOT}/ai-video-generator"
MCP_SERVER_DIR = f"{PROJECT_ROOT}/mcp-server"
VIDEO_OUTPUTS_DIR = f"{PROJECT_ROOT}/video_outputs"
DOWNLOADS_DIR = f"{PROJECT_ROOT}/downloads"

# Mapping file sing sering diakses - UPDATE LENGKAP!
FILE_MAP = {
    # ===== FRONTEND / FLUTTER FILES =====
    "main": f"{LIB_DIR}/main.dart",
    "theme": f"{LIB_DIR}/core/theme.dart",
    "constants": f"{LIB_DIR}/core/constants.dart",
    "login": f"{LIB_DIR}/screens/auth/login_screen.dart",
    "register": f"{LIB_DIR}/screens/auth/register_screen.dart",
    "auth": f"{LIB_DIR}/screens/auth/login_screen.dart",
    "chat": f"{LIB_DIR}/screens/chat/chat_screen.dart",
    "chat_screen": f"{LIB_DIR}/screens/chat/chat_screen.dart",
    "chat_list": f"{LIB_DIR}/screens/chat/chat_list_screen.dart",
    "home": f"{LIB_DIR}/screens/home/home_screen.dart",
    "dashboard": f"{LIB_DIR}/screens/home/dashboard_screen.dart",
    "projects": f"{LIB_DIR}/screens/projects/projects_screen.dart",
    "project_detail": f"{LIB_DIR}/screens/projects/project_detail_screen.dart",
    "project_create": f"{LIB_DIR}/screens/projects/create_project_screen.dart",
    "toko": f"{LIB_DIR}/screens/toko/toko_screen.dart",
    "product": f"{LIB_DIR}/screens/toko/product_detail_screen.dart",
    "cart": f"{LIB_DIR}/screens/toko/cart_screen.dart",
    "checkout": f"{LIB_DIR}/screens/toko/checkout_screen.dart",
    "settings": f"{LIB_DIR}/screens/settings/settings_screen.dart",
    "profile": f"{LIB_DIR}/screens/settings/profile_screen.dart",
    "video_player": f"{LIB_DIR}/screens/video_player_screen.dart",
    "social": f"{LIB_DIR}/screens/social/social_feed_screen.dart",
    "feed": f"{LIB_DIR}/screens/social/social_feed_screen.dart",
    "user_model": f"{LIB_DIR}/models/user.dart",
    "chat_model": f"{LIB_DIR}/models/chat.dart",
    "project_model": f"{LIB_DIR}/models/project.dart",
    "video_model": f"{LIB_DIR}/models/video_project.dart",
    "knowledge_model": f"{LIB_DIR}/models/knowledge.dart",
    "auth_provider": f"{LIB_DIR}/providers/auth_provider.dart",
    "chat_provider": f"{LIB_DIR}/providers/chat_provider.dart",
    "project_provider": f"{LIB_DIR}/providers/project_provider.dart",
    "toko_provider": f"{LIB_DIR}/providers/toko_provider.dart",
    "settings_provider": f"{LIB_DIR}/providers/settings_provider.dart",
    "social_provider": f"{LIB_DIR}/providers/social_provider.dart",
    "api_service": f"{LIB_DIR}/services/api_service.dart",
    "chat_service": f"{LIB_DIR}/services/chat_service.dart",
    "video_service": f"{LIB_DIR}/services/video_service.dart",
    "social_service": f"{LIB_DIR}/services/social_service.dart",
    "pubspec": f"{FRONTEND_DIR}/pubspec.yaml",
    "pubspec.yaml": f"{FRONTEND_DIR}/pubspec.yaml",
    
    # ===== BACKEND FILES =====
    "backend_main": f"{BACKEND_DIR}/main.py",
    "backend_main.py": f"{BACKEND_DIR}/main.py",
    "core": f"{BACKEND_DIR}/chat/core.py",
    "chat_core": f"{BACKEND_DIR}/chat/core.py",
    "chat_routes": f"{BACKEND_DIR}/chat/routes.py",
    "chat_models": f"{BACKEND_DIR}/chat/models.py",
    "auth_routes": f"{BACKEND_DIR}/auth/routes.py",
    "auth_models": f"{BACKEND_DIR}/auth/models.py",
    "auth_utils": f"{BACKEND_DIR}/auth/utils.py",
    "db": f"{BACKEND_DIR}/database/manager.py",
    "database": f"{BACKEND_DIR}/database/manager.py",
    "db_manager": f"{BACKEND_DIR}/database/manager.py",
    "toko_routes": f"{BACKEND_DIR}/toko/routes.py",
    "toko_service": f"{BACKEND_DIR}/toko/service.py",
    "toko_models": f"{BACKEND_DIR}/toko/models.py",
    "toko_db": f"{BACKEND_DIR}/toko/database.py",
    "toko_schema": f"{BACKEND_DIR}/toko/schema.sql",
    "knowledge": f"{BACKEND_DIR}/knowledge/routes.py",
    "knowledge_routes": f"{BACKEND_DIR}/knowledge/routes.py",
    "video_routes": f"{BACKEND_DIR}/video/routes.py",
    "video_agent": f"{BACKEND_DIR}/video_agent.py",
    "video_generator": f"{BACKEND_DIR}/video_generator.py",
    "nvidia": f"{BACKEND_DIR}/nvidia_routes.py",
    "nvidia_wrapper": f"{BACKEND_DIR}/nvidia_wrapper.py",
    "language": f"{BACKEND_DIR}/language_intelligence.py",
    "language_intel": f"{BACKEND_DIR}/language_intelligence.py",
    "dibs": __file__,
    "dibs_tool": __file__,
    "auditor": f"{BACKEND_DIR}/tools/auditor.py",
    "config": f"{BACKEND_DIR}/config/settings.py",
    "logging_config": f"{BACKEND_DIR}/config/logging.py",
    
    # ===== AI VIDEO GENERATOR =====
    "ai_video_main": f"{AI_VIDEO_DIR}/main.py",
    "ai_video_run": f"{AI_VIDEO_DIR}/run.py",
    "video_app": f"{AI_VIDEO_DIR}/app/main.py",
    "video_apps": f"{AI_VIDEO_DIR}/apps/main.py",
    "effects_ui": f"{AI_VIDEO_DIR}/apps/effects_ui.py",
    "video_effects": f"{AI_VIDEO_DIR}/apps/video_generator_effects.py",
    "video_utils": f"{AI_VIDEO_DIR}/utils/video_editor.py",
    "tts_handler": f"{AI_VIDEO_DIR}/utils/tts_handler.py",
    "speech_to_text": f"{AI_VIDEO_DIR}/utils/speech_to_text.py",
    "story_gen": f"{AI_VIDEO_DIR}/utils/story_generator.py",
    "text_effects": f"{AI_VIDEO_DIR}/utils/text_effects.py",
    "text_processor": f"{AI_VIDEO_DIR}/utils/text_processor.py",
    "content_optimizer": f"{AI_VIDEO_DIR}/utils/content_optimizer.py",
    "cleanup": f"{AI_VIDEO_DIR}/utils/cleanup.py",
    "ffmpeg_checker": f"{AI_VIDEO_DIR}/utils/ffmpeg_checker.py",
    "session_manager": f"{AI_VIDEO_DIR}/utils/session_manager.py",
    "compatibility": f"{AI_VIDEO_DIR}/utils/compatibility.py",
    "video_settings": f"{AI_VIDEO_DIR}/config/settings.py",
    
    # ===== MCP SERVER =====
    "mcp": f"{MCP_SERVER_DIR}/mcp_server_production.py",
    "mcp_server": f"{MCP_SERVER_DIR}/mcp_server_production.py",
    
    # ===== DATABASE FILES =====
    "dibs1.db": f"{PROJECT_ROOT}/dibs1.db",
    "toko.db": f"{BACKEND_DIR}/toko.db",
    
    # ===== DIRECTORY MAPPING =====
    "downloads": DOWNLOADS_DIR,
    "video_outputs": VIDEO_OUTPUTS_DIR,
    "videos": VIDEO_OUTPUTS_DIR,
    "frontend_dir": FRONTEND_DIR,
    "backend_dir": BACKEND_DIR,
    "lib_dir": LIB_DIR,
    "project_root": PROJECT_ROOT,
}

# ==================== UTILITY FUNCTIONS ====================
def find_file(name: str) -> Optional[str]:
    """Nggolek file based on name or path"""
    name = name.strip().lower()
    
    if name in FILE_MAP:
        return FILE_MAP[name]
    
    for key, path in FILE_MAP.items():
        if name in key or key in name:
            return path
    
    if os.path.exists(name):
        return name
    
    full_path = os.path.join(PROJECT_ROOT, name)
    if os.path.exists(full_path):
        return full_path
    
    for root, dirs, files in os.walk(PROJECT_ROOT):
        if 'venv' in root or '__pycache__' in root or '.git' in root:
            continue
        for f in files:
            if f == name or f == name + ".dart" or f == name + ".py" or f == name + ".yaml":
                return os.path.join(root, f)
            if name in f.lower():
                return os.path.join(root, f)
    
    return None

def show_menu():
    """Nampilake menu bantuan"""
    print("""
╔══════════════════════════════════════════════════════════╗
║     🚀 DIBS - Developer Intelligent Buddy System v2.0    ║
╚══════════════════════════════════════════════════════════╝

CARANE NGANGGOKE:
  dibs "perintah mu"           → Mode otomatis (paling gampang)
  dibs --fix <file>            → Dandani file
  dibs --mod <file> "instruksi" → Modifikasi file
  dibs --exec "perintah"       → Jalanake perintah
  dibs --scan                  → Scan kabeh project
  dibs --list                  → Delok file sing kasedia
  dibs --help                  → Bantuan iki

CONTOH:
  dibs "dandani chat screen error"
  dibs "analisa pubspec.yaml"
  dibs "gawe fungsi login anyar di auth_service"
  dibs "run flutter run"
  dibs "cek file main.dart"
  dibs "tambah product model di toko"

FILE SING SIAP (cukup sebut jenenge):
  • Frontend: main, chat, login, home, toko, pubspec, theme
  • Backend: core, db, auth, nvidia, video_agent
  • AI Video: ai_video, effects, tts, story_gen
  • Database: dibs1.db, toko.db
""")

def list_available_files():
    """Nampilake file sing kasedia"""
    print("\n📂 FILE SING KASEDIA:")
    print("="*60)
    
    categories = {
        "FRONTEND": ["main", "chat", "login", "home", "toko", "pubspec", "theme", 
                     "api_service", "auth_provider", "chat_provider"],
        "BACKEND": ["core", "db", "auth_routes", "toko_routes", "nvidia", 
                    "video_agent", "language", "knowledge"],
        "AI VIDEO": ["ai_video_main", "effects_ui", "tts_handler", "story_gen", 
                     "video_editor", "text_effects"],
        "DATABASE": ["dibs1.db", "toko.db"],
        "TOOLS": ["dibs", "auditor"],
    }
    
    for category, files in categories.items():
        print(f"\n{category}:")
        for f in files:
            path = FILE_MAP.get(f, "?")
            if path and os.path.exists(path):
                status = "✅"
            else:
                status = "⚠️"
            print(f"  {status} {f:15} → {os.path.basename(path) if path else '?'}")
    
    print("\n" + "="*60)
    print("Tips: Cukup ketik 'dibs --fix chat' kanggo dandani chat_screen.dart")

# ==================== CORE FUNCTIONS ====================
async def analyze_file(file_path: str, instruction: str = ""):
    """Analisa file lan kasi saran perbaikan"""
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} ora ono!")
        return
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    ext = os.path.splitext(file_path)[1]
    file_type = "Dart" if ext == ".dart" else "Python" if ext == ".py" else "YAML" if ext in [".yaml", ".yml"] else "unknown"
    
    prompt = f"""
    Kowe iku AI Senior Developer. Tugasmu ANALISA kode iki.
    
    FILE: {file_path}
    JENIS: {file_type}
    
    {f'INSTRUKSI TAMBAHAN: {instruction}' if instruction else ''}
    
    KODE:
    {content[:6000]}
    
    TULISKAN:
    1. Apa masalah/kesalahan sing katon?
    2. Saran perbaikan (spesifik)
    3. Bagian sing iso dioptimalake
    4. Best practices sing kurang
    5. Keamanan (security concerns) yen ono
    
    Gawe gaya ngomong kaya Diskusi teknis nang warung kopi, tapi tetep profesional.
    """
    
    try:
        print("🔍 Lagi analisa...")
        result = await ollama_ai.generate(prompt)
        print("\n" + "="*60)
        print("📊 HASIL ANALISA:")
        print("="*60)
        print(result)
        print("="*60)
        
        report_path = f"{PROJECT_ROOT}/analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, 'w') as f:
            f.write(f"Analisa: {file_path}\n")
            f.write("="*60 + "\n")
            f.write(result)
        print(f"\n💾 Laporan disimpen: {report_path}")
        
    except Exception as e:
        print(f"❌ Gagal analisa: {e}")

async def fix_file(file_path: str, instruction: str = ""):
    """Dandani file otomatis"""
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} ora ono!")
        return
    
    backup_path = f"{file_path}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    
    with open(file_path, 'r') as f:
        original = f.read()
    
    print(f"📦 Backup: {os.path.basename(backup_path)}")
    print(f"📏 Ukuran file: {len(original)} karakter, {len(original.splitlines())} baris")
    
    prompt = f"""
    Kowe iku AI Senior Developer sing ahli Flutter & Python.
    
    TUGAS: DANDANI kode iki.
    {f'CATATAN: {instruction}' if instruction else 'Dandani error, tambahi import sing kurang, optimalke.'}
    
    ATURAN PENTING:
    - BALIKKE KABEH KODE sing wis didandani
    - OJO NGANGGO backticks (```)
    - OJO ngganti struktur utama
    - Tambahi komentar nang bagian sing diowahi (nganggo "// FIXED:" utawa "# FIXED:")
    - Prioritaskan perbaikan error lan bug
    
    FILE: {file_path}
    
    KODE SAIKI:
    {original}
    """
    
    try:
        print("🔧 Lagi ndandani...")
        updated = await ollama_ai.generate(prompt)
        clean_code = updated.replace("```dart", "").replace("```python", "").replace("```yaml", "").replace("```", "").strip()
        
        if len(clean_code) < 10:
            print("⚠️ Hasil perbaikan kosong, backup ora ditimpa.")
            return
        
        with open(file_path, 'w') as f:
            f.write(clean_code)
        
        print(f"✅ BERES! {os.path.basename(file_path)} wis didandani.")
        print(f"💾 Backup: {backup_path}")
        
        old_lines = len(original.splitlines())
        new_lines = len(clean_code.splitlines())
        print(f"\n📝 Ringkesan owahan:")
        print(f"  - Garis: {old_lines} → {new_lines} ({new_lines - old_lines:+d})")
        print(f"  - Backup: {os.path.basename(backup_path)}")
        
    except Exception as e:
        print(f"❌ Gagal ndandani: {e}")
        if input("\n🔧 Pengen balikke file? (y/n): ").lower() == 'y':
            shutil.copy2(backup_path, file_path)
            print("✅ File dibalikke saka backup.")

async def modify_file(file_path: str, instruction: str):
    """Modifikasi file sesuai instruksi"""
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} ora ono!")
        return
    
    backup_path = f"{file_path}.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    
    with open(file_path, 'r') as f:
        original = f.read()
    
    print(f"📦 Backup: {os.path.basename(backup_path)}")
    
    prompt = f"""
    Kowe iku AI Senior Developer.
    
    TUGAS: MODIFIKASI kode iki sesuai instruksi.
    INSTRUKSI: {instruction}
    
    ATURAN:
    - Balikke kabeh kode sing wis dimodifikasi
    - Ojo nganggo backticks
    - Tambahi komentar nang bagian anyar (nganggo "// ADDED:" utawa "# ADDED:")
    - Jaga struktur lan gaya koding sing konsisten
    
    FILE: {file_path}
    
    KODE SAIKI:
    {original}
    """
    
    try:
        print("🔨 Lagi ngowahi...")
        modified = await ollama_ai.generate(prompt)
        clean_code = modified.replace("```dart", "").replace("```python", "").replace("```yaml", "").replace("```", "").strip()
        
        if len(clean_code) < 10:
            print("⚠️ Hasil modifikasi kosong, backup ora ditimpa.")
            return
        
        with open(file_path, 'w') as f:
            f.write(clean_code)
        
        print(f"✅ MODIFIKASI BERHASIL!")
        print(f"📦 Backup: {backup_path}")
        
        old_lines = len(original.splitlines())
        new_lines = len(clean_code.splitlines())
        print(f"\n📝 Ringkesan owahan:")
        print(f"  - Garis: {old_lines} → {new_lines} ({new_lines - old_lines:+d})")
        
    except Exception as e:
        print(f"❌ Gagal modifikasi: {e}")
        if input("\n🔧 Pengen balikke file? (y/n): ").lower() == 'y':
            shutil.copy2(backup_path, file_path)
            print("✅ File dibalikke saka backup.")

async def execute_command(command: str):
    """Jalanake command lan analisa output"""
    print(f"🚀 Jalanake: {command}")
    
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=PROJECT_ROOT
        )
        
        stdout, stderr = process.communicate(timeout=60)
        
        if stdout:
            print("\n📤 OUTPUT:")
            print(stdout)
        
        if stderr:
            print("\n⚠️ ERROR:")
            print(stderr)
            
            if process.returncode != 0:
                print("\n🔍 Analisa error...")
                await analyze_error(stderr)
        
        print(f"\n✅ Selesai kode: {process.returncode}")
        
    except subprocess.TimeoutExpired:
        process.kill()
        print("❌ Command timeout (60 detik)")
    except Exception as e:
        print(f"❌ Error: {e}")

async def analyze_error(error_text: str):
    """Analisa error message lan kasi solusi"""
    prompt = f"""
    Kowe iku AI Developer. Terima error iki:
    
    {error_text[:1000]}
    
    Tugasmu:
    1. Jelaskan penyebab error (bahasa santai)
    2. Kasi solusi konkret
    3. Kasi contoh kode sing bener
    
    Gawe gaya ngomong kaya lagi ngobrol nang grup developer.
    """
    
    try:
        solution = await ollama_ai.generate(prompt)
        print("\n💡 SARAN SOLUSI:")
        print(solution)
    except:
        pass

def scan_project():
    """Scan kabeh project golek masalah umum"""
    print("🔍 Scanning project...")
    
    issues = []
    
    # Cek pubspec.yaml
    pubspec = f"{FRONTEND_DIR}/pubspec.yaml"
    if os.path.exists(pubspec):
        with open(pubspec, 'r') as f:
            content = f.read()
            if "cupertino_icons" not in content:
                issues.append("⚠️ Pubspec: cupertino_icons mungkin kurang")
            if "http:" not in content and "dio:" not in content:
                issues.append("⚠️ Pubspec: KOK tanpa http client?")
    
    # Cek file Dart tanpa import
    for root, dirs, files in os.walk(LIB_DIR):
        for file in files:
            if file.endswith('.dart'):
                path = os.path.join(root, file)
                with open(path, 'r') as f:
                    try:
                        content = f.read()
                        if "import '" not in content and file != "main.dart" and "part of" not in content:
                            issues.append(f"⚠️ {file}: Kok tanpa import?")
                    except:
                        pass
    
    # Cek file Python tanpa imports
    py_files = 0
    for root, dirs, files in os.walk(BACKEND_DIR):
        if 'venv' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                py_files += 1
    
    print("\n" + "="*50)
    print("📋 HASIL SCAN:")
    print("="*50)
    
    if issues:
        for issue in issues[:15]:
            print(issue)
        print(f"\n⚠️ Total masalah: {len(issues)}")
    else:
        print("✅ Ora nemu masalah berarti!")
    
    print(f"\n📊 Statistik:")
    print(f"  - File Dart: {len([f for f in Path(LIB_DIR).rglob('*.dart')])}")
    print(f"  - File Python: {py_files}")
    print(f"  - Backup files: {len([f for f in Path(PROJECT_ROOT).rglob('*.bak*')])}")

async def smart_parse(command: str):
    """Parse perintah bahasa alami"""
    
    if any(word in command for word in ["gawe", "buat", "tambah", "create", "add"]):
        for file_key in FILE_MAP:
            if file_key in command:
                await modify_file(FILE_MAP[file_key], command)
                return
        print("❓ File apa sing arep digawe? Sebutno jenenge.")
        
    elif any(word in command for word in ["dandani", "benak", "fix", "repair", "benerke"]):
        for file_key in FILE_MAP:
            if file_key in command:
                await fix_file(FILE_MAP[file_key], command)
                return
        
        words = command.split()
        for word in words:
            if word.endswith('.dart') or word.endswith('.py') or word.endswith('.yaml'):
                file_path = find_file(word)
                if file_path:
                    await fix_file(file_path, command)
                    return
        
        print("❓ File endi sing arep didandani?")
        
    elif any(word in command for word in ["analisa", "cek", "check", "lihat", "analisis"]):
        for file_key in FILE_MAP:
            if file_key in command:
                await analyze_file(FILE_MAP[file_key], command)
                return
        
        await analyze_file(LIB_DIR, command)
        
    elif any(word in command for word in ["run", "jalan", "execute", "flutter", "python"]):
        cmd = command.replace("run", "").replace("jalan", "").replace("execute", "").strip()
        if cmd:
            await execute_command(cmd)
        else:
            print("❓ Perintah apa sing arep dijalanke?")
            
    elif "scan" in command:
        scan_project()
        
    elif "list" in command or "file" in command:
        list_available_files()
        
    else:
        if len(command.split()) == 1 and command in FILE_MAP:
            file_path = FILE_MAP[command]
            if os.path.exists(file_path):
                print(f"📂 {file_path}")
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines[:20]):
                        print(f"{i+1:4d}: {line.rstrip()}")
                    if len(lines) > 20:
                        print(f"... lan {len(lines)-20} baris liyane")
            else:
                print(f"❌ File {command} ora ketemu!")
        else:
            print(f"❓ Aku durung mudeng: '{command}'")
            show_menu()

# ==================== MAIN ====================
async def main():
    if len(sys.argv) < 2:
        show_menu()
        return
    
    if sys.argv[1] == "--help" or sys.argv[1] == "-h":
        show_menu()
    elif sys.argv[1] == "--list":
        list_available_files()
    elif sys.argv[1] == "--fix":
        if len(sys.argv) > 2:
            file_path = find_file(sys.argv[2])
            if file_path:
                instruction = " ".join(sys.argv[3:]) if len(sys.argv) > 3 else ""
                await fix_file(file_path, instruction)
            else:
                print(f"❌ File '{sys.argv[2]}' ora ketemu!")
                print("Coba 'dibs --list' kanggo deleng file sing kasedia.")
    elif sys.argv[1] == "--mod":
        if len(sys.argv) > 3:
            file_path = find_file(sys.argv[2])
            if file_path:
                instruction = " ".join(sys.argv[3:])
                await modify_file(file_path, instruction)
            else:
                print(f"❌ File '{sys.argv[2]}' ora ketemu!")
    elif sys.argv[1] == "--exec":
        if len(sys.argv) > 2:
            await execute_command(" ".join(sys.argv[2:]))
    elif sys.argv[1] == "--scan":
        scan_project()
    else:
        command = " ".join(sys.argv[1:])
        await smart_parse(command.lower())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Dadah Jon! Matur suwun.")
    except Exception as e:
        print(f"❌ Error umum: {e}")
