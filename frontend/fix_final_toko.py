#!/usr/bin/env python3
"""
Fix final - toko screen
"""
import shutil
from pathlib import Path

FILE_PATH = Path("lib/screens/toko/toko_screen.dart")
BACKUP_PATH = FILE_PATH.with_suffix(".dart.bak.final")

shutil.copy2(FILE_PATH, BACKUP_PATH)
print(f"✅ Backup: {BACKUP_PATH}")

with open(FILE_PATH, 'r') as f:
    content = f.read()

# Fix 1: Hapus semua print debug yang bikin error
import re
content = re.sub(r'^\s*print\(".*?"\);\s*\n', '', content, flags=re.MULTILINE)

# Fix 2: Pastikan fungsi-fungsi tab menerima parameter yang benar
# (tidak bisa dengan regex sederhana, tapi kita restore dari backup yang benar)

# Karena kompleks, kita restore dari backup terbaik yang ada
print("\n🔍 Mencari backup terbaik...")
backups = list(Path("lib/screens/toko").glob("*.bak*"))
if backups:
    # Ambil backup terbaru yang bukan dari debug tadi
    latest = max(backups, key=lambda p: p.stat().st_mtime)
    if "debug" not in latest.name:
        shutil.copy2(latest, FILE_PATH)
        print(f"✅ Restore dari: {latest}")
    else:
        print("⚠️ Hanya ada backup debug, perlu restore manual")
else:
    print("❌ Tidak ada backup ditemukan")

print("\n🚀 YANG HARUS DILAKUKAN:")
print("1. Edit manual file ini:")
print("   nano lib/screens/toko/toko_screen.dart")
print("\n2. Cari baris sekitar 110-130, pastikan TabBarView memanggil fungsi dengan parameter:")
print("   _buildDashboard(context, iconColor, textColor, secondaryTextColor, surfaceColor)")
print("\n3. Pastikan setiap fungsi tab (_buildDashboard, _buildKasir, _buildProduk)")
print("   menerima 5 parameter tersebut.")
print("\n4. Simpan dan build ulang:")
print("   flutter clean && flutter pub get")
print("   flutter build apk --release --dart-define=API_URL=http://94.100.26.128:8081/api/v1")
