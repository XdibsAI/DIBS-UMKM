#!/usr/bin/env python3
"""
Fix toko_screen.dart - Memperbaiki struktur build() method yang kacau
"""

import re
import shutil
from pathlib import Path

FILE_PATH = Path.home() / "dibs1/frontend/lib/screens/toko/toko_screen.dart"
BACKUP_PATH = FILE_PATH.with_suffix(".dart.bak.final")

NEW_BUILD_METHOD = '''  @override
  Widget build(BuildContext context) {
    final bgColor = _getBackgroundColor(context);
    final surfaceColor = _getSurfaceColor(context);
    final textColor = _getTextColor(context);
    final secondaryTextColor = _getSecondaryTextColor(context);
    final iconColor = _getIconColor(context);

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
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
        ],
      ),
      bottom: const TabBar(
        tabs: [
          Tab(text: 'Dashboard', icon: Icon(Icons.dashboard)),
          Tab(text: 'Kasir', icon: Icon(Icons.point_of_sale)),
          Tab(text: 'Produk', icon: Icon(Icons.inventory)),
        ],
      ),
      body: Consumer<TokoProvider>(
        builder: (context, provider, child) {
          return TabBarView(
            children: [
              _buildDashboard(context, iconColor, textColor, secondaryTextColor, surfaceColor),
              _buildKasir(context, iconColor, textColor, secondaryTextColor, surfaceColor),
              _buildProduk(context, iconColor, textColor, secondaryTextColor, surfaceColor),
            ],
          );
        },
      ),
    );
  }'''

def find_build_method_range(lines):
    """Cari baris awal dan akhir dari method build()"""
    start = None
    brace_count = 0
    in_method = False

    for i, line in enumerate(lines):
        if start is None:
            # Cari @override diikuti Widget build
            if '@override' in line:
                # Cek apakah baris berikutnya adalah Widget build
                for j in range(i, min(i+3, len(lines))):
                    if 'Widget build(BuildContext context)' in lines[j]:
                        start = i
                        break
        
        if start is not None and i >= start:
            brace_count += line.count('{') - line.count('}')
            if i > start and brace_count == 0:
                return start, i
    
    return start, None

def main():
    if not FILE_PATH.exists():
        print(f"❌ File tidak ditemukan: {FILE_PATH}")
        return

    # Backup dulu
    shutil.copy2(FILE_PATH, BACKUP_PATH)
    print(f"✅ Backup dibuat: {BACKUP_PATH}")

    content = FILE_PATH.read_text(encoding='utf-8')
    lines = content.splitlines()

    start, end = find_build_method_range(lines)

    if start is None or end is None:
        print(f"❌ Tidak bisa menemukan method build(). start={start}, end={end}")
        print("   Coba cek manual dengan: grep -n 'Widget build' ~/dibs1/frontend/lib/screens/toko/toko_screen.dart")
        return

    print(f"✅ Method build() ditemukan: baris {start+1} - {end+1}")

    # Ganti bagian tersebut
    new_lines = lines[:start] + NEW_BUILD_METHOD.splitlines() + lines[end+1:]
    new_content = '\n'.join(new_lines) + '\n'

    FILE_PATH.write_text(new_content, encoding='utf-8')
    print(f"✅ File berhasil diperbaiki!")
    print()
    print("🚀 Sekarang jalankan:")
    print("   cd ~/dibs1/frontend")
    print("   flutter clean && flutter pub get")
    print("   flutter build apk --release --dart-define=API_URL=http://94.100.26.128:8081/api/v1")
    print()
    print(f"⚠️  Jika ada masalah, restore backup dengan:")
    print(f"   cp {BACKUP_PATH} {FILE_PATH}")

if __name__ == "__main__":
    main()
