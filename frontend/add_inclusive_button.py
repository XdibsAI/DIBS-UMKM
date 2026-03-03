#!/usr/bin/env python3
"""
Tambahkan tombol mode inklusif di AppBar toko_screen.dart
"""
import re

def add_button():
    # Backup dulu
    import shutil
    shutil.copy2('lib/screens/toko/toko_screen.dart', 'lib/screens/toko/toko_screen.dart.bak')
    print("✅ Backup created")
    
    with open('lib/screens/toko/toko_screen.dart', 'r') as f:
        content = f.read()
    
    # Cari pattern AppBar
    pattern = r'(appBar: AppBar\(\s+backgroundColor: surfaceColor,\s+elevation: 2,\s+title: Text\([^)]+\),[^)]+\)),(\s+bottom: TabBar)'
    
    # Tambahkan actions
    replacement = r'''appBar: AppBar(
        backgroundColor: surfaceColor,
        elevation: 2,
        title: Text(
          'Toko & Kasir',
          style: TextStyle(
            color: iconColor,
            fontSize: 24,
            fontWeight: FontWeight.bold,
          ),
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.accessibility_new, color: iconColor),
            onPressed: () {
              Navigator.pushNamed(context, '/inclusive-checkout');
            },
            tooltip: 'Mode Inklusif',
          ),
        ],\1\2'''
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open('lib/screens/toko/toko_screen.dart', 'w') as f:
        f.write(new_content)
    
    print("✅ Tombol mode inklusif ditambahkan di AppBar")

def verify():
    print("\n🔍 VERIFIKASI:")
    with open('lib/screens/toko/toko_screen.dart', 'r') as f:
        content = f.read()
    
    if 'actions: [' in content and 'accessibility_new' in content:
        print("✅ Tombol berhasil ditambahkan!")
        # Tampilkan preview
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'actions: [' in line:
                print(f"\n📌 Line {i+1}: {line.strip()}")
                for j in range(i+1, i+10):
                    if j < len(lines):
                        print(f"   {lines[j].strip()}")
                    if '],' in lines[j]:
                        break
    else:
        print("❌ Tombol gagal ditambahkan")

if __name__ == "__main__":
    add_button()
    verify()
