#!/usr/bin/env python3
"""
FIX FINAL - Tulis ulang seluruh fungsi dengan parameter yang benar
"""
import shutil
from pathlib import Path

FILE_PATH = Path("lib/screens/toko/toko_screen.dart")
BACKUP_PATH = FILE_PATH.with_suffix(".dart.bak.final2")

shutil.copy2(FILE_PATH, BACKUP_PATH)
print(f"✅ Backup dibuat: {BACKUP_PATH}")

with open(FILE_PATH, 'r') as f:
    content = f.read()

# Fungsi _buildDashboard yang benar dengan parameter
dashboard_func = '''
  Widget _buildDashboard(
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
          return Center(
            child: CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(iconColor),
            ),
          );
        }
        if (provider.error != null) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.error_outline, size: 48, color: Colors.red),
                const SizedBox(height: 16),
                Text(
                  'Error: ${provider.error}',
                  style: TextStyle(color: textColor),
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => provider.loadDashboard(),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: iconColor,
                    foregroundColor: Colors.white,
                  ),
                  child: const Text('Coba Lagi'),
                ),
              ],
            ),
          );
        }
        
        // Dashboard content
        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Dashboard Toko',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: textColor,
                ),
              ),
              const SizedBox(height: 20),
              // Stats cards
              GridView.count(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                crossAxisCount: 2,
                mainAxisSpacing: 10,
                crossAxisSpacing: 10,
                children: [
                  _buildStatCard(
                    'Total Penjualan Hari Ini',
                    'Rp ${provider.dashboard['today_sales'] ?? 0}',
                    Icons.today,
                    iconColor,
                    surfaceColor,
                  ),
                  _buildStatCard(
                    'Transaksi Hari Ini',
                    '${provider.dashboard['today_transactions'] ?? 0}',
                    Icons.receipt,
                    iconColor,
                    surfaceColor,
                  ),
                  _buildStatCard(
                    'Total Produk',
                    '${provider.dashboard['total_products'] ?? 0}',
                    Icons.inventory,
                    iconColor,
                    surfaceColor,
                  ),
                  _buildStatCard(
                    'Stok Menipis',
                    '${provider.dashboard['low_stock'] ?? 0}',
                    Icons.warning,
                    iconColor,
                    surfaceColor,
                  ),
                ],
              ),
              const SizedBox(height: 20),
              Text(
                'Transaksi Terbaru',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: textColor,
                ),
              ),
              const SizedBox(height: 10),
              ...provider.recentSales.map((sale) => Card(
                margin: const EdgeInsets.only(bottom: 8),
                color: surfaceColor,
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: iconColor.withOpacity(0.2),
                    child: Icon(Icons.receipt, color: iconColor, size: 20),
                  ),
                  title: Text(
                    sale['invoice_number'] ?? 'TRX-${sale['id']}',
                    style: TextStyle(color: textColor),
                  ),
                  subtitle: Text(
                    '${sale['items']?.length ?? 0} item',
                    style: TextStyle(color: secondaryTextColor),
                  ),
                  trailing: Text(
                    'Rp ${sale['total'] ?? 0}',
                    style: TextStyle(
                      color: iconColor,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              )),
            ],
          ),
        );
      },
    );
  }
'''

kasir_func = '''
  Widget _buildKasir(
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
          return Center(
            child: CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(iconColor),
            ),
          );
        }
        
        return Column(
          children: [
            // Voice scan button
            Padding(
              padding: const EdgeInsets.all(16),
              child: ElevatedButton.icon(
                onPressed: () => _showVoiceScanDialog(context, iconColor),
                icon: const Icon(Icons.mic, size: 24),
                label: const Text(
                  'Scan Suara',
                  style: TextStyle(fontSize: 16),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: iconColor,
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 50),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
              ),
            ),
            
            // Cart items
            Expanded(
              child: provider.cartItems.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.shopping_cart_outlined,
                            size: 80,
                            color: secondaryTextColor,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'Keranjang belanja kosong',
                            style: TextStyle(
                              color: secondaryTextColor,
                              fontSize: 18,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Gunakan tombol "Scan Suara" untuk memulai',
                            style: TextStyle(
                              color: secondaryTextColor,
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(8),
                      itemCount: provider.cartItems.length,
                      itemBuilder: (context, index) {
                        final item = provider.cartItems[index];
                        return Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          color: surfaceColor,
                          child: ListTile(
                            leading: CircleAvatar(
                              backgroundColor: iconColor.withOpacity(0.2),
                              child: Text(
                                '${item['quantity']}x',
                                style: TextStyle(
                                  color: iconColor,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            title: Text(
                              item['name'] ?? '',
                              style: TextStyle(color: textColor),
                            ),
                            subtitle: Text(
                              'Rp ${item['price']} per item',
                              style: TextStyle(color: secondaryTextColor),
                            ),
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                IconButton(
                                  icon: Icon(Icons.remove_circle_outline,
                                      color: Colors.red),
                                  onPressed: () => provider.decrementCartItem(item['id']),
                                ),
                                Text(
                                  'Rp ${item['subtotal']}',
                                  style: TextStyle(
                                    color: iconColor,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                                IconButton(
                                  icon: Icon(Icons.add_circle_outline,
                                      color: Colors.green),
                                  onPressed: () => provider.incrementCartItem(item['id']),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
            ),
            
            // Total and checkout
            if (provider.cartItems.isNotEmpty)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: surfaceColor,
                  border: Border(
                    top: BorderSide(color: secondaryTextColor.withOpacity(0.3)),
                  ),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Total:',
                          style: TextStyle(
                            fontSize: 14,
                            color: secondaryTextColor,
                          ),
                        ),
                        Text(
                          'Rp ${provider.cartTotal}',
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: iconColor,
                          ),
                        ),
                      ],
                    ),
                    ElevatedButton(
                      onPressed: () => _processCheckout(context, provider, iconColor),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green,
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 30,
                          vertical: 15,
                        ),
                      ),
                      child: const Text('Checkout'),
                    ),
                  ],
                ),
              ),
          ],
        );
      },
    );
  }
'''

produk_func = '''
  Widget _buildProduk(
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
          return Center(
            child: CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(iconColor),
            ),
          );
        }
        
        return Column(
          children: [
            // Search bar
            Padding(
              padding: const EdgeInsets.all(16),
              child: TextField(
                onChanged: provider.searchProducts,
                decoration: InputDecoration(
                  hintText: 'Cari produk...',
                  hintStyle: TextStyle(color: secondaryTextColor),
                  prefixIcon: Icon(Icons.search, color: iconColor),
                  filled: true,
                  fillColor: surfaceColor,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide.none,
                  ),
                ),
              ),
            ),
            
            // Add product button
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: ElevatedButton.icon(
                onPressed: () => _showAddProductDialog(
                  context, iconColor, textColor, secondaryTextColor, surfaceColor,
                ),
                icon: const Icon(Icons.add),
                label: const Text('Tambah Produk'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: iconColor,
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 45),
                ),
              ),
            ),
            
            const SizedBox(height: 8),
            
            // Product list
            Expanded(
              child: provider.products.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.inventory_outlined,
                            size: 80,
                            color: secondaryTextColor,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'Belum ada produk',
                            style: TextStyle(
                              color: secondaryTextColor,
                              fontSize: 18,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Tambahkan produk baru',
                            style: TextStyle(
                              color: secondaryTextColor,
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(8),
                      itemCount: provider.products.length,
                      itemBuilder: (context, index) {
                        final product = provider.products[index];
                        return Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          color: surfaceColor,
                          child: ListTile(
                            leading: CircleAvatar(
                              backgroundColor: iconColor.withOpacity(0.2),
                              child: Text(
                                '${product['stock'] ?? 0}',
                                style: TextStyle(
                                  color: iconColor,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                ),
                              ),
                            ),
                            title: Text(
                              product['name'] ?? '',
                              style: TextStyle(color: textColor),
                            ),
                            subtitle: Text(
                              'Rp ${product['price'] ?? 0}',
                              style: TextStyle(color: secondaryTextColor),
                            ),
                            trailing: PopupMenuButton(
                              icon: Icon(Icons.more_vert, color: iconColor),
                              itemBuilder: (context) => [
                                PopupMenuItem(
                                  child: const ListTile(
                                    leading: Icon(Icons.edit),
                                    title: Text('Edit'),
                                  ),
                                  onTap: () => _showEditProductDialog(
                                    context,
                                    product,
                                    iconColor,
                                    textColor,
                                    secondaryTextColor,
                                    surfaceColor,
                                  ),
                                ),
                                PopupMenuItem(
                                  child: const ListTile(
                                    leading: Icon(Icons.delete, color: Colors.red),
                                    title: Text('Hapus', style: TextStyle(color: Colors.red)),
                                  ),
                                  onTap: () => _showDeleteConfirmDialog(
                                    context,
                                    product['id'],
                                    iconColor,
                                    secondaryTextColor,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        );
      },
    );
  }
'''

# Ganti fungsi-fungsi yang ada
import re

# Hapus semua fungsi yang ada
content = re.sub(r'Widget _buildDashboard\([^}]*}\s*}', dashboard_func, content, flags=re.DOTALL)
content = re.sub(r'Widget _buildKasir\([^}]*}\s*}', kasir_func, content, flags=re.DOTALL)
content = re.sub(r'Widget _buildProduk\([^}]*}\s*}', produk_func, content, flags=re.DOTALL)

with open(FILE_PATH, 'w') as f:
    f.write(content)

print("✅ Semua fungsi telah ditulis ulang dengan parameter yang benar!")
print("\n📝 Perubahan:")
print("   - Setiap fungsi sekarang menerima 5 parameter warna")
print("   - Setiap fungsi menggunakan parameter tersebut")
print("   - Loading indicator pakai iconColor")
print("   - Text menggunakan textColor/secondaryTextColor")
print("   - Cards menggunakan surfaceColor")
print("\n🚀 Build sekarang:")
print("   flutter clean && flutter pub get")
print("   flutter build apk --release --dart-define=API_URL=http://94.100.26.128:8081/api/v1")
