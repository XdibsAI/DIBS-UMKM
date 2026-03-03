#!/usr/bin/env python3
"""
Fix corrupt file - tulis ulang bagian akhir dengan fungsi helper yang benar
"""
import shutil
from pathlib import Path

CLEAN_FILE = Path("lib/screens/toko/toko_screen_clean.dart")
FINAL_FILE = Path("lib/screens/toko/toko_screen.dart")

# Backup final
shutil.copy2(FINAL_FILE, FINAL_FILE.with_suffix(".dart.bak.corrupt2"))

with open(CLEAN_FILE, 'r') as f:
    clean_content = f.read()

# Fungsi helper yang benar (tanpa const yang salah)
helpers = '''

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

  void _showVoiceScanDialog(BuildContext context, Color iconColor) {
    showDialog(
      context: context,
      builder: (BuildContext ctx) {
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
          actions: <Widget>[
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

  void _processCheckout(BuildContext context, TokoProvider provider, Color iconColor) async {
    final success = await provider.checkout();
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ Transaksi berhasil!'),
          backgroundColor: Colors.green,
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('❌ Transaksi gagal'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

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
      builder: (BuildContext ctx) {
        return AlertDialog(
          title: const Text('Tambah Produk'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
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
          actions: <Widget>[
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
        );
      },
    );
  }

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
      builder: (BuildContext ctx) {
        return AlertDialog(
          title: const Text('Edit Produk'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: <Widget>[
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
          actions: <Widget>[
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
        );
      },
    );
  }

  void _showDeleteConfirmDialog(
    BuildContext context,
    int productId,
    Color iconColor,
    Color secondaryTextColor,
  ) {
    showDialog(
      context: context,
      builder: (BuildContext ctx) {
        return AlertDialog(
          title: const Text('Hapus Produk'),
          content: const Text('Apakah Anda yakin ingin menghapus produk ini?'),
          actions: <Widget>[
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
        );
      },
    );
  }
'''

# Gabungkan clean_content + helpers
final_content = clean_content + helpers + '\n}'

with open(FINAL_FILE, 'w') as f:
    f.write(final_content)

print("✅ File telah diperbaiki!")
print("   - Bagian awal file dipertahankan")
print("   - Fungsi helper ditulis ulang dengan benar")
print("\n🚀 Build sekarang:")
print("   flutter clean && flutter pub get")
print("   flutter build apk --release --dart-define=API_URL=http://94.100.26.128:8081/api/v1")
