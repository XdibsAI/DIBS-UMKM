import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/toko_provider.dart';
import 'product_screen.dart';
import 'transaction_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> with SingleTickerProviderStateMixin {
  late AnimationController _refreshController;

  @override
  void initState() {
    super.initState();
    _refreshController = AnimationController(
      duration: const Duration(seconds: 1),
      vsync: this,
    );
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadDashboardData();
    });
  }

  @override
  void dispose() {
    _refreshController.dispose();
    super.dispose();
  }

  Future<void> _loadDashboardData() async {
    final toko = Provider.of<TokoProvider>(context, listen: false);
    await toko.loadDashboard();
    await toko.loadProducts();
    await toko.loadSales(limit: 10);
  }

  @override
  Widget build(BuildContext context) {
    final toko = Provider.of<TokoProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('DASHBOARD TOKO'),
        backgroundColor: const Color(0xFF050507),
        foregroundColor: const Color(0xFF9D4DFF),
        actions: [
          IconButton(
            icon: AnimatedBuilder(
              animation: _refreshController,
              builder: (context, child) {
                return Transform.rotate(
                  angle: _refreshController.value * 2 * 3.14159,
                  child: const Icon(Icons.refresh),
                );
              },
            ),
            onPressed: () {
              _refreshController.forward().then((_) {
                _refreshController.reset();
                _loadDashboardData();
              });
            },
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
        child: toko.isLoading && toko.dashboardSummary == null
            ? const Center(
                child: CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF9D4DFF)),
                ),
              )
            : RefreshIndicator(
                onRefresh: _loadDashboardData,
                color: const Color(0xFF9D4DFF),
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Welcome Header
                      _buildWelcomeHeader(),
                      const SizedBox(height: 20),

                      // Stats Cards
                      _buildStatsGrid(toko),
                      const SizedBox(height: 24),

                      // Quick Actions
                      _buildSectionTitle('AKSI CEPAT', const Color(0xFF9D4DFF)),
                      const SizedBox(height: 12),
                      _buildQuickActions(),
                      const SizedBox(height: 24),

                      // Low Stock Alert
                      if (toko.dashboardSummary?['alerts']?['low_stock'] != null &&
                          (toko.dashboardSummary!['alerts']['low_stock'] as List).isNotEmpty)
                        _buildLowStockSection(toko),
                      const SizedBox(height: 24),

                      // Recent Transactions
                      _buildSectionTitle('TRANSAKSI TERBARU', const Color(0xFFFF44AA)),
                      const SizedBox(height: 12),
                      _buildRecentTransactions(toko),
                      const SizedBox(height: 24),

                      // Top Products (placeholder)
                      _buildSectionTitle('PRODUK POPULER', const Color(0xFF00FFAA)),
                      const SizedBox(height: 12),
                      _buildTopProducts(toko),
                    ],
                  ),
                ),
              ),
      ),
    );
  }

  Widget _buildWelcomeHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF12121A), Color(0xFF0A0A0F)],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: const Color(0xFF9D4DFF).withOpacity(0.3),
        ),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF9D4DFF).withOpacity(0.15),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.storefront,
              color: Color(0xFF9D4DFF),
              size: 32,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'TOKO ANDA',
                  style: TextStyle(
                    color: Color(0xFF9D4DFF),
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Kelola produk, stok, dan transaksi',
                  style: TextStyle(
                    color: const Color(0xFF8888AA).withOpacity(0.8),
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsGrid(TokoProvider toko) {
    final summary = toko.dashboardSummary;
    final products = summary?['products'] ?? {};
    final inventory = summary?['inventory'] ?? {};
    final salesToday = summary?['sales_today'] ?? {};

    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 1.5,
      children: [
        _buildStatCard(
          title: 'PRODUK',
          value: '${products['active'] ?? 0}',
          subtitle: 'Total: ${products['total'] ?? 0}',
          icon: Icons.inventory,
          color: const Color(0xFF00FFFF),
        ),
        _buildStatCard(
          title: 'STOK RENDAH',
          value: '${products['low_stock'] ?? 0}',
          subtitle: 'Perlu restok',
          icon: Icons.warning,
          color: products['low_stock'] > 0 ? Colors.red : const Color(0xFF00FFAA),
        ),
        _buildStatCard(
          title: 'PENJUALAN HARI INI',
          value: 'Rp ${(salesToday['total_sales'] ?? 0).toStringAsFixed(0)}',
          subtitle: '${salesToday['transaction_count'] ?? 0} transaksi',
          icon: Icons.today,
          color: const Color(0xFFFF44AA),
        ),
        _buildStatCard(
          title: 'NILAI STOK',
          value: 'Rp ${(inventory['total_value'] ?? 0).toStringAsFixed(0)}',
          subtitle: 'Modal: Rp ${(inventory['total_investment'] ?? 0).toStringAsFixed(0)}',
          icon: Icons.attach_money,
          color: const Color(0xFF00FFAA),
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required String subtitle,
    required IconData icon,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF12121A), Color(0xFF0A0A0F)],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: TextStyle(
                  color: color,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.5,
                ),
              ),
              Icon(icon, color: color, size: 16),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              color: Color(0xFFE0E0FF),
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
            overflow: TextOverflow.ellipsis,
          ),
          Text(
            subtitle,
            style: TextStyle(
              color: const Color(0xFF8888AA).withOpacity(0.8),
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title, Color color) {
    return Padding(
      padding: const EdgeInsets.only(left: 4),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 14,
          fontWeight: FontWeight.bold,
          color: color,
          letterSpacing: 1,
        ),
      ),
    );
  }

  Widget _buildQuickActions() {
    return Row(
      children: [
        Expanded(
          child: _buildActionButton(
            icon: Icons.add_shopping_cart,
            label: 'TAMBAH PRODUK',
            color: const Color(0xFF00FFFF),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const ProductScreen()),
              );
            },
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildActionButton(
            icon: Icons.qr_code_scanner,
            label: 'SCAN TRANSAKSI',
            color: const Color(0xFFFF44AA),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const TransactionScreen()),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [color.withOpacity(0.15), Colors.transparent],
          ),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: color.withOpacity(0.3)),
        ),
        child: Column(
          children: [
            Icon(icon, color: color, size: 28),
            const SizedBox(height: 8),
            Text(
              label,
              style: TextStyle(
                color: color,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLowStockSection(TokoProvider toko) {
    final lowStock = toko.dashboardSummary!['alerts']['low_stock'] as List;
    
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF12121A), Color(0xFF0A0A0F)],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: Colors.red.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.warning, color: Colors.red, size: 20),
              const SizedBox(width: 8),
              const Text(
                'STOK RENDAH',
                style: TextStyle(
                  color: Colors.red,
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...lowStock.take(3).map((product) => Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    product['name'],
                    style: const TextStyle(color: Color(0xFFE0E0FF)),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    'Stok: ${product['stock']}',
                    style: const TextStyle(color: Colors.red, fontSize: 12),
                  ),
                ),
              ],
            ),
          )),
          if (lowStock.length > 3)
            Text(
              '+${lowStock.length - 3} produk lainnya',
              style: TextStyle(
                color: const Color(0xFF8888AA).withOpacity(0.6),
                fontSize: 12,
                fontStyle: FontStyle.italic,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildRecentTransactions(TokoProvider toko) {
    if (toko.sales.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF12121A), Color(0xFF0A0A0F)],
          ),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFFFF44AA).withOpacity(0.3)),
        ),
        child: Center(
          child: Column(
            children: [
              Icon(Icons.receipt_outlined, color: const Color(0xFFFF44AA).withOpacity(0.3), size: 48),
              const SizedBox(height: 8),
              Text(
                'Belum ada transaksi',
                style: TextStyle(color: const Color(0xFF8888AA).withOpacity(0.8)),
              ),
            ],
          ),
        ),
      );
    }

    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF12121A), Color(0xFF0A0A0F)],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: const Color(0xFFFF44AA).withOpacity(0.3),
        ),
      ),
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: toko.sales.length > 5 ? 5 : toko.sales.length,
        separatorBuilder: (_, __) => Divider(
          height: 1,
          color: const Color(0xFFFF44AA).withOpacity(0.1),
        ),
        itemBuilder: (context, index) {
          final sale = toko.sales[index];
          final items = sale['items'] is String 
              ? jsonDecode(sale['items']) 
              : (sale['items'] as List? ?? []);
          
          return ListTile(
            leading: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: const Color(0xFFFF44AA).withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.receipt, color: Color(0xFFFF44AA), size: 16),
            ),
            title: Text(
              sale['invoice_number'] ?? 'INV-XXXX',
              style: const TextStyle(color: Color(0xFFE0E0FF), fontSize: 14),
            ),
            subtitle: Text(
              '${items.length} item • ${_formatTime(sale['created_at'])}',
              style: TextStyle(color: const Color(0xFF8888AA).withOpacity(0.8), fontSize: 12),
            ),
            trailing: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: const Color(0xFF00FFAA).withOpacity(0.15),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                'Rp ${sale['total']?.toStringAsFixed(0)}',
                style: const TextStyle(color: Color(0xFF00FFAA), fontSize: 12),
              ),
            ),
            onTap: () {
              // TODO: Show sale detail
            },
          );
        },
      ),
    );
  }

  Widget _buildTopProducts(TokoProvider toko) {
    // Placeholder - nanti bisa diisi dengan produk terlaris dari API
    final topProducts = toko.products.take(3).toList();
    
    if (topProducts.isEmpty) {
      return Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF12121A), Color(0xFF0A0A0F)],
          ),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFF00FFAA).withOpacity(0.3)),
        ),
        child: Center(
          child: Column(
            children: [
              Icon(Icons.inventory_2_outlined, color: const Color(0xFF00FFAA).withOpacity(0.3), size: 48),
              const SizedBox(height: 8),
              Text(
                'Belum ada produk',
                style: TextStyle(color: const Color(0xFF8888AA).withOpacity(0.8)),
              ),
            ],
          ),
        ),
      );
    }

    return Container(
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF12121A), Color(0xFF0A0A0F)],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: const Color(0xFF00FFAA).withOpacity(0.3),
        ),
      ),
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: topProducts.length,
        separatorBuilder: (_, __) => Divider(
          height: 1,
          color: const Color(0xFF00FFAA).withOpacity(0.1),
        ),
        itemBuilder: (context, index) {
          final product = topProducts[index];
          return ListTile(
            leading: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: const Color(0xFF00FFAA).withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.shopping_bag, color: Color(0xFF00FFAA), size: 16),
            ),
            title: Text(
              product['name'] ?? 'Produk',
              style: const TextStyle(color: Color(0xFFE0E0FF), fontSize: 14),
            ),
            subtitle: Text(
              'Stok: ${product['stock'] ?? 0}',
              style: TextStyle(color: const Color(0xFF8888AA).withOpacity(0.8), fontSize: 12),
            ),
            trailing: Text(
              'Rp ${product['price']?.toStringAsFixed(0)}',
              style: const TextStyle(color: Color(0xFF00FFAA), fontSize: 12),
            ),
          );
        },
      ),
    );
  }

  String _formatTime(String? dateStr) {
    if (dateStr == null) return '';
    try {
      final dt = DateTime.parse(dateStr);
      return '${dt.hour}:${dt.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return '';
    }
  }
}
