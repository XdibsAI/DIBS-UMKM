#!/bin/bash
set -e

echo "🧹 DIBS1 Cleanup - Removing unnecessary files..."

# Backup important files first
echo "📦 Creating safety backup..."
tar -czf ~/dibs1_backup_$(date +%Y%m%d_%H%M%S).tar.gz \
    backend/main.py \
    backend/main_monolith.py \
    .env 2>/dev/null || true

# Backend cleanup
cd ~/dibs1/backend
echo "🔸 Cleaning backend..."

# Remove all backup files
rm -f main.py.backup* main.py.bak* main.py.before* 2>/dev/null
rm -f main_modular.py modular_*.log 2>/dev/null
rm -f *.py.backup* *.py.bak 2>/dev/null
rm -f fix_*.py patch_*.py cek_*.py 2>/dev/null
rm -f video_agent_lite.py video_agent_full.py 2>/dev/null
rm -rf projects knowledge 2>/dev/null

# Remove old venv (dibs)
rm -rf dibs 2>/dev/null

# Clean pycache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo "✅ Backend cleaned"

# AI video generator cleanup
cd ~/dibs1
if [ -d "ai-video-generator" ]; then
    echo "🔸 Cleaning ai-video-generator..."
    cd ai-video-generator
    
    # Remove all fix/patch scripts
    rm -f fix_*.py create_*.py update_*.py verify_*.py 2>/dev/null
    rm -f quick_*.py safe_*.py simple_*.py direct_*.py 2>/dev/null
    rm -f add_*.py remove_*.py comment_*.py skip_*.py restore_*.py 2>/dev/null
    rm -f use_*.py improve_*.py 2>/dev/null
    
    # Remove backup files in apps
    cd apps 2>/dev/null && rm -f *.backup* main_*.py *_patch.py 2>/dev/null
    cd ~/dibs1/ai-video-generator
    
    # Remove temp video files
    rm -f video_*TEMP*.mp4 2>/dev/null
    
    # Remove backup utils
    cd utils 2>/dev/null && rm -f *.backup* 2>/dev/null
    
    echo "✅ ai-video-generator cleaned"
fi

# Root cleanup
cd ~/dibs1
echo "🔸 Cleaning root directory..."
rm -f backend.log database.db check_dibs_ai.py build.sh gen_keys.py 2>/dev/null
rm -f dibs1.db.backup* dibs1.db.bak 2>/dev/null
rm -f server.sh tanya_ai.sh test_video_generation.sh 2>/dev/null
rm -f model.gguf llama-cli 2>/dev/null
rm -rf knowledge temp uploads media/temp 2>/dev/null
rm -rf frontend_old 2>/dev/null

# Old venv in root
rm -rf venv 2>/dev/null

# Keep only latest 5 APKs
cd downloads 2>/dev/null
echo "🔸 Cleaning old APKs (keeping latest 5)..."
ls -t dibs1-*.apk 2>/dev/null | tail -n +6 | xargs rm -f 2>/dev/null || true

echo ""
echo "✅ Cleanup complete!"
echo ""
echo "📊 Space saved:"
du -sh ~/dibs1 2>/dev/null
echo ""
echo "📁 Remaining structure:"
tree -L 2 -I 'venv|build|__pycache__|node_modules' ~/dibs1
