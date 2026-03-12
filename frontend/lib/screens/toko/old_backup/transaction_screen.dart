import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/toko_provider.dart';
import '../../providers/auth_provider.dart';

class TransactionScreen extends StatefulWidget {
  const TransactionScreen({super.key});

  @override
  State<TransactionScreen> createState() => _TransactionScreenState();
}

class _TransactionScreenState extends State<TransactionScreen>
    with SingleTickerProviderStateMixin {
  final TextEditingController _voiceController = TextEditingController();
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      duration: const Duration(seconds: 1),
      vsync: this,
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _voiceController.dispose();
    _pulseController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final toko = Provider.of<TokoProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('SCAN TRANSAKSI'),
        backgroundColor: const Color(0xFF050507),
        foregroundColor: const Color(0xFFFF44AA),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => _showHistory(context),
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
            // Voice Input Area
            Expanded(
              flex: 3,
              child: Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      AnimatedBuilder(
                        animation: _pulseController,
                        builder: (context, child) {
                          return Container(
                            width: 120,
                            height: 120,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              border: Border.all(
                                color: const Color(0xFFFF44AA).withOpacity(
                                    0.5 + (_pulseController.value * 0.3)),
                                width: 3,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: const Color(0xFFFF44AA).withOpacity(
                                      0.3 * _pulseController.value),
                                  blurRadius: 30,
                                  spreadRadius: 10,
                                ),
                              ],
                            ),
                            child: const Icon(
                              Icons.mic,
                              color: Color(0xFFFF44AA),
                              size: 60,
                            ),
                          );
                        },
                      ),
                      const SizedBox(height: 32),
                      const Text(
                        'SCAN SUARA',
                        style: TextStyle(
                          color: Color(0xFFFF44AA),
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 2,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Ketik atau scan suara belanjaan',
                        style: TextStyle(
                          color: const Color(0xFF8888AA).withOpacity(0.8),
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 24),
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: const Color(0xFF12121A),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(
                            color: const Color(0xFFFF44AA).withOpacity(0.3),
                          ),
                        ),
                        child: Column(
                          children: [
                            TextField(
                              controller: _voiceController,
                              style: const TextStyle(color: Color(0xFFE0E0FF)),
                              maxLines: 3,
                              decoration: InputDecoration(
                                hintText:
                                    'Contoh: beli rokok 20rb, susu 15rb, beras 14rb',
                                hintStyle: TextStyle(
                                    color: const Color(0xFF8888AA)
                                        .withOpacity(0.5)),
                                border: InputBorder.none,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.end,
                              children: [
                                Icon(Icons.spatial_audio,
                                    color: const Color(0xFFFF44AA), size: 16),
                                const SizedBox(width: 4),
                                Text(
                                  'Fitur voice soon',
                                  style: TextStyle(
                                      color: const Color(0xFF8888AA)
                                          .withOpacity(0.5),
                                      fontSize: 12),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),

            // Scan Button
            Padding(
              padding: const EdgeInsets.all(16),
              child: SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: toko.isLoading ? null : _processScan,
                  icon: toko.isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(
                                Color(0xFF0A0A0F)),
                          ),
                        )
                      : const Icon(Icons.qr_code_scanner,
                          color: Color(0xFF0A0A0F)),
                  label: Text(
                    toko.isLoading ? 'MEMPROSES...' : 'SCAN BELANJA',
                    style: const TextStyle(
                      color: Color(0xFF0A0A0F),
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1,
                    ),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFFF44AA),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 4,
                    shadowColor: const Color(0xFFFF44AA).withOpacity(0.5),
                  ),
                ),
              ),
            ),

            // Last Scan Result
            if (toko.lastScanResult != null) ...[
              Container(
                margin: const EdgeInsets.all(16),
                padding: const EdgeInsets.all(16),
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
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.check_circle,
                            color: const Color(0xFF00FFAA), size: 20),
                        const SizedBox(width: 8),
                        const Text(
                          'HASIL SCAN',
                          style: TextStyle(
                            color: Color(0xFF00FFAA),
                            fontWeight: FontWeight.bold,
                            letterSpacing: 1,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    SelectableText(
                      toko.lastScanResult!['preview'] ?? '',
                      style: const TextStyle(
                          color: Color(0xFFE0E0FF), height: 1.5),
                    ),
                    if (toko.lastScanResult!['not_found'] != null &&
                        (toko.lastScanResult!['not_found'] as List)
                            .isNotEmpty) ...[
                      const SizedBox(height: 12),
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.orange.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                          border:
                              Border.all(color: Colors.orange.withOpacity(0.3)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(Icons.warning,
                                    color: Colors.orange, size: 16),
                                const SizedBox(width: 4),
                                Text(
                                  'Produk tidak ditemukan:',
                                  style: TextStyle(
                                      color: Colors.orange,
                                      fontWeight: FontWeight.bold),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              (toko.lastScanResult!['not_found'] as List)
                                  .join(', '),
                              style: const TextStyle(color: Colors.orange),
                            ),
                          ],
                        ),
                      ),
                    ],
                    const SizedBox(height: 16),
                    if (toko.lastScanResult!['transaction_id'] == null)
                      Row(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          TextButton(
                            onPressed: () => toko.clearLastScan(),
                            child: const Text('BATAL',
                                style: TextStyle(color: Color(0xFF8888AA))),
                          ),
                          const SizedBox(width: 8),
                          ElevatedButton(
                            onPressed: () =>
                                _saveTransaction(toko.lastScanResult!),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: const Color(0xFFFF44AA),
                              foregroundColor: const Color(0xFF0A0A0F),
                            ),
                            child: const Text('SIMPAN TRANSAKSI'),
                          ),
                        ],
                      ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Future<void> _processScan() async {
    if (_voiceController.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Masukkan teks belanjaan'),
          backgroundColor: Colors.orange,
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }

    final toko = Provider.of<TokoProvider>(context, listen: false);
    final result = await toko.scanVoice(_voiceController.text, autoSave: false);

    if (result != null && mounted) {
      _voiceController.clear();
    }
  }

  Future<void> _saveTransaction(Map<String, dynamic> scanResult) async {
    if (scanResult['items'] == null || (scanResult['items'] as List).isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Tidak ada item untuk disimpan'),
          backgroundColor: Colors.orange,
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }

    // Konversi ke format sale
    final saleData = {
      'items': scanResult['items'],
      'payment_method': 'cash',
      'notes': 'Voice scan',
    };

    final toko = Provider.of<TokoProvider>(context, listen: false);
    final result = await toko.createSale(saleData);

    if (result != null && mounted) {
      toko.clearLastScan();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ Transaksi disimpan'),
          backgroundColor: Color(0xFF12121A),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.all(Radius.circular(12)),
            side: BorderSide(color: Color(0xFF00FFAA), width: 0.5),
          ),
        ),
      );
    }
  }

  void _showHistory(BuildContext context) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => const SalesHistoryScreen(),
      ),
    );
  }
}

// Sales History Screen
class SalesHistoryScreen extends StatelessWidget {
  const SalesHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final toko = Provider.of<TokoProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('RIWAYAT TRANSAKSI'),
        backgroundColor: const Color(0xFF050507),
        foregroundColor: const Color(0xFFFF44AA),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF0A0A0F), Color(0xFF050507)],
          ),
        ),
        child: toko.isLoading
            ? const Center(
                child: CircularProgressIndicator(
                  valueColor: AlwaysStoppedAnimation<Color>(Color(0xFFFF44AA)),
                ),
              )
            : toko.sales.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Container(
                          padding: const EdgeInsets.all(24),
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: const Color(0xFFFF44AA).withOpacity(0.3),
                              width: 2,
                            ),
                          ),
                          child: const Icon(
                            Icons.receipt_outlined,
                            size: 64,
                            color: Color(0xFFFF44AA),
                          ),
                        ),
                        const SizedBox(height: 24),
                        const Text(
                          'BELUM ADA TRANSAKSI',
                          style: TextStyle(
                            color: Color(0xFFFF44AA),
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 2,
                          ),
                        ),
                      ],
                    ),
                  )
                : ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: toko.sales.length,
                    itemBuilder: (context, index) {
                      final sale = toko.sales[index];
                      return _buildSaleCard(sale);
                    },
                  ),
      ),
    );
  }

  Widget _buildSaleCard(Map<String, dynamic> sale) {
    final items = sale['items'] is String
        ? jsonDecode(sale['items'])
        : (sale['items'] as List? ?? []);

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
          color: const Color(0xFFFF44AA).withOpacity(0.3),
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
                    color: const Color(0xFFFF44AA).withOpacity(0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(
                    Icons.receipt,
                    color: Color(0xFFFF44AA),
                    size: 20,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        sale['invoice_number'] ?? 'INV-XXXX',
                        style: const TextStyle(
                          color: Color(0xFFE0E0FF),
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        _formatDate(sale['created_at']),
                        style: TextStyle(
                          color: const Color(0xFF8888AA).withOpacity(0.8),
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: const Color(0xFF00FFAA).withOpacity(0.15),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: const Color(0xFF00FFAA).withOpacity(0.3),
                    ),
                  ),
                  child: Text(
                    'Rp ${sale['total']?.toStringAsFixed(0) ?? '0'}',
                    style: const TextStyle(
                      fontSize: 12,
                      color: Color(0xFF00FFAA),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...items.take(2).map((item) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Text(
                    '• ${item['name']}: ${item['qty']} x Rp ${item['price']?.toStringAsFixed(0)}',
                    style: TextStyle(
                      color: const Color(0xFF8888AA).withOpacity(0.9),
                      fontSize: 13,
                    ),
                  ),
                )),
            if (items.length > 2)
              Text(
                '+${items.length - 2} item lainnya',
                style: TextStyle(
                  color: const Color(0xFF8888AA).withOpacity(0.6),
                  fontSize: 12,
                  fontStyle: FontStyle.italic,
                ),
              ),
          ],
        ),
      ),
    );
  }

  String _formatDate(String? dateStr) {
    if (dateStr == null) return '';
    try {
      final dt = DateTime.parse(dateStr);
      return '${dt.day}/${dt.month}/${dt.year} ${dt.hour}:${dt.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return dateStr;
    }
  }
}
