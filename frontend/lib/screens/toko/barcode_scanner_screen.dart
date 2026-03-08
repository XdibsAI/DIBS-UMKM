import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:provider/provider.dart';

import '../../providers/toko_provider.dart';

class BarcodeScannerScreen extends StatefulWidget {
  final bool returnRawBarcode;

  const BarcodeScannerScreen({
    super.key,
    this.returnRawBarcode = false,
  });

  @override
  State<BarcodeScannerScreen> createState() => _BarcodeScannerScreenState();
}

class _BarcodeScannerScreenState extends State<BarcodeScannerScreen> {
  bool _isProcessing = false;
  final MobileScannerController _controller = MobileScannerController();

  Future<void> _handleBarcode(String code) async {
    if (_isProcessing) return;
    _isProcessing = true;

    try {
      if (widget.returnRawBarcode) {
        if (!mounted) return;
        Navigator.pop(context, code);
        return;
      }

      final provider = context.read<TokoProvider>();
      final result = await provider.scanBarcode(code);

      if (!mounted) return;

      if (result['matched'] == true) {
        final data = Map<String, dynamic>.from(result['data'] ?? {});
        final product = Map<String, dynamic>.from(data['product'] ?? {});

        final qty = await _askQuantity();
        if (qty == null) {
          return;
        }

        provider.addToCart(product, qty);

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${product['name'] ?? 'Produk'} x$qty ditambahkan'),
            backgroundColor: Colors.green,
          ),
        );

        Navigator.pop(context, code);
        return;
      }

      final add = await showDialog<bool>(
        context: context,
        builder: (_) => AlertDialog(
          title: const Text('Produk belum ada'),
          content: Text('Barcode $code belum terdaftar.\nTambah produk baru?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('Batal'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('Tambah'),
            ),
          ],
        ),
      );

      if (add == true) {
        Navigator.pop(context, code);
        return;
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('❌ $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      await Future.delayed(const Duration(milliseconds: 1200));
      _isProcessing = false;
    }
  }

  Future<int?> _askQuantity() async {
    final controller = TextEditingController(text: '1');

    return showDialog<int>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Jumlah Produk'),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
          autofocus: true,
          decoration: const InputDecoration(
            labelText: 'Qty',
            hintText: 'Masukkan jumlah',
            border: OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () {
              final qty = int.tryParse(controller.text.trim()) ?? 1;
              Navigator.pop(context, qty < 1 ? 1 : qty);
            },
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          widget.returnRawBarcode
              ? 'Scan Barcode untuk Produk'
              : 'Scan Barcode Produk',
        ),
      ),
      body: Stack(
        children: [
          MobileScanner(
            controller: _controller,
            onDetect: (capture) {
              final barcode =
                  capture.barcodes.isNotEmpty ? capture.barcodes.first : null;
              final code = barcode?.rawValue?.trim();

              if (code != null && code.isNotEmpty) {
                _handleBarcode(code);
              }
            },
          ),
          Positioned(
            left: 16,
            right: 16,
            bottom: 24,
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.black.withOpacity(0.65),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Text(
                widget.returnRawBarcode
                    ? 'Arahkan kamera ke barcode untuk mengisi field produk'
                    : 'Arahkan kamera ke barcode produk',
                textAlign: TextAlign.center,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
