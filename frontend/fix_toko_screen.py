#!/usr/bin/env python3
"""
Fix syntax error di toko_screen.dart
"""
import re

def fix_toko_screen():
    # Backup dulu
    import shutil
    import os
    
    backup_file = 'lib/screens/toko/toko_screen.dart.bak.' + os.path.basename(__file__).replace('.py', '')
    shutil.copy2('lib/screens/toko/toko_screen.dart', backup_file)
    print(f"✅ Backup created: {backup_file}")
    
    # Baca file
    with open('lib/screens/toko/toko_screen.dart', 'r') as f:
        content = f.read()
    
    # 1. Fix pattern pertama: ],appBar: AppBar(
    pattern1 = r'(\s+\),[\s\n]*\],appBar: AppBar\('
    replacement1 = r'        ),\n      ],\n      appBar: AppBar('
    content = re.sub(pattern1, replacement1, content)
    
    # 2. Fix pattern kedua: kemungkinan ada versi lain
    pattern2 = r'(\s+\),[\s\n]*\],\s*appBar: AppBar\('
    replacement2 = r'        ),\n      ],\n      appBar: AppBar('
    content = re.sub(pattern2, replacement2, content)
    
    # 3. Pastikan struktur Scaffold benar
    # Cari scaffold yang mungkin kehilangan kurung buka
    if 'Scaffold(' in content and 'appBar:' in content:
        # Sudah ok
        pass
    
    # Tulis kembali
    with open('lib/screens/toko/toko_screen.dart', 'w') as f:
        f.write(content)
    
    print("✅ File telah diperbaiki")

def verify():
    """Cek apakah masih ada error syntax"""
    print("\n🔍 VERIFIKASI:")
    
    with open('lib/screens/toko/toko_screen.dart', 'r') as f:
        content = f.read()
    
    # Cek pattern yang salah
    if '],appBar:' in content:
        print("❌ Masih ditemukan pattern '],appBar:'")
    else:
        print("✅ Pattern '],appBar:' sudah tidak ada")
    
    if ']),appBar:' in content:
        print("❌ Masih ditemukan pattern ']),appBar:'")
    else:
        print("✅ Pattern ']),appBar:' sudah tidak ada")
    
    # Cek jumlah kurung
    open_paren = content.count('(')
    close_paren = content.count(')')
    open_bracket = content.count('[')
    close_bracket = content.count(']')
    open_brace = content.count('{')
    close_brace = content.count('}')
    
    print(f"\n📊 Statistik kurung:")
    print(f"   ( : {open_paren}  ) : {close_paren}  {'✅' if open_paren == close_paren else '❌'}")
    print(f"   [ : {open_bracket}  ] : {close_bracket}  {'✅' if open_bracket == close_bracket else '❌'}")
    print(f"   {{ : {open_brace}  }} : {close_brace}  {'✅' if open_brace == close_brace else '❌'}")
    
    # Tampilkan bagian sekitar actions untuk preview
    print("\n📝 Preview bagian yang diperbaiki:")
    lines = content.split('\n')
    action_lines = []
    recording = False
    count = 0
    
    for i, line in enumerate(lines):
        if 'actions: [' in line:
            recording = True
            action_lines = []
            count = 0
        if recording:
            action_lines.append(line.strip())
            if '],' in line and count > 3:
                break
            count += 1
    
    for line in action_lines[:15]:
        print(f"   {line}")

if __name__ == "__main__":
    fix_toko_screen()
    verify()
    print("\n🚀 Selanjutnya build APK:")
    print("   flutter clean")
    print("   flutter pub get")
    print("   flutter build apk --release --dart-define=API_URL=http://94.100.26.128:8081/api/v1")
    print("   cp build/app/outputs/flutter-apk/app-release.apk ~/dibs1/downloads/dibs1-latest.apk")
