#!/usr/bin/env python3
"""
Update manage.sh - Fix dangling symlink issue in build function
"""
import re
import os
from datetime import datetime

def update_manage_sh():
    # Baca file manage.sh
    with open('manage.sh', 'r') as f:
        content = f.read()
    
    # Pattern untuk mencari fungsi build()
    build_pattern = r'(build\(\) \{\n.*?\n    # Copy ke download folder\n    mkdir -p "\$DOWNLOAD_DIR"\n)(.*?)(    local size=.*?\n)'
    
    # Fungsi build yang baru dengan fix symlink
    new_build = r'''build() {
    echo -e "\n${BLUE}📱 BUILDING APK...${NC}\n"

    cd "$FRONTEND_DIR"

    # Bersihkan
    flutter clean > /dev/null 2>&1
    rm -rf pubspec.lock

    # Install dependencies
    flutter pub get > /dev/null 2>&1

    # Build dengan logging
    echo -e "${YELLOW}⏳ Building APK, mohon tunggu...${NC}"
    flutter build apk --release

    # Copy ke download folder
    mkdir -p "$DOWNLOAD_DIR"
    
    # Hapus symlink/file lama
    rm -f "$DOWNLOAD_DIR/dibs1-latest.apk"
    
    # Copy file baru
    cp build/app/outputs/flutter-apk/app-release.apk "$DOWNLOAD_DIR/dibs1-latest.apk"
    cp build/app/outputs/flutter-apk/app-release.apk "$DOWNLOAD_DIR/dibs1-$(date +%Y%m%d-%H%M).apk"

    local size=$(du -h "$DOWNLOAD_DIR/dibs1-latest.apk" | cut -f1)
    echo -e "\n${GREEN}✅ APK siap!${NC}"
    echo -e "  📦 Ukuran: $size"
    echo -e "  📱 URL: http://$IP:$DOWNLOAD_PORT/dibs1-latest.apk"
    echo -e "  💾 Backup: dibs1-$(date +%Y%m%d-%H%M).apk\n"
}'''
    
    # Ganti fungsi build() yang lama dengan yang baru
    new_content = re.sub(
        r'build\(\) \{\n.*?\n\}',
        new_build,
        content,
        flags=re.DOTALL
    )
    
    # Tulis kembali file
    with open('manage.sh', 'w') as f:
        f.write(new_content)
    
    print("✅ manage.sh updated successfully!")
    print("📁 Backup saved as: manage.sh.bak." + datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    # Tampilkan perbedaan
    print("\n📊 Changes made:")
    print("  - Added 'rm -f \"$DOWNLOAD_DIR/dibs1-latest.apk\"' before copying")
    print("  - Fixed dangling symlink issue")

if __name__ == "__main__":
    update_manage_sh()
