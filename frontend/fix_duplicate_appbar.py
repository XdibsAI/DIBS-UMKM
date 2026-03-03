#!/usr/bin/env python3
"""
Fix duplicate appBar di toko_screen.dart
"""
import re

def fix_duplicate_appbar():
    # Backup dulu
    import shutil
    import time
    backup_file = f'lib/screens/toko/toko_screen.dart.bak.duplicate.{int(time.time())}'
    shutil.copy2('lib/screens/toko/toko_screen.dart', backup_file)
    print(f"✅ Backup created: {backup_file}")
    
    # Baca file
    with open('lib/screens/toko/toko_screen.dart', 'r') as f:
        lines = f.readlines()
    
    # Cari dan hapus appBar duplikat
    new_lines = []
    appbar_count = 0
    fixed = False
    
    for i, line in enumerate(lines):
        # Hitung appBar
        if 'appBar: AppBar' in line:
            appbar_count += 1
            if appbar_count == 2:
                print(f"❌ Found duplicate appBar at line {i+1}")
                # Lewati baris ini (hapus)
                fixed = True
                continue
        
        # Tambahkan baris yang tidak di-skip
        new_lines.append(line)
    
    # Tulis kembali
    with open('lib/screens/toko/toko_screen.dart', 'w') as f:
        f.writelines(new_lines)
    
    if fixed:
        print("✅ Duplicate appBar removed")
    else:
        print("⚠️ No duplicate appBar found")
    
    return fixed

def verify():
    """Verifikasi hasil fix"""
    print("\n🔍 VERIFIKASI:")
    import subprocess
    result = subprocess.run(
        ['flutter', 'analyze', 'lib/screens/toko/toko_screen.dart'],
        capture_output=True,
        text=True
    )
    
    if 'duplicate_named_argument' in result.stderr or 'duplicate_named_argument' in result.stdout:
        print("❌ Still has duplicate appBar error")
        return False
    else:
        print("✅ No duplicate appBar error")
        
        # Tampilkan warning lain (tidak kritis)
        warnings = []
        for line in (result.stdout + result.stderr).split('\n'):
            if 'warning' in line or 'info' in line:
                warnings.append(line.strip())
        
        if warnings:
            print(f"\n📝 Non-critical issues ({len(warnings)}):")
            for w in warnings[:5]:
                print(f"   {w}")
        
        return True

if __name__ == "__main__":
    fixed = fix_duplicate_appbar()
    if fixed:
        verify()
        print("\n🚀 Build sekarang:")
        print("   flutter clean")
        print("   flutter pub get")
        print("   flutter build apk --release --dart-define=API_URL=http://94.100.26.128:8081/api/v1")
    else:
        print("\n🔧 Perlu fix manual:")
        print("   nano lib/screens/toko/toko_screen.dart")
        print("   Cari line 107, hapus appBar duplikat")
