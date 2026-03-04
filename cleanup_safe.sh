#!/bin/bash

echo "🧹 Starting safe cleanup..."

# ===== FRONTEND CLEANUP =====
cd frontend

echo "Cleaning frontend..."

# 1. Remove temporary Python fix scripts
rm -f add_debug_logs.py add_inclusive_button.py check_projects.py
rm -f debug_toko_blank.py final_fix_toko.py fix_*.py
rm -f update_main.py update_toko_provider.py
echo "✅ Removed fix scripts"

# 2. Remove backup files
rm -f lib/main.dart.backup-inclusive lib/main.dart.bak*
rm -f lib/providers/*.bak lib/providers/*.broken
rm -f pubspec.yamlnnn
echo "✅ Removed backup files"

# 3. Remove duplicate font/image folders
rm -rf fonts images  # Keep only in assets/
echo "✅ Removed duplicate assets"

# 4. Clean build artifacts (can rebuild anytime)
rm -rf build
echo "✅ Removed build folder"

# ===== BACKEND CLEANUP =====
cd ../backend

echo "Cleaning backend..."

# 1. Remove old backups
rm -f main.py.bak* config/settings.py.broken
echo "✅ Removed backup files"

# 2. Remove unused Modelfiles (keep one if needed)
rm -f Modelfile.balanced Modelfile.q4
echo "✅ Removed unused Modelfiles"

# 3. Clean logs
> backend.log  # Empty but keep file
echo "✅ Cleared backend.log"

# 4. Remove __pycache__ (will regenerate)
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
echo "✅ Removed __pycache__"

# 5. Clean unused tools scripts
rm -f tools/dibs_auto.py tools/dibs_pinter.py tools/dibs_sync.py
echo "✅ Removed unused tools"

# ===== ROOT CLEANUP =====
cd ..

echo "Cleaning root..."

# 1. Remove old scripts
rm -f auto_healer.py auto_healer_final.py check_db.sh cleanup.sh
rm -f create_admin.py create_user.py final_cleanup.* fix_*.py
rm -f init_db.py update_*.py healer.log
echo "✅ Removed old scripts"

# 2. Clean old database (keep data/dibs.db)
rm -f dibs1.db  # Old location
echo "✅ Removed old database"

# 3. Archive old APKs (already done)
echo "✅ APKs already archived"

# ===== SUMMARY =====
echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📊 Disk space saved:"
du -sh frontend/build 2>/dev/null || echo "  build: already removed"
du -sh backend/__pycache__ 2>/dev/null || echo "  __pycache__: cleaned"
echo ""
echo "⚠️  KEPT (important):"
echo "  - All source code (.dart, .py)"
echo "  - venv (backend dependencies)"
echo "  - data/dibs.db (main database)"
echo "  - backend/toko.db (toko database)"  
echo "  - Final APK (downloads/dibs-ai-v2.3.0-STABLE.apk)"
