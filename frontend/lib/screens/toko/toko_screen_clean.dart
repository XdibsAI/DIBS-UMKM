import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/toko_provider.dart';
import '../../core/theme.dart';

class TokoScreen extends StatefulWidget {
  const TokoScreen({Key? key}) : super(key: key);

  @override
  State<TokoScreen> createState() => _TokoScreenState();
}

class _TokoScreenState extends State<TokoScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _searchController = TextEditingController();
  bool _isInitialized = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    
    // Load data setelah frame pertama
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _initializeData();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _initializeData() async {
    if (!_isInitialized) {
      final provider = context.read<TokoProvider>();
      await provider.loadDashboard();
      await provider.loadProducts();
      setState(() {
        _isInitialized = true;
      });
    }
  }

  // Helper untuk warna dinamis
  Color _getBackgroundColor(BuildContext context) {
    return Theme.of(context).brightness == Brightness.dark 
        ? const Color(0xFF0A0A0F) 
        : const Color(0xFFF5F5F5);
  }

  Color _getSurfaceColor(BuildContext context) {
    return Theme.of(context).brightness == Brightness.dark 
        ? const Color(0xFF1A1A2E) 
        : Colors.white;
  }

  Color _getTextColor(BuildContext context) {
    return Theme.of(context).brightness == Brightness.dark 
        ? Colors.white 
        : Colors.black87;
  }

  Color _getSecondaryTextColor(BuildContext context) {
    return Theme.of(context).brightness == Brightness.dark 
        ? Colors.grey.shade400 
        : Colors.grey.shade600;
  }

  Color _getIconColor(BuildContext context) {
    return const Color(0xFF00FFFF);
  }

  @override
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
        bottom: const TabBar(
          tabs: [
            Tab(text: 'Dashboard', icon: Icon(Icons.dashboard)),
            Tab(text: 'Kasir', icon: Icon(Icons.point_of_sale)),
            Tab(text: 'Produk', icon: Icon(Icons.inventory)),
          ],
        ),
      ),
      body: Consumer<TokoProvider>(
        builder: (context, provider, child) {
          return TabBarView(
            children: [
              _buildDashboard(context),
    // Dashboard called
              _buildKasir(context),
    // Kasir called
              _buildProduk(context),
    // Produk called
            ],
          );
        },
      ),
    );
  }

  // 📊 Dashboard Tab
  Widget _buildDashboard(BuildContext context) {
    return Consumer<TokoProvider>(
      builder: (context, provider, child) {
        // Tampilkan loading jika masih loading
        if (provider.isLoading) {
          return Center(
            child: CircularProgressIndicator(color: iconColor),
          );
        }

        // Ambil data dashboard dengan safe access
        final dashboard = provider.dashboard ?? {};
        final todaySales = dashboard['today_sales'] ?? 0;
        final todayTransactions = dashboard['today_transactions'] ?? 0;
        final totalProducts = dashboard['total_products'] ?? 0;
        final lowStock = dashboard['low_stock'] ?? 0;
        final recentSales = provider.recentSales ?? [];

        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Stats Cards - 2 baris
              Row(
                children: [
                  Expanded(
                    child: _buildStatCard(
                      title: 'Penjualan Hari Ini',
                      value: 'Rp ${_formatNumber(todaySales)}',
                      icon: Icons.attach_money,
                      color: Colors.green,
                      textColor: textColor,
                      secondaryTextColor: secondaryTextColor,
                      surfaceColor: surfaceColor,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildStatCard(
                      title: 'Transaksi',
                      value: _formatNumber(todayTransactions),
                      icon: Icons.receipt,
                      color: Colors.blue,
                      textColor: textColor,
                      secondaryTextColor: secondaryTextColor,
                      surfaceColor: surfaceColor,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Expanded(
                    child: _buildStatCard(
                      title: 'Total Produk',
                      value: _formatNumber(totalProducts),
                      icon: Icons.inventory_2,
                      color: Colors.orange,
                      textColor: textColor,
                      secondaryTextColor: secondaryTextColor,
                      surfaceColor: surfaceColor,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildStatCard(
                      title: 'Stok Menipis',
                      value: _formatNumber(lowStock),
                      icon: Icons.warning,
                      color: Colors.red,
                      textColor: textColor,
                      secondaryTextColor: secondaryTextColor,
                      surfaceColor: surfaceColor,
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 24),
              
              // Recent Sales Header
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Transaksi Terakhir',
                    style: TextStyle(
                      color: textColor,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  TextButton.icon(
                    onPressed: () {
                      // Navigasi ke laporan lengkap
                    },
                    icon: Icon(Icons.visibility, color: iconColor, size: 16),
                    label: Text(
                      'Lihat Semua',
                      style: TextStyle(color: iconColor, fontSize: 12),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              
              // Recent Sales List
              if (recentSales.isNotEmpty)
                ...recentSales.take(5).map((sale) => _buildSaleItem(
                  context,
                  sale,
                  iconColor,
                  textColor,
                  secondaryTextColor,
                  surfaceColor,
                ))
              else
                Container(
                  padding: const EdgeInsets.all(32),
                  decoration: BoxDecoration(
                    color: surfaceColor,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: secondaryTextColor.withOpacity(0.2)),
                  ),
                  child: Column(
                    children: [
                      Icon(Icons.receipt_long, size: 48, color: secondaryTextColor),
                      const SizedBox(height: 12),
                      Text(
                        'Belum ada transaksi',
                        style: TextStyle(color: secondaryTextColor, fontSize: 16),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Transaksi akan muncul di sini',
                        style: TextStyle(color: secondaryTextColor, fontSize: 12),
                      ),
                    ],
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required IconData icon,
    required Color color,
    required Color textColor,
    required Color secondaryTextColor,
    required Color surfaceColor,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: surfaceColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Icon(icon, color: color, size: 28),
              Text(
                value,
                style: TextStyle(
                  color: color,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            title,
            style: TextStyle(color: secondaryTextColor, fontSize: 12),
          ),
        ],
      ),
    );
  }

  Widget _buildSaleItem(
    BuildContext context,
    Map<String, dynamic> sale,
    Color iconColor,
    Color textColor,
    Color secondaryTextColor,
    Color surfaceColor,
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: surfaceColor,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: secondaryTextColor.withOpacity(0.2)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: iconColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(Icons.shopping_bag, color: iconColor, size: 16),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  sale['product_name'] ?? 'Produk',
                  style: TextStyle(color: textColor, fontWeight: FontWeight.w500),
                ),
                Text(
                  _formatDate(sale['created_at']),
                  style: TextStyle(color: secondaryTextColor, fontSize: 11),
                ),
              ],
            ),
          ),
          Text(
            'Rp ${_formatNumber(sale['total'] ?? 0)}',
            style: TextStyle(
              color: iconColor,
              fontWeight: FontWeight.bold,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  // 🛒 Kasir Tab
  Widget _buildKasir(BuildContext context) {
    return Consumer<TokoProvider>(
      builder: (context, provider, child) {
        final cartItems = provider.cartItems ?? [];
        final cartTotal = provider.cartTotal ?? 0;

        return Column(
          children: [
            // Voice Scan Button
            Padding(
              padding: const EdgeInsets.all(16),
              child: ElevatedButton.icon(
                onPressed: () => _showVoiceScanDialog(context, iconColor),
                icon: const Icon(Icons.mic, color: Colors.black),
                label: const Text(
                  '🎤 Scan Suara Kasir',
                  style: TextStyle(color: Colors.black, fontSize: 16),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: iconColor,
                  minimumSize: const Size(double.infinity, 56),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),

            // Cart Items
            Expanded(
              child: cartItems.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.shopping_cart_outlined, size: 80, color: secondaryTextColor),
                          const SizedBox(height: 16),
                          Text(
                            'Keranjang Kosong',
                            style: TextStyle(color: secondaryTextColor, fontSize: 18),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Gunakan scan suara untuk menambah produk',
                            style: TextStyle(color: secondaryTextColor, fontSize: 14),
                          ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      itemCount: cartItems.length,
                      itemBuilder: (context, index) {
                        final item = cartItems[index];
                        return _buildCartItem(
                          context,
                          item,
                          provider,
                          iconColor,
                          textColor,
                          secondaryTextColor,
                          surfaceColor,
                        );
                      },
                    ),
            ),

            // Total & Checkout
            if (cartItems.isNotEmpty)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: surfaceColor,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, -2),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Total',
                          style: TextStyle(
                            color: textColor,
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          'Rp ${_formatNumber(cartTotal)}',
                          style: TextStyle(
                            color: iconColor,
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: () => _processCheckout(context, provider, iconColor),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: iconColor,
                          foregroundColor: Colors.black,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                        ),
                        child: const Text(
                          'Proses Pembayaran',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
          ],
        );
      },
    );
  }

  Widget _buildCartItem(
    BuildContext context,
    Map<String, dynamic> item,
    TokoProvider provider,
    Color iconColor,
    Color textColor,
    Color secondaryTextColor,
    Color surfaceColor,
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: surfaceColor,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: secondaryTextColor.withOpacity(0.2)),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item['name'] ?? 'Produk',
                  style: TextStyle(color: textColor, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Text(
                  'Rp ${_formatNumber(item['price'])} x ${item['quantity']}',
                  style: TextStyle(color: secondaryTextColor, fontSize: 12),
                ),
              ],
            ),
          ),
          Row(
            children: [
              IconButton(
                icon: const Icon(Icons.remove_circle_outline, color: Colors.red),
                onPressed: () => provider.decrementCartItem(item['id']),
                constraints: const BoxConstraints(),
                padding: const EdgeInsets.all(4),
                iconSize: 20,
              ),
              Container(
                width: 30,
                alignment: Alignment.center,
                child: Text(
                  '${item['quantity']}',
                  style: TextStyle(color: textColor, fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ),
              IconButton(
                icon: Icon(Icons.add_circle_outline, color: iconColor),
                onPressed: () => provider.incrementCartItem(item['id']),
                constraints: const BoxConstraints(),
                padding: const EdgeInsets.all(4),
                iconSize: 20,
              ),
            ],
          ),
          const SizedBox(width: 8),
          Text(
            'Rp ${_formatNumber(item['subtotal'])}',
            style: TextStyle(color: iconColor, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  // 📦 Produk Tab
  Widget _buildProduk(BuildContext context) {
    return Consumer<TokoProvider>(
      builder: (context, provider, child) {
        final products = provider.products ?? [];
        final isLoading = provider.isLoading;

        return Column(
          children: [
            // Search & Add Button
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(
                    child: Container(
                      decoration: BoxDecoration(
                        color: surfaceColor,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: secondaryTextColor.withOpacity(0.3)),
                      ),
                      child: TextField(
                        controller: _searchController,
                        decoration: InputDecoration(
                          hintText: 'Cari produk...',
                          hintStyle: TextStyle(color: secondaryTextColor),
                          prefixIcon: Icon(Icons.search, color: iconColor),
                          border: InputBorder.none,
                          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                        ),
                        style: TextStyle(color: textColor),
                        onChanged: (value) => provider.searchProducts(value),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  FloatingActionButton(
                    onPressed: () => _showAddProductDialog(
                      context, 
                      iconColor, 
                      textColor, 
                      secondaryTextColor, 
                      surfaceColor
                    ),
                    backgroundColor: iconColor,
                    child: const Icon(Icons.add, color: Colors.black),
                  ),
                ],
              ),
            ),

            // Product List
            Expanded(
              child: isLoading
                  ? Center(child: CircularProgressIndicator(color: iconColor))
                  : products.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.inventory_2_outlined, size: 80, color: secondaryTextColor),
                              const SizedBox(height: 16),
                              Text(
                                'Belum ada produk',
                                style: TextStyle(color: secondaryTextColor, fontSize: 18),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                'Tambahkan produk dengan tombol +',
                                style: TextStyle(color: secondaryTextColor, fontSize: 14),
                              ),
                            ],
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          itemCount: products.length,
                          itemBuilder: (context, index) {
                            final product = products[index];
                            return _buildProductItem(
                              context,
                              product,
                              provider,
                              iconColor,
                              textColor,
                              secondaryTextColor,
                              surfaceColor,
                            );
                          },
                        ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildProductItem(
    BuildContext context,
    Map<String, dynamic> product,
    TokoProvider provider,
    Color iconColor,
    Color textColor,
    Color secondaryTextColor,
    Color surfaceColor,
  ) {
    final stock = product['stock'] ?? 0;
    final isLowStock = stock < 10;

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: surfaceColor,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isLowStock ? Colors.red.withOpacity(0.5) : secondaryTextColor.withOpacity(0.2),
        ),
      ),
      child: Row(
        children: [
          Container(
            width: 50,
            height: 50,
            decoration: BoxDecoration(
              color: iconColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(Icons.inventory_2, color: iconColor),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  product['name'] ?? 'Produk',
                  style: TextStyle(color: textColor, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Text(
                  'Rp ${_formatNumber(product['price'])}',
                  style: TextStyle(color: iconColor, fontWeight: FontWeight.w500),
                ),
                const SizedBox(height: 2),
                Row(
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: isLowStock ? Colors.red : Colors.green,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 4),
                    Text(
                      'Stok: $stock',
                      style: TextStyle(
                        color: isLowStock ? Colors.red : secondaryTextColor,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          PopupMenuButton<String>(
            icon: Icon(Icons.more_vert, color: secondaryTextColor),
            color: surfaceColor,
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'edit',
                child: Row(
                  children: [
                    Icon(Icons.edit, color: Colors.blue, size: 18),
                    const SizedBox(width: 8),
                    Text('Edit', style: TextStyle(color: textColor)),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'delete',
                child: Row(
                  children: [
                    Icon(Icons.delete, color: Colors.red, size: 18),
                    const SizedBox(width: 8),
                    Text('Hapus', style: TextStyle(color: textColor)),
                  ],
                ),
              ),
            ],
            onSelected: (value) {
              if (value == 'edit') {
                _showEditProductDialog(
                  context, 
                  product, 
                  iconColor, 
                  textColor, 
                  secondaryTextColor, 
                  surfaceColor
                );
              } else if (value == 'delete') {
                _deleteProduct(context, product['id'], provider, iconColor, textColor);
              }
            },
          ),
        ],
      ),
