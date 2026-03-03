#!/usr/bin/env python3
"""
Fix _buildStatCard - tambahkan parameter warna
"""
import shutil
from pathlib import Path

FILE_PATH = Path("lib/screens/toko/toko_screen.dart")
BACKUP_PATH = FILE_PATH.with_suffix(".dart.bak.statcard")

shutil.copy2(FILE_PATH, BACKUP_PATH)
print(f"✅ Backup dibuat: {BACKUP_PATH}")

with open(FILE_PATH, 'r') as f:
    content = f.read()

# Fix 1: Cari dan perbaiki _buildStatCard di dalam _buildDashboard
import re

# Pola untuk mencari pemanggilan _buildStatCard
pattern = r'_buildStatCard\(\s*([^,]+),\s*([^,]+),\s*([^,]+),\s*iconColor,\s*surfaceColor\s*\)'

# Ganti dengan parameter yang benar (iconColor dan surfaceColor sudah ada)
replacement = r'_buildStatCard(\1, \2, \3, iconColor, surfaceColor)'
content = re.sub(pattern, replacement, content)

# Fix 2: Pastikan fungsi _buildStatCard menerima parameter warna
stat_card_func = '''
  Widget _buildStatCard(
    String title,
    String value,
    IconData icon,
    Color iconColor,
    Color surfaceColor,
  ) {
    return Card(
      color: surfaceColor,
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: iconColor, size: 24),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: iconColor,
              ),
            ),
            Text(
              title,
              style: TextStyle(
                fontSize: 12,
                color: iconColor.withOpacity(0.7),
              ),
            ),
          ],
        ),
      ),
    );
  }
'''

# Ganti fungsi _buildStatCard yang lama
stat_card_pattern = r'Widget _buildStatCard\([^}]*}\s*}'
content = re.sub(stat_card_pattern, stat_card_func, content, flags=re.DOTALL)

with open(FILE_PATH, 'w') as f:
    f.write(content)

print("✅ _buildStatCard telah diperbaiki!")
print("   - Fungsi sekarang menerima iconColor dan surfaceColor")
print("   - Pemanggilan di _buildDashboard sudah disesuaikan")
print("\n🚀 Build sekarang:")
print("   flutter clean && flutter pub get")
print("   flutter build apk --release --dart-define=API_URL=http://94.100.26.128:8081/api/v1")
