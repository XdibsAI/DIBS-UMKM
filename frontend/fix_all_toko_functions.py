#!/usr/bin/env python3
"""
Fix semua fungsi toko screen dengan Python - tinggal jalankan
"""
import shutil
from pathlib import Path

FILE_PATH = Path("lib/screens/toko/toko_screen.dart")
BACKUP_PATH = FILE_PATH.with_suffix(".dart.bak.finalfix")

# Backup
shutil.copy2(FILE_PATH, BACKUP_PATH)
print(f"✅ Backup dibuat: {BACKUP_PATH}")

# Baca file
with open(FILE_PATH, 'r') as f:
    content = f.read()

# Definisi fungsi yang benar
correct_dashboard = '''  Widget _buildDashboard(
    BuildContext context,
    Color iconColor,
    Color textColor,
    Color secondaryTextColor,
    Color surfaceColor,
  ) {
    print("🚀 _buildDashboard dipanggil");
    return Consumer<TokoProvider>(
      builder: (context, provider, child) {
        if (provider.isLoading) {
          return Center(child: CircularProgressIndicator(color: iconColor));
        }
        if (provider.error != null) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.error_outline, size: 48, color: Colors.red),
                const SizedBox(height: 16),
                Text('Error: \${provider.error}'),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => provider.loadDashboard(),
                  child: const Text('Coba Lagi'),
                ),
              ],
            ),
          );
        }
        // TODO: Implementasi dashboard
        return Center(
          child: Text(
            'Dashboard',
            style: TextStyle(color: textColor, fontSize: 18),
          ),
        );
      },
    );
  }'''

correct_kasir = '''  Widget _buildKasir(
    BuildContext context,
    Color iconColor,
    Color textColor,
    Color secondaryTextColor,
    Color surfaceColor,
  ) {
    print("💰 _buildKasir dipanggil");
    return Consumer<TokoProvider>(
      builder: (context, provider, child) {
        if (provider.isLoading) {
          return Center(child: CircularProgressIndicator(color: iconColor));
        }
        if (provider.cartItems.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.shopping_cart_outlined, size: 80, color: secondaryTextColor),
                const SizedBox(height: 16),
                Text(
                  'Keranjang belanja kosong',
                  style: TextStyle(color: secondaryTextColor, fontSize: 18),
                ),
                const SizedBox(height: 8),
                Text(
                  'Gunakan tombol "Scan Suara" untuk memulai',
                  style: TextStyle(color: secondaryTextColor, fontSize: 14),
                ),
              ],
            ),
          );
        }
        // TODO: Implementasi kasir
        return ListView.builder(
          itemCount: provider.cartItems.length,
          itemBuilder: (context, index) {
            final item = provider.cartItems[index];
            return ListTile(
              title: Text(item['name'] ?? ''),
              subtitle: Text('Rp \${item['price']} x \${item['quantity']}'),
              trailing: Text('Rp \${item['subtotal']}'),
            );
          },
        );
      },
    );
  }'''

correct_produk = '''  Widget _buildProduk(
    BuildContext context,
    Color iconColor,
    Color textColor,
    Color secondaryTextColor,
    Color surfaceColor,
  ) {
    print("📦 _buildProduk dipanggil");
    return Consumer<TokoProvider>(
      builder: (context, provider, child) {
        if (provider.isLoading) {
          return Center(child: CircularProgressIndicator(color: iconColor));
        }
        if (provider.products.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.inventory_outlined, size: 80, color: secondaryTextColor),
                const SizedBox(height: 16),
                Text(
                  'Belum ada produk',
                  style: TextStyle(color: secondaryTextColor, fontSize: 18),
                ),
                const SizedBox(height: 8),
                Text(
                  'Tambahkan produk baru',
                  style: TextStyle(color: secondaryTextColor, fontSize: 14),
                ),
              ],
            ),
          );
        }
        // TODO: Implementasi produk
        return ListView.builder(
          itemCount: provider.products.length,
          itemBuilder: (context, index) {
            final product = provider.products[index];
            return ListTile(
              title: Text(product['name'] ?? ''),
              subtitle: Text('Rp \${product['price']} | Stok: \${product['stock']}'),
            );
          },
        );
      },
    );
  }'''

# Ganti fungsi-fungsi yang ada
import re

# Hapus semua print yang salah
content = re.sub(r'    print\(".*?"\);', '', content)

# Ganti _buildDashboard
dashboard_pattern = r'Widget _buildDashboard\([^}]*}\s*}'
content = re.sub(dashboard_pattern, correct_dashboard, content, flags=re.DOTALL)

# Ganti _buildKasir
kasir_pattern = r'Widget _buildKasir\([^}]*}\s*}'
content = re.sub(kasir_pattern, correct_kasir, content, flags=re.DOTALL)

# Ganti _buildProduk
produk_pattern = r'Widget _buildProduk\([^}]*}\s*}'
content = re.sub(produk_pattern, correct_produk, content, flags=re.DOTALL)

# Tulis kembali
with open(FILE_PATH, 'w') as f:
    f.write(content)

print("✅ Semua fungsi toko telah diperbaiki!")
print("\n📝 Perubahan:")
print("   - _buildDashboard: parameter lengkap + error handling")
print("   - _buildKasir: parameter lengkap + empty state")
print("   - _buildProduk: parameter lengkap + empty state")
print("\n🚀 Build sekarang:")
print("   flutter clean && flutter pub get")
print("   flutter build apk --release --dart-define=API_URL=http://94.100.26.128:8081/api/v1")
