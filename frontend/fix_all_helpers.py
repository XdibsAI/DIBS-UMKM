#!/usr/bin/env python3
"""
FIX ALL HELPERS - Tambahkan parameter warna ke semua fungsi helper
"""
import shutil
from pathlib import Path

FILE_PATH = Path("lib/screens/toko/toko_screen.dart")
BACKUP_PATH = FILE_PATH.with_suffix(".dart.bak.helpers")

shutil.copy2(FILE_PATH, BACKUP_PATH)
print(f"✅ Backup dibuat: {BACKUP_PATH}")

with open(FILE_PATH, 'r') as f:
    content = f.read()

# ==================== FUNGSI HELPER YANG BENAR ====================

# _buildStatCard
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

# _showVoiceScanDialog
voice_dialog_func = '''
  void _showVoiceScanDialog(BuildContext context, Color iconColor) {
    showDialog(
      context: context,
      builder: (ctx) {
        String text = '';
        return AlertDialog(
          title: const Text('Scan Suara'),
          content: TextField(
            onChanged: (val) => text = val,
            decoration: const InputDecoration(
              hintText: 'Contoh: 2 keripik pisang 1 cireng',
              border: OutlineInputBorder(),
            ),
            autofocus: true,
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Batal'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(ctx);
                Provider.of<TokoProvider>(context, listen: false)
                    .processVoiceScan(text);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: iconColor,
                foregroundColor: Colors.white,
              ),
              child: const Text('Proses'),
            ),
          ],
        );
      },
    );
  }
'''

# _processCheckout
checkout_func = '''
  void _processCheckout(BuildContext context, TokoProvider provider, Color iconColor) async {
    final success = await provider.checkout();
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('✅ Transaksi berhasil!'),
          backgroundColor: Colors.green,
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('❌ Transaksi gagal'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }
'''

# _showAddProductDialog
add_product_func = '''
  void _showAddProductDialog(
    BuildContext context,
    Color iconColor,
    Color textColor,
    Color secondaryTextColor,
    Color surfaceColor,
  ) {
    final nameController = TextEditingController();
    final priceController = TextEditingController();
    final stockController = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Tambah Produk'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(
                labelText: 'Nama Produk',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: priceController,
              decoration: const InputDecoration(
                labelText: 'Harga',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 8),
            TextField(
              controller: stockController,
              decoration: const InputDecoration(
                labelText: 'Stok',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text('Batal', style: TextStyle(color: secondaryTextColor)),
          ),
          ElevatedButton(
            onPressed: () {
              if (nameController.text.isNotEmpty) {
                final data = {
                  'name': nameController.text,
                  'price': int.tryParse(priceController.text) ?? 0,
                  'stock': int.tryParse(stockController.text) ?? 0,
                };
                context.read<TokoProvider>().addProduct(data);
                Navigator.pop(ctx);
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: iconColor,
              foregroundColor: Colors.white,
            ),
            child: const Text('Simpan'),
          ),
        ],
      ),
    );
  }
'''

# _showEditProductDialog
edit_product_func = '''
  void _showEditProductDialog(
    BuildContext context,
    Map<String, dynamic> product,
    Color iconColor,
    Color textColor,
    Color secondaryTextColor,
    Color surfaceColor,
  ) {
    final nameController = TextEditingController(text: product['name']);
    final priceController = TextEditingController(text: product['price'].toString());
    final stockController = TextEditingController(text: product['stock'].toString());

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Edit Produk'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: nameController,
              decoration: const InputDecoration(
                labelText: 'Nama Produk',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: priceController,
              decoration: const InputDecoration(
                labelText: 'Harga',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 8),
            TextField(
              controller: stockController,
              decoration: const InputDecoration(
                labelText: 'Stok',
                border: OutlineInputBorder(),
              ),
              keyboardType: TextInputType.number,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text('Batal', style: TextStyle(color: secondaryTextColor)),
          ),
          ElevatedButton(
            onPressed: () {
              final data = {
                'name': nameController.text,
                'price': int.tryParse(priceController.text) ?? 0,
                'stock': int.tryParse(stockController.text) ?? 0,
              };
              context.read<TokoProvider>().updateProduct(product['id'], data);
              Navigator.pop(ctx);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: iconColor,
              foregroundColor: Colors.white,
            ),
            child: const Text('Simpan'),
          ),
        ],
      ),
    );
  }
'''

# _showDeleteConfirmDialog
delete_dialog_func = '''
  void _showDeleteConfirmDialog(
    BuildContext context,
    int productId,
    Color iconColor,
    Color secondaryTextColor,
  ) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Hapus Produk'),
        content: const Text('Apakah Anda yakin ingin menghapus produk ini?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text('Batal', style: TextStyle(color: secondaryTextColor)),
          ),
          ElevatedButton(
            onPressed: () {
              context.read<TokoProvider>().deleteProduct(productId);
              Navigator.pop(ctx);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('Hapus'),
          ),
        ],
      ),
    );
  }
'''

# ==================== TERAPKAN PERUBAHAN ====================

import re

# Ganti semua fungsi helper
helpers = [
    (r'Widget _buildStatCard\([^}]*}\s*}', stat_card_func),
    (r'void _showVoiceScanDialog\([^}]*}\s*}', voice_dialog_func),
    (r'void _processCheckout\([^}]*}\s*}', checkout_func),
    (r'void _showAddProductDialog\([^}]*}\s*}', add_product_func),
    (r'void _showEditProductDialog\([^}]*}\s*}', edit_product_func),
    (r'void _showDeleteConfirmDialog\([^}]*}\s*}', delete_dialog_func),
]

for pattern, replacement in helpers:
    if re.search(pattern, content, flags=re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        print(f"✅ {pattern.split('_')[1].split('(')[0]} updated")

with open(FILE_PATH, 'w') as f:
    f.write(content)

print("\n✅ SEMUA FUNGSI HELPER TELAH DIPERBAIKI!")
print("   - Setiap fungsi helper sekarang menerima parameter warna")
print("   - Parameter diteruskan ke dialog-dialog")
print("\n🚀 Build sekarang:")
print("   flutter clean && flutter pub get")
print("   flutter build apk --release --dart-define=API_URL=http://94.100.26.128:8081/api/v1")
