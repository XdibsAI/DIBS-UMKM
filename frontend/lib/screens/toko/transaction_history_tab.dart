import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../providers/toko_provider.dart';
import '../../services/printer_service.dart';
import 'printer_setup_screen.dart';

class TransactionHistoryTab extends StatefulWidget {
  const TransactionHistoryTab({super.key});

  @override
  State<TransactionHistoryTab> createState() => _TransactionHistoryTabState();
}

class _TransactionHistoryTabState extends State<TransactionHistoryTab> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        context.read<TokoProvider>().loadSalesHistory();
      }
    });
  }

  List<Map<String, dynamic>> _parseItems(dynamic raw) {
    try {
      if (raw is List) {
        return List<Map<String, dynamic>>.from(raw);
      }
      if (raw is String && raw.trim().isNotEmpty) {
        final decoded = json.decode(raw);
        if (decoded is List) {
          return List<Map<String, dynamic>>.from(decoded);
        }
      }
    } catch (_) {}
    return [];
  }

  int _toInt(dynamic v) {
    if (v is int) return v;
    if (v is double) return v.toInt();
    if (v is String) return int.tryParse(v) ?? double.tryParse(v)?.toInt() ?? 0;
    return 0;
  }

  String _fmt(int value) => value.toString();

  String _fmtDate(dynamic raw) {
    try {
      final dt = DateTime.parse(raw.toString()).toLocal();
      final d = dt.day.toString().padLeft(2, '0');
      final m = dt.month.toString().padLeft(2, '0');
      final y = dt.year.toString();
      final h = dt.hour.toString().padLeft(2, '0');
      final min = dt.minute.toString().padLeft(2, '0');
      return '$d/$m/$y $h:$min';
    } catch (_) {
      return raw?.toString() ?? '-';
    }
  }

  Future<void> _showDetail(Map<String, dynamic> sale) async {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = isDark ? Colors.white : Colors.black87;
    final secondaryTextColor = isDark ? Colors.grey.shade400 : Colors.grey.shade700;
    final surfaceColor = isDark ? const Color(0xFF1A1A2E) : Colors.white;

    final items = _parseItems(sale['items']);
    final paymentMethod = (sale['payment_method']?.toString().trim().isNotEmpty ?? false)
        ? sale['payment_method'].toString()
        : 'cash';

    await showDialog(
      context: context,
      builder: (_) => AlertDialog(
        backgroundColor: surfaceColor,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Detail Transaksi', style: TextStyle(color: textColor)),
        content: SizedBox(
          width: double.maxFinite,
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('ID: ${sale['id'] ?? '-'}', style: TextStyle(color: secondaryTextColor, fontSize: 12)),
                const SizedBox(height: 4),
                Text('Tanggal: ${_fmtDate(sale['created_at'])}', style: TextStyle(color: secondaryTextColor)),
                const SizedBox(height: 4),
                Text(
                  'Metode: ${paymentMethod == 'qris' ? 'QRIS' : paymentMethod == 'transfer' ? 'Transfer' : 'Cash'}',
                  style: TextStyle(color: secondaryTextColor),
                ),
                const SizedBox(height: 12),
                ...items.map((item) {
                  final qty = _toInt(item['qty'] ?? item['quantity']);
                  final price = _toInt(item['price']);
                  final subtotal = _toInt(item['subtotal']) == 0 ? qty * price : _toInt(item['subtotal']);

                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            '${item['name'] ?? 'Produk'} x$qty',
                            style: TextStyle(color: textColor),
                          ),
                        ),
                        Text(
                          'Rp ${_fmt(subtotal)}',
                          style: TextStyle(color: textColor, fontWeight: FontWeight.w600),
                        ),
                      ],
                    ),
                  );
                }),
                const Divider(),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Total', style: TextStyle(color: textColor, fontWeight: FontWeight.bold)),
                    Text(
                      'Rp ${_fmt(_toInt(sale['total']))}',
                      style: const TextStyle(
                        color: Color(0xFF00FFFF),
                        fontWeight: FontWeight.bold,
                        fontSize: 18,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        actions: [
          OutlinedButton(
            onPressed: () async {
              await Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const PrinterSetupScreen()),
              );
            },
            child: const Text('Pilih Printer'),
          ),
          OutlinedButton(
            onPressed: () async {
              try {
                final printableItems = items.map((e) {
                  final qty = _toInt(e['qty'] ?? e['quantity']);
                  final price = _toInt(e['price']);
                  final subtotal = _toInt(e['subtotal']) == 0 ? qty * price : _toInt(e['subtotal']);
                  return {
                    'name': e['name'] ?? 'Produk',
                    'quantity': qty,
                    'subtotal': subtotal,
                  };
                }).toList();

                await PrinterService.printReceipt(
                  items: printableItems,
                  total: _toInt(sale['total']),
                  paymentMethod: paymentMethod,
                );

                if (!mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Struk berhasil dikirim ke printer'),
                    backgroundColor: Colors.green,
                  ),
                );
              } catch (e) {
                if (!mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text('Gagal cetak struk: $e'),
                    backgroundColor: Colors.red,
                  ),
                );
              }
            },
            child: const Text('Cetak Ulang'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF00FFFF),
              foregroundColor: Colors.black,
            ),
            child: const Text('Tutup'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final provider = context.watch<TokoProvider>();
    final history = provider.salesHistory;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDark ? const Color(0xFF0A0A0F) : const Color(0xFFF5F5F5);
    final surfaceColor = isDark ? const Color(0xFF1A1A2E) : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black87;
    final secondaryTextColor = isDark ? Colors.grey.shade400 : Colors.grey.shade700;
    const accentColor = Color(0xFF00FFFF);

    if (provider.isLoading && history.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    if (history.isEmpty) {
      return Container(
        color: bgColor,
        child: Center(
          child: Text(
            'Belum ada riwayat transaksi',
            style: TextStyle(color: secondaryTextColor, fontSize: 16),
          ),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => context.read<TokoProvider>().loadSalesHistory(),
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: history.length,
        itemBuilder: (_, i) {
          final sale = history[i];
          final total = _toInt(sale['total']);
          final paymentMethod = (sale['payment_method']?.toString().trim().isNotEmpty ?? false)
              ? sale['payment_method'].toString()
              : 'cash';

          return Container(
            margin: const EdgeInsets.only(bottom: 12),
            decoration: BoxDecoration(
              color: surfaceColor,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: accentColor.withOpacity(0.15)),
            ),
            child: ListTile(
              onTap: () => _showDetail(sale),
              title: Text(
                'Rp ${_fmt(total)}',
                style: TextStyle(
                  color: textColor,
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
              subtitle: Padding(
                padding: const EdgeInsets.only(top: 6),
                child: Text(
                  '${_fmtDate(sale['created_at'])}\nMetode: ${paymentMethod == 'qris' ? 'QRIS' : paymentMethod == 'transfer' ? 'Transfer' : 'Cash'}',
                  style: TextStyle(color: secondaryTextColor),
                ),
              ),
              trailing: Icon(Icons.receipt_long, color: accentColor),
              isThreeLine: true,
            ),
          );
        },
      ),
    );
  }
}
