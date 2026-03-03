#!/usr/bin/env python3
"""
FIX FINAL - Tulis ulang SEMUA fungsi dengan parameter yang benar
"""
import shutil
from pathlib import Path

FILE_PATH = Path("lib/screens/toko/toko_screen.dart")
BACKUP_PATH = FILE_PATH.with_suffix(".dart.bak.finalfix")

shutil.copy2(FILE_PATH, BACKUP_PATH)
print(f"✅ Backup dibuat: {BACKUP_PATH}")

with open(FILE_PATH, 'r') as f:
    lines = f.readlines()

# Cari baris pemanggilan TabBarView untuk melihat parameter yang dikirim
tabbarview_line = None
for i, line in enumerate(lines):
    if 'TabBarView' in line and '_buildDashboard' in line:
        tabbarview_line = i
        print(f"✅ Found TabBarView at line {i+1}")
        break

if tabbarview_line:
    # Ekstrak parameter dari pemanggilan
    import re
    match = re.search(r'_buildDashboard\(([^)]+)\)', lines[tabbarview_line])
    if match:
        params = match.group(1)
        print(f"📝 Parameters: {params}")

print("\n🔧 Menulis ulang semua fungsi...")

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
                                  icon: Icon(Icons.remove_circle_outline, color: Colors.red),
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
                                  icon: Icon(Icons.add_circle_outline, color: Colors.green),
                                  onPressed: () => provider.incrementCartItem(item['id']),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
            ),
            
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

# Baca file sebagai string untuk memudahkan penggantian
with open(FILE_PATH, 'r') as f:
    content = f.read()

# Ganti fungsi-fungsi yang ada
import re

# Hapus fungsi _buildDashboard yang lama dan ganti dengan yang baru
dashboard_pattern = r'Widget _buildDashboard\([^}]*}\s*}'
if re.search(dashboard_pattern, content, flags=re.DOTALL):
    content = re.sub(dashboard_pattern, dashboard_func, content, flags=re.DOTALL)
    print("✅ _buildDashboard updated")

# Ganti _buildKasir
kasir_pattern = r'Widget _buildKasir\([^}]*}\s*}'
if re.search(kasir_pattern, content, flags=re.DOTALL):
    content = re.sub(kasir_pattern, kasir_func, content, flags=re.DOTALL)
    print("✅ _buildKasir updated")

# Ganti _buildProduk
produk_pattern = r'Widget _buildProduk\([^}]*}\s*}'
if re.search(produk_pattern, content, flags=re.DOTALL):
    content = re.sub(produk_pattern, produk_func, content, flags=re.DOTALL)
    print("✅ _buildProduk updated")

# Ganti _buildStatCard
stat_card_pattern = r'Widget _buildStatCard\([^}]*}\s*}'
if re.search(stat_card_pattern, content, flags=re.DOTALL):
    content = re.sub(stat_card_pattern, stat_card_func, content, flags=re.DOTALL)
    print("✅ _buildStatCard updated")

# Tulis kembali
with open(FILE_PATH, 'w') as f:
    f.write(content)

print("\n✅ SEMUA FUNGSI TELAH DIPERBAIKI!")
print("   - Setiap fungsi sekarang menerima 5 parameter warna")
print("   - Setiap fungsi menggunakan parameter tersebut")
print("\n🚀 Build sekarang:")
print("   flutter clean && flutter pub get")
print("   flutter build apk --release --dart-define=API_URL=http://94.100.26.128:8081/api/v1")
