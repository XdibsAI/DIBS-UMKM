import 'voice_scan_dialog.dart';
import 'barcode_scanner_screen.dart';
import '../../services/api_service.dart';
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
    _tabController.addListener(() {
      if (!_tabController.indexIsChanging) {
        // Jika pindah ke tab Dashboard (index 0), refresh data
        if (_tabController.index == 0) {
          context.read<TokoProvider>().loadDashboard();
        }
      }
    });
    
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
  
  
  
  void _openVoiceScanner() async {
    final result = await showModalBottomSheet<String>(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => const VoiceScanDialog(),
    );
    
    if (result != null && result.isNotEmpty) {
      // Kirim ke Provider untuk diproses masuk keranjang
      final provider = Provider.of<TokoProvider>(context, listen: false);
      provider.processVoiceCommand(result);
      
      // Feedback visual di layar
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("Dibs mendeteksi: $result"), 
          backgroundColor: const Color(0xFF00FFFF),
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
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
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: iconColor,
          labelColor: iconColor,
          unselectedLabelColor: secondaryTextColor,
          tabs: const [
            Tab(icon: Icon(Icons.dashboard), text: 'Dashboard'),
            Tab(icon: Icon(Icons.shopping_cart), text: 'Kasir'),
            Tab(icon: Icon(Icons.inventory), text: 'Produk'),
          ],
        ),
      ),
      body: _isInitialized 
          ? TabBarView(
              controller: _tabController,
              children: [
                _buildDashboard(context, iconColor, textColor, secondaryTextColor, surfaceColor),
                _buildKasir(context, iconColor, textColor, secondaryTextColor, surfaceColor),
                _buildProduk(context, iconColor, textColor, secondaryTextColor, surfaceColor),
              ],
            )
          : const Center(
              child: CircularProgressIndicator(
                valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF00FFFF)),
              ),
            ),
    );
  }

  // 📊 Dashboard Tab
  Widget _buildDashboard(
    BuildContext context,
    Color iconColor,
    Color textColor,
    Color secondaryTextColor,
    Color surfaceColor,
  ) {
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
  Widget _buildKasir(
    BuildContext context,
    Color iconColor,
    Color textColor,
    Color secondaryTextColor,
    Color surfaceColor,
  ) {
    return Consumer<TokoProvider>(
      builder: (context, provider, child) {
        final cartItems = provider.cartItems ?? [];
        final cartTotal = provider.cartTotal ?? 0;

        return Column(
          children: [
            // Voice Scan Button
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: _openVoiceScanner,
                      icon: const Icon(Icons.mic, color: Colors.black),
                      label: const Text(
                        '🎤 Scan Suara',
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
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () async {
                        await Navigator.push(
                          context,
                          MaterialPageRoute(
                            builder: (_) => const BarcodeScannerScreen(),
                          ),
                        );
                      },
                      icon: const Icon(Icons.qr_code_scanner, color: Colors.black),
                      label: const Text(
                        '📷 Barcode',
                        style: TextStyle(color: Colors.black, fontSize: 16),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.amberAccent,
                        minimumSize: const Size(double.infinity, 56),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                ],
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
                  :                     SingleChildScrollView(
                      scrollDirection: Axis.vertical,
                      child: DataTable(
                        columnSpacing: 15,
                        horizontalMargin: 10,
                        headingRowHeight: 40,
                        columns: [
                          DataColumn(label: Text('PRODUK', style: TextStyle(color: iconColor, fontSize: 12))),
                          DataColumn(label: Text('QTY', style: TextStyle(color: iconColor, fontSize: 12))),
                          DataColumn(label: Text('SUBTOTAL', style: TextStyle(color: iconColor, fontSize: 12))),
                          DataColumn(label: Text('', style: TextStyle(color: iconColor, fontSize: 12))),
                        ],
                        rows: cartItems.map((item) => DataRow(
                          cells: [
                            DataCell(Text(item['name'] ?? '', style: TextStyle(color: Colors.white, fontSize: 13))),
                            DataCell(Text('${item['quantity']}', style: TextStyle(color: Colors.white))),
                            DataCell(Text('Rp ${_formatNumber(item['subtotal'] ?? 0)}', style: TextStyle(color: Colors.white))),
                            DataCell(IconButton(
                              icon: Icon(Icons.remove_circle_outline, color: Colors.redAccent, size: 18),
                              onPressed: () => provider.decrementCartItem(item['id']),
                            )),
                          ],
                        )).toList(),
                      ),
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
  Widget _buildProduk(
    BuildContext context,
    Color iconColor,
    Color textColor,
    Color secondaryTextColor,
    Color surfaceColor,
  ) {
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
                      :                     SingleChildScrollView(
                      scrollDirection: Axis.vertical,
                      child: DataTable(
                        columnSpacing: 15,
                        horizontalMargin: 10,
                        headingRowHeight: 40,
                        columns: [
                          DataColumn(label: Text('PRODUK', style: TextStyle(color: iconColor, fontSize: 12))),
                          DataColumn(label: Text('QTY', style: TextStyle(color: iconColor, fontSize: 12))),
                          DataColumn(label: Text('SUBTOTAL', style: TextStyle(color: iconColor, fontSize: 12))),
                          DataColumn(label: Text('', style: TextStyle(color: iconColor, fontSize: 12))),
                        ],
                        rows: products.map((product) => DataRow(
                          cells: [
                            DataCell(Text(product['name'] ?? '', style: TextStyle(color: Colors.white, fontSize: 13))),
                            DataCell(Text('${product['stock'] ?? 0}', style: TextStyle(color: Colors.white))),
                            DataCell(Text('Rp ${_formatNumber(product['price'] ?? 0)}', style: TextStyle(color: Colors.white))),
                            DataCell(IconButton(
                              icon: Icon(Icons.add_circle, color: Colors.green, size: 18),
                              onPressed: () { provider.addToCart(product, 1); },
                            )),
                          ],
                        )).toList(),
                      ),
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
    );
  }

  // ==================== DIALOGS ====================

  
  void _showVoiceScanDialog(BuildContext context, Color iconColor) {
    final TextEditingController voiceController = TextEditingController();
    bool isProcessing = false;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          backgroundColor: Theme.of(context).cardColor,
          title: Row(
            children: [
              Icon(Icons.mic, color: iconColor),
              const SizedBox(width: 8),
              const Text('Voice Scan Kasir'),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Contoh: "2 keripik pisang 1 cireng"',
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: voiceController,
                decoration: InputDecoration(
                  labelText: 'Ucapkan atau ketik',
                  hintText: '2 keripik pisang 1 cireng',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.keyboard_voice, color: iconColor),
                ),
                maxLines: 2,
                enabled: !isProcessing,
                autofocus: true,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                voiceController.dispose();
                Navigator.pop(ctx);
              },
              child: const Text('Batal'),
            ),
            ElevatedButton.icon(
              onPressed: isProcessing ? null : () async {
                final text = voiceController.text.trim();
                if (text.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Mohon masukkan teks')),
                  );
                  return;
                }

                setState(() => isProcessing = true);

                try {
                  await context.read<TokoProvider>().processVoiceScan(text);
                  
                  Navigator.pop(ctx);
                  
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('✅ Produk ditambahkan ke keranjang'),
                      backgroundColor: Colors.green,
                    ),
                  );
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('❌ Error: $e'),
                      backgroundColor: Colors.red,
                    ),
                  );
                } finally {
                  setState(() => isProcessing = false);
                }
              },
              icon: isProcessing 
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                  )
                : const Icon(Icons.send),
              label: Text(isProcessing ? 'Memproses...' : 'Proses'),
              style: ElevatedButton.styleFrom(
                backgroundColor: iconColor,
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    ).then((_) => voiceController.dispose());
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
    final barcodeController = TextEditingController();
    final inputColor = Theme.of(context).brightness == Brightness.dark 
        ? const Color(0xFF0A0A0F) 
        : Colors.grey.shade100;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: surfaceColor,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Tambah Produk', style: TextStyle(color: textColor)),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: InputDecoration(
                  labelText: 'Nama Produk',
                  labelStyle: TextStyle(color: secondaryTextColor),
                  filled: true,
                  fillColor: inputColor,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.all(12),
                ),
                style: TextStyle(color: textColor),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: priceController,
                decoration: InputDecoration(
                  labelText: 'Harga',
                  labelStyle: TextStyle(color: secondaryTextColor),
                  filled: true,
                  fillColor: inputColor,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.all(12),
                ),
                keyboardType: TextInputType.number,
                style: TextStyle(color: textColor),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: stockController,
                decoration: InputDecoration(
                  labelText: 'Stok',
                  labelStyle: TextStyle(color: secondaryTextColor),
                  filled: true,
                  fillColor: inputColor,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.all(12),
                ),
                keyboardType: TextInputType.number,
                style: TextStyle(color: textColor),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: barcodeController,
                decoration: InputDecoration(
                  labelText: 'Barcode',
                  labelStyle: TextStyle(color: secondaryTextColor),
                  filled: true,
                  fillColor: inputColor,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.all(12),
                ),
                keyboardType: TextInputType.text,
                style: TextStyle(color: textColor),
              ),
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                    onPressed: () async {
                      final code = await Navigator.push<String>(
                        context,
                        MaterialPageRoute(
                          builder: (_) => const BarcodeScannerScreen(returnRawBarcode: true),
                        ),
                      );
                      if (code != null && code.isNotEmpty) {
                        barcodeController.text = code;

                        final result = await ApiService.lookupProductByBarcode(code);
                        if (result != null && result['name'] != null) {
                          final productName = result['name'].toString().trim();
                          if (productName.isNotEmpty) {
                            nameController.text = productName;
                          }
                        }
                      }
                    },
                  icon: const Icon(Icons.qr_code_scanner, color: Colors.black),
                  label: const Text(
                    'Scan Barcode',
                    style: TextStyle(color: Colors.black),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.amberAccent,
                    foregroundColor: Colors.black,
                    minimumSize: const Size(double.infinity, 48),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10),
                    ),
                  ),
                ),
              ),
            ],
          ),
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
                  'price': double.tryParse(priceController.text) ?? 0.0,
                  'stock': int.tryParse(stockController.text) ?? 0,
                'barcode': barcodeController.text.trim().isEmpty ? null : barcodeController.text.trim(),
                };
                context.read<TokoProvider>().addProduct(data);
                Navigator.pop(ctx);
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: iconColor,
              foregroundColor: Colors.black,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text('Simpan'),
          ),
        ],
      ),
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
    final priceController = TextEditingController(text: '${product['price']}');
    final stockController = TextEditingController(text: '${product['stock']}');
    final barcodeController = TextEditingController(text: product['barcode'] ?? '');
    final inputColor = Theme.of(context).brightness == Brightness.dark 
        ? const Color(0xFF0A0A0F) 
        : Colors.grey.shade100;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: surfaceColor,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Edit Produk', style: TextStyle(color: textColor)),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameController,
                decoration: InputDecoration(
                  labelText: 'Nama Produk',
                  labelStyle: TextStyle(color: secondaryTextColor),
                  filled: true,
                  fillColor: inputColor,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.all(12),
                ),
                style: TextStyle(color: textColor),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: priceController,
                decoration: InputDecoration(
                  labelText: 'Harga',
                  labelStyle: TextStyle(color: secondaryTextColor),
                  filled: true,
                  fillColor: inputColor,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.all(12),
                ),
                keyboardType: TextInputType.number,
                style: TextStyle(color: textColor),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: stockController,
                decoration: InputDecoration(
                  labelText: 'Stok',
                  labelStyle: TextStyle(color: secondaryTextColor),
                  filled: true,
                  fillColor: inputColor,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.all(12),
                ),
                keyboardType: TextInputType.number,
                style: TextStyle(color: textColor),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: barcodeController,
                decoration: InputDecoration(
                  labelText: 'Barcode',
                  labelStyle: TextStyle(color: secondaryTextColor),
                  filled: true,
                  fillColor: inputColor,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.all(12),
                ),
                keyboardType: TextInputType.text,
                style: TextStyle(color: textColor),
              ),
            ],
          ),
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
                'price': double.tryParse(priceController.text) ?? 0.0,
                'stock': int.tryParse(stockController.text) ?? 0,
                'barcode': barcodeController.text.trim().isEmpty ? null : barcodeController.text.trim(),
              };
              context.read<TokoProvider>().updateProduct(product['id'], data);
              Navigator.pop(ctx);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: iconColor,
              foregroundColor: Colors.black,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text('Update'),
          ),
        ],
      ),
    );
  }

  void _deleteProduct(
    BuildContext context,
    int productId,
    TokoProvider provider,
    Color iconColor,
    Color textColor,
  ) {
    final secondaryTextColor = Theme.of(context).brightness == Brightness.dark 
        ? Colors.grey.shade400 
        : Colors.grey.shade600;
    final surfaceColor = Theme.of(context).brightness == Brightness.dark 
        ? const Color(0xFF1A1A2E) 
        : Colors.white;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: surfaceColor,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Konfirmasi', style: TextStyle(color: textColor)),
        content: Text(
          'Yakin ingin menghapus produk ini?',
          style: TextStyle(color: secondaryTextColor),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text('Batal', style: TextStyle(color: secondaryTextColor)),
          ),
          ElevatedButton(
            onPressed: () {
              provider.deleteProduct(productId);
              Navigator.pop(ctx);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text('Hapus'),
          ),
        ],
      ),
    );
  }

  void _processCheckout(BuildContext context, TokoProvider provider, Color iconColor) {
    final textColor = Theme.of(context).brightness == Brightness.dark 
        ? Colors.white 
        : Colors.black87;
    final secondaryTextColor = Theme.of(context).brightness == Brightness.dark 
        ? Colors.grey.shade400 
        : Colors.grey.shade600;
    final surfaceColor = Theme.of(context).brightness == Brightness.dark 
        ? const Color(0xFF1A1A2E) 
        : Colors.white;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: surfaceColor,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Proses Pembayaran', style: TextStyle(color: textColor)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              'Total: Rp ${_formatNumber(provider.cartTotal)}',
              style: TextStyle(
                color: iconColor,
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              'Konfirmasi pembayaran?',
              style: TextStyle(color: secondaryTextColor),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text('Batal', style: TextStyle(color: secondaryTextColor)),
          ),
          ElevatedButton(
            onPressed: () async {
              await provider.checkout();
              Navigator.pop(ctx);
              
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Row(
                      children: const [
                        Icon(Icons.check_circle, color: Colors.white),
                        SizedBox(width: 8),
                        Text('✅ Transaksi berhasil!'),
                      ],
                    ),
                    backgroundColor: Colors.green,
                    behavior: SnackBarBehavior.floating,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: iconColor,
              foregroundColor: Colors.black,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text('Bayar'),
          ),
        ],
      ),
    );
  }

  // ==================== HELPERS ====================

  String _formatNumber(dynamic value) {
    if (value == null) return '0';
    if (value is int) return value.toString();
    if (value is double) return value.toStringAsFixed(0);
    return value.toString();
  }

  String _formatDate(String? dateStr) {
    if (dateStr == null || dateStr.isEmpty) return '';
    try {
      final date = DateTime.parse(dateStr);
      final now = DateTime.now();
      final difference = now.difference(date);

      if (difference.inDays == 0) {
        if (difference.inHours == 0) {
          return '${difference.inMinutes} menit yang lalu';
        }
        return '${difference.inHours} jam yang lalu';
      } else if (difference.inDays == 1) {
        return 'Kemarin';
      } else if (difference.inDays < 7) {
        return '${difference.inDays} hari yang lalu';
      } else {
        return '${date.day}/${date.month}/${date.year}';
      }
    } catch (e) {
      return dateStr;
    }
  }
}
