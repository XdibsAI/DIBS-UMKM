#!/usr/bin/env python3
"""
Tambahkan debug print di toko_screen.dart
"""
import shutil
from pathlib import Path

FILE_PATH = Path("lib/screens/toko/toko_screen.dart")
BACKUP_PATH = FILE_PATH.with_suffix(".dart.bak.debug")

shutil.copy2(FILE_PATH, BACKUP_PATH)
print(f"✅ Backup: {BACKUP_PATH}")

with open(FILE_PATH, 'r') as f:
    lines = f.readlines()

new_lines = []
added = False

for line in lines:
    new_lines.append(line)
    
    # Tambah debug print di awal build
    if 'Widget build(BuildContext context) {' in line and not added:
        new_lines.append('    print("🚀 TokoScreen build started");\n')
        added = True
    
    # Tambah debug di setiap tab function
    if '_buildDashboard' in line and '(' in line:
        new_lines.append('    print("📊 _buildDashboard called");\n')
    if '_buildKasir' in line and '(' in line:
        new_lines.append('    print("💰 _buildKasir called");\n')
    if '_buildProduk' in line and '(' in line:
        new_lines.append('    print("📦 _buildProduk called");\n')

with open(FILE_PATH, 'w') as f:
    f.writelines(new_lines)

print("✅ Debug logs added")
print("\n🚀 Jalankan ulang:")
print("   flutter run --dart-define=API_URL=http://94.100.26.128:8081/api/v1")
