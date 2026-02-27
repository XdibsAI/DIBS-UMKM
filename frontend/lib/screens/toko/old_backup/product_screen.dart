import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/toko_provider.dart';
import '../../providers/auth_provider.dart';

class ProductScreen extends StatefulWidget {
  const ProductScreen({super.key});

  @override
  State<ProductScreen> createState() => _ProductScreenState();
}

class _ProductScreenState extends State<ProductScreen> {
  String? _selectedCategory;
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<TokoProvider>(context, listen: false).loadProducts();
    });
  }

  @override
  Widget build(BuildContext context) {
    final toko = Provider.of<TokoProvider>(context);
    final auth = Provider.of<AuthProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('PRODUK TOKO'),
        backgroundColor: const Color(0xFF050507),
        foregroundColor: const Color(0xFF00FFFF),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _showProductDialog(context),
          ),
        ],
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF0A0A0F), Color(0xFF050507)],
          ),
        ),
        child: Column(
          children: [
            // Search bar
            Padding(
              padding: const EdgeInsets.all(16),
              child: TextField(
                controller: _searchController,
                style: const TextStyle(color: Color(0xFFE0E0FF)),
                decoration: InputDecoration(
                  hintText: 'Cari produk...',
                  hintStyle: TextStyle(color: const Color(0xFF8888AA).withOpacity(0.5)),
                  prefixIcon: const Icon(Icons.search, color: Color(0xFF00FFFF)),
                  filled: true,
                  fillColor: const Color(0xFF12121A),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: const Color(0xFF00FFFF).withOpacity(0.3)),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: const Color(0xFF00FFFF).withOpacity(0.3)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: Color(0xFF00FFFF)),
                  ),
                ),
                onChanged: (value) {
                  // TODO: Implement search
                },
              ),
            ),

            // Product list
            Expanded(
              child: toko.isLoading
                  ? const Center(
                      child: CircularProgressIndicator(
                        valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF00FFFF)),
                      ),
                    )
                  : toko.products.isEmpty
                      ? _buildEmptyState()
                      : ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: toko.products.length,
                          itemBuilder: (context, index) {
                            final product = toko.products[index];
                            return _buildProductCard(product);
                          },
                        ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(
                color: const Color(0xFF00FFFF).withOpacity(0.3),
                width: 2,
              ),
            ),
            child: const Icon(
              Icons.inventory_2_outlined,
              size: 64,
              color: Color(0xFF00FFFF),
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'BELUM ADA PRODUK',
            style: TextStyle(
              color: Color(0xFF00FFFF),
              fontSize: 18,
              fontWeight: FontWeight.bold,
              letterSpacing: 2,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Tambahkan produk pertama Anda',
            style: TextStyle(
              color: const Color(0xFF8888AA).withOpacity(0.8),
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => _showProductDialog(context),
            icon: const Icon(Icons.add, color: Color(0xFF0A0A0F)),
            label: const Text(
              'TAMBAH PRODUK',
              style: TextStyle(color: Color(0xFF0A0A0F)),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF00FFFF),
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProductCard(Map<String, dynamic> product) {
    final isLowStock = product['stock'] <= (product['min_stock'] ?? 0);
    
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF12121A), Color(0xFF0A0A0F)],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isLowStock 
              ? Colors.red.withOpacity(0.3)
              : const Color(0xFF00FFFF).withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: const Color(0xFF00FFFF).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    Icons.shopping_bag_outlined,
                    color: isLowStock ? Colors.red : const Color(0xFF00FFFF),
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        product['name'] ?? 'Produk',
                        style: const TextStyle(
                          color: Color(0xFFE0E0FF),
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      if (product['category'] != null)
                        Text(
                          product['category'],
                          style: TextStyle(
                            color: const Color(0xFF8888AA).withOpacity(0.8),
                            fontSize: 12,
                          ),
                        ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: isLowStock 
                        ? Colors.red.withOpacity(0.15)
                        : const Color(0xFF00FFFF).withOpacity(0.15),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: isLowStock 
                          ? Colors.red.withOpacity(0.3)
                          : const Color(0xFF00FFFF).withOpacity(0.3),
                    ),
                  ),
                  child: Text(
                    'Stok: ${product['stock'] ?? 0}',
                    style: TextStyle(
                      fontSize: 12,
                      color: isLowStock ? Colors.red : const Color(0xFF00FFFF),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _buildInfoChip(
                  icon: Icons.attach_money,
                  label: 'Rp ${product['price']?.toStringAsFixed(0) ?? '0'}',
                  color: const Color(0xFF00FFAA),
                ),
                const SizedBox(width: 8),
                if (product['barcode'] != null)
                  _buildInfoChip(
                    icon: Icons.qr_code,
                    label: product['barcode'],
                    color: const Color(0xFF9D4DFF),
                  ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                IconButton(
                  icon: const Icon(Icons.edit, color: Color(0xFF00FFFF)),
                  onPressed: () => _showProductDialog(context, product: product),
                ),
                IconButton(
                  icon: const Icon(Icons.delete, color: Colors.red),
                  onPressed: () => _deleteProduct(context, product),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoChip({
    required IconData icon,
    required String label,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: color, size: 14),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  void _showProductDialog(BuildContext context, {Map<String, dynamic>? product}) {
    final isEditing = product != null;
    final nameController = TextEditingController(text: product?['name']);
    final priceController = TextEditingController(
      text: product?['price']?.toString(),
    );
    final stockController = TextEditingController(
      text: product?['stock']?.toString(),
    );
    final minStockController = TextEditingController(
      text: product?['min_stock']?.toString() ?? '0',
    );
    final categoryController = TextEditingController(text: product?['category']);
    final barcodeController = TextEditingController(text: product?['barcode']);

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF12121A),
        title: Text(
          isEditing ? 'EDIT PRODUK' : 'TAMBAH PRODUK',
          style: const TextStyle(
            color: Color(0xFF00FFFF),
            fontWeight: FontWeight.bold,
          ),
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                style: const TextStyle(color: Color(0xFFE0E0FF)),
                decoration: InputDecoration(
                  labelText: 'Nama Produk',
                  labelStyle: const TextStyle(color: Color(0xFF8888AA)),
                  filled: true,
                  fillColor: const Color(0xFF050507),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: const Color(0xFF00FFFF).withOpacity(0.3)),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: priceController,
                style: const TextStyle(color: Color(0xFFE0E0FF)),
                keyboardType: TextInputType.number,
                decoration: InputDecoration(
                  labelText: 'Harga',
                  prefixText: 'Rp ',
                  labelStyle: const TextStyle(color: Color(0xFF8888AA)),
                  filled: true,
                  fillColor: const Color(0xFF050507),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: const Color(0xFF00FFFF).withOpacity(0.3)),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: stockController,
                      style: const TextStyle(color: Color(0xFFE0E0FF)),
                      keyboardType: TextInputType.number,
                      decoration: InputDecoration(
                        labelText: 'Stok',
                        labelStyle: const TextStyle(color: Color(0xFF8888AA)),
                        filled: true,
                        fillColor: const Color(0xFF050507),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(color: const Color(0xFF00FFFF).withOpacity(0.3)),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextField(
                      controller: minStockController,
                      style: const TextStyle(color: Color(0xFFE0E0FF)),
                      keyboardType: TextInputType.number,
                      decoration: InputDecoration(
                        labelText: 'Min Stok',
                        labelStyle: const TextStyle(color: Color(0xFF8888AA)),
                        filled: true,
                        fillColor: const Color(0xFF050507),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide(color: const Color(0xFF00FFFF).withOpacity(0.3)),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              TextField(
                controller: categoryController,
                style: const TextStyle(color: Color(0xFFE0E0FF)),
                decoration: InputDecoration(
                  labelText: 'Kategori',
                  labelStyle: const TextStyle(color: Color(0xFF8888AA)),
                  filled: true,
                  fillColor: const Color(0xFF050507),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: const Color(0xFF00FFFF).withOpacity(0.3)),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: barcodeController,
                style: const TextStyle(color: Color(0xFFE0E0FF)),
                decoration: InputDecoration(
                  labelText: 'Barcode',
                  labelStyle: const TextStyle(color: Color(0xFF8888AA)),
                  filled: true,
                  fillColor: const Color(0xFF050507),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide(color: const Color(0xFF00FFFF).withOpacity(0.3)),
                  ),
                ),
              ),
            ],
          ),
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(color: Color(0xFF00FFFF), width: 0.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('BATAL', style: TextStyle(color: Color(0xFF8888AA))),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(ctx);
              
              final data = {
                'name': nameController.text,
                'price': double.tryParse(priceController.text) ?? 0,
                'stock': int.tryParse(stockController.text) ?? 0,
                'min_stock': int.tryParse(minStockController.text) ?? 0,
                'category': categoryController.text.isEmpty ? null : categoryController.text,
                'barcode': barcodeController.text.isEmpty ? null : barcodeController.text,
              };

              final toko = Provider.of<TokoProvider>(context, listen: false);
              
              bool success;
              if (isEditing) {
                success = await toko.updateProduct(product!['id'], data);
              } else {
                final result = await toko.createProduct(data);
                success = result != null;
              }

              if (success && mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(isEditing ? '✅ Produk diupdate' : '✅ Produk ditambahkan'),
                    backgroundColor: const Color(0xFF12121A),
                    behavior: SnackBarBehavior.floating,
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF00FFFF),
              foregroundColor: const Color(0xFF0A0A0F),
            ),
            child: Text(isEditing ? 'UPDATE' : 'SIMPAN'),
          ),
        ],
      ),
    );
  }

  void _deleteProduct(BuildContext context, Map<String, dynamic> product) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF12121A),
        title: const Text(
          'HAPUS PRODUK',
          style: TextStyle(color: Color(0xFFFF44AA)),
        ),
        content: Text(
          'Yakin ingin menghapus "${product['name']}"?',
          style: const TextStyle(color: Color(0xFFE0E0FF)),
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(color: Color(0xFFFF44AA), width: 0.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('BATAL', style: TextStyle(color: Color(0xFF8888AA))),
          ),
          TextButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: TextButton.styleFrom(foregroundColor: const Color(0xFFFF44AA)),
            child: const Text('HAPUS'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      final toko = Provider.of<TokoProvider>(context, listen: false);
      final success = await toko.deleteProduct(product['id']);
      
      if (success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('✅ Produk dihapus'),
            backgroundColor: Color(0xFF12121A),
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }
}
