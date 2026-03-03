#!/usr/bin/env python3
"""
Fix syntax error di toko_screen.dart - Version 2 dengan regex sederhana
"""
import re
import os

def fix_toko_screen():
    # Backup dulu
    backup_file = 'lib/screens/toko/toko_screen.dart.bak.' + str(int(time.time()))
    os.system(f'cp lib/screens/toko/toko_screen.dart {backup_file}')
    print(f"✅ Backup created: {backup_file}")
    
    # Baca file baris per baris (lebih aman)
    with open('lib/screens/toko/toko_screen.dart', 'r') as f:
        lines = f.readlines()
    
    # Cari dan perbaiki baris yang bermasalah
    new_lines = []
    fixed = False
    
    for i, line in enumerate(lines):
        # Cari pattern "],appBar: AppBar("
        if '],appBar: AppBar' in line:
            # Split menjadi dua baris
            parts = line.split('],appBar: AppBar')
            new_lines.append(parts[0] + '],\n')
            new_lines.append('      ),\n')
            new_lines.append('      appBar: AppBar' + parts[1])
            fixed = True
            print(f"✅ Fixed line {i+1}: {line.strip()} -> split into 3 lines")
        else:
            new_lines.append(line)
    
    if not fixed:
        # Coba cari pattern lain
        for i, line in enumerate(lines):
            if '],appBar:' in line and 'AppBar' in line:
                new_line = line.replace('],appBar:', '],\n      ),\n      appBar:')
                new_lines[i] = new_line
                fixed = True
                print(f"✅ Fixed line {i+1} with alternative pattern")
                break
    
    # Tulis kembali
    with open('lib/screens/toko/toko_screen.dart', 'w') as f:
        f.writelines(new_lines)
    
    if fixed:
        print("✅ File telah diperbaiki")
    else:
        print("⚠️ Tidak menemukan pattern yang perlu diperbaiki")
    
    return fixed

def verify_syntax():
    """Cek apakah file masih punya masalah syntax"""
    with open('lib/screens/toko/toko_screen.dart', 'r') as f:
        content = f.read()
    
    issues = []
    
    # Cek pattern yang salah
    if '],appBar:' in content:
        issues.append("❌ Masih ada pattern '],appBar:'")
    
    if ']),appBar:' in content:
        issues.append("❌ Masih ada pattern ']),appBar:'")
    
    # Cek jumlah kurung
    open_paren = content.count('(')
    close_paren = content.count(')')
    open_bracket = content.count('[')
    close_bracket = content.count(']')
    open_brace = content.count('{')
    close_brace = content.count('}')
    
    print("\n📊 Statistik kurung:")
    print(f"   ( : {open_paren}  ) : {close_paren}  {'✅' if open_paren == close_paren else '❌'}")
    print(f"   [ : {open_bracket}  ] : {close_bracket}  {'✅' if open_bracket == close_bracket else '❌'}")
    print(f"   {{ : {open_brace}  }} : {close_brace}  {'✅' if open_brace == close_brace else '❌'}")
    
    if open_paren != close_paren:
        issues.append(f"❌ Kurung tidak seimbang: (={open_paren}, )={close_paren}")
    
    if issues:
        print("\n".join(issues))
        return False
    else:
        print("\n✅ Semua kurung seimbang, tidak ada pattern salah")
        return True

def show_preview():
    """Tampilkan bagian yang diperbaiki"""
    print("\n📝 Preview bagian AppBar:")
    with open('lib/screens/toko/toko_screen.dart', 'r') as f:
        lines = f.readlines()
    
    appbar_lines = []
    recording = False
    
    for i, line in enumerate(lines):
        if 'appBar: AppBar' in line or 'actions: [' in line:
            recording = True
            appbar_lines = []
        if recording:
            appbar_lines.append(line.strip())
            if 'bottom: TabBar' in line:
                break
    
    for line in appbar_lines[:20]:
        print(f"   {line}")

import time
if __name__ == "__main__":
    fixed = fix_toko_screen()
    if fixed:
        verify_syntax()
        show_preview()
        print("\n🚀 Selanjutnya build APK:")
        print("   flutter clean")
        print("   flutter pub get")
        print("   flutter build apk --release --dart-define=API_URL=http://94.100.26.128:8081/api/v1")
        print("   cp build/app/outputs/flutter-apk/app-release.apk ~/dibs1/downloads/dibs1-latest.apk")
    else:
        # Kalau tidak fixed, tampilkan petunjuk manual
        print("\n🔧 Silakan edit manual dengan nano:")
        print("   nano lib/screens/toko/toko_screen.dart")
        print("\nCari baris yang mengandung '],appBar: AppBar'")
        print("Ubah menjadi:")
        print("        ],")
        print("      ),")
        print("      appBar: AppBar(")
