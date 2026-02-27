#!/bin/bash
echo "🧹 Final cleanup pass..."

# 1. Backend - Remove unused ngelantur files
cd ~/dibs1/backend
rm -f ngelantur_*.py 2>/dev/null
rm -f main.py.MONOLITH-BACKUP main_monolith.py 2>/dev/null
rm -f database.db 2>/dev/null  # Duplicate, use ~/dibs1/dibs1.db
echo "✅ Backend cleaned"

# 2. Frontend - Remove backup files
cd ~/dibs1/frontend/lib
rm -f main.dart.backup 2>/dev/null
rm -f providers/chat_provider.dart.backup* providers/chat_provider.dart.bak providers/chat_provider_new.dart 2>/dev/null
rm -f services/api_service.dart.backup services/api_service.dart.bak 2>/dev/null
rm -f pubspec.yamlnnn 2>/dev/null
echo "✅ Frontend cleaned"

# 3. AI video generator - Remove test files
cd ~/dibs1/ai-video-generator
rm -f check_syntax.py final_fix.py test_*.py 2>/dev/null
echo "✅ AI video generator cleaned"

# 4. MCP - Remove redundant files
cd ~/dibs1/mcp-server
rm -f mcp_server.py mcp_server_fixed.py mcp_wrapper.sh 2>/dev/null
echo "✅ MCP server cleaned"

# 5. Root - Remove empty dirs
cd ~/dibs1
rmdir thumbnails 2>/dev/null || true
rmdir media/thumbnails media/videos media 2>/dev/null || true

# 6. Clean old video outputs (keep only last 3)
cd video_outputs 2>/dev/null
if [ -d "$(pwd)" ]; then
    ls -t audio_*.mp3 2>/dev/null | tail -n +4 | xargs rm -f 2>/dev/null || true
    ls -t video_*.mp4 2>/dev/null | tail -n +4 | xargs rm -f 2>/dev/null || true
fi

echo "✅ Video outputs trimmed"

# 7. Clean Flutter build cache (optional, uncomment if needed)
# cd ~/dibs1/frontend && flutter clean

echo ""
echo "✅ Final cleanup complete!"
echo "📊 Final size:"
du -sh ~/dibs1
