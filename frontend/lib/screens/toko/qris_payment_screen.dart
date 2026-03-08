import 'dart:io';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../../services/api_service.dart';

class QrisPaymentScreen extends StatefulWidget {
  final int totalAmount;
  final Future<void> Function() onPaymentConfirmed;

  const QrisPaymentScreen({
    super.key,
    required this.totalAmount,
    required this.onPaymentConfirmed,
  });

  @override
  State<QrisPaymentScreen> createState() => _QrisPaymentScreenState();
}

class _QrisPaymentScreenState extends State<QrisPaymentScreen> {
  bool _isLoading = true;
  bool _isUploading = false;
  bool _isFinishing = false;

  String? _qrisImageUrl;
  String _bankName = '';
  String _accountName = '';
  String _accountNumber = '';

  @override
  void initState() {
    super.initState();
    _loadPaymentSettings();
  }

  Future<void> _loadPaymentSettings() async {
    setState(() => _isLoading = true);

    try {
      final res = await ApiService.getTokoPaymentSettings();
      final data = Map<String, dynamic>.from(res['data'] ?? {});

      setState(() {
        _qrisImageUrl = data['qris_image_url']?.toString();
        _bankName = data['bank_name']?.toString() ?? '';
        _accountName = data['account_name']?.toString() ?? '';
        _accountNumber = data['account_number']?.toString() ?? '';
      });
    } catch (_) {
      // noop
    }

    if (mounted) {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _uploadQrisImage() async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.image,
      allowMultiple: false,
    );

    if (result == null || result.files.isEmpty) return;

    final filePath = result.files.single.path;
    if (filePath == null || filePath.isEmpty) return;

    setState(() => _isUploading = true);

    try {
      final uploadRes = await ApiService.uploadFile(filePath);
      final data = Map<String, dynamic>.from(uploadRes['data'] ?? {});
      final rawPath = data['file_path']?.toString();

      if (rawPath == null || rawPath.isEmpty) {
        throw Exception('Upload QRIS gagal');
      }

      final fileName = rawPath.split('/').last;
      final publicUrl = '${ApiConfig.baseUrl.replaceFirst('/api/v1', '')}/uploads/$fileName';

      final saveRes = await ApiService.saveTokoPaymentSettings({
        'qris_image_url': publicUrl,
        'bank_name': _bankName,
        'account_name': _accountName,
        'account_number': _accountNumber,
      });

      if (saveRes['status'] != 'success') {
        throw Exception(saveRes['message'] ?? 'Gagal menyimpan QRIS');
      }

      if (!mounted) return;
      setState(() {
        _qrisImageUrl = publicUrl;
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('QRIS berhasil diupload'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Gagal upload QRIS: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isUploading = false);
      }
    }
  }

  Future<void> _finishPayment() async {
    setState(() => _isFinishing = true);

    try {
      await widget.onPaymentConfirmed();

      if (!mounted) return;
      Navigator.pop(context, true);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('✅ Pembayaran berhasil diproses'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Gagal menyelesaikan pembayaran: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isFinishing = false);
      }
    }
  }

  String _formatNumber(int value) => value.toString();

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDark ? const Color(0xFF0A0A0F) : const Color(0xFFF5F5F5);
    final surfaceColor = isDark ? const Color(0xFF1A1A2E) : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black87;
    final secondaryTextColor = isDark ? Colors.grey.shade400 : Colors.grey.shade700;
    final accentColor = const Color(0xFF00FFFF);

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        title: const Text('Pembayaran QRIS'),
        backgroundColor: surfaceColor,
        foregroundColor: textColor,
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : SafeArea(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: surfaceColor,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Column(
                        children: [
                          Text(
                            'Total Pembayaran',
                            style: TextStyle(
                              color: secondaryTextColor,
                              fontSize: 14,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Rp ${_formatNumber(widget.totalAmount)}',
                            style: TextStyle(
                              color: accentColor,
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    Expanded(
                      child: Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: surfaceColor,
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: _qrisImageUrl == null || _qrisImageUrl!.isEmpty
                            ? Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.qr_code_2,
                                    size: 80,
                                    color: secondaryTextColor,
                                  ),
                                  const SizedBox(height: 16),
                                  Text(
                                    'QRIS belum diatur',
                                    style: TextStyle(
                                      color: textColor,
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  const SizedBox(height: 8),
                                  Text(
                                    'Upload gambar QRIS milik penjual agar pembeli bisa scan pembayaran.',
                                    textAlign: TextAlign.center,
                                    style: TextStyle(color: secondaryTextColor),
                                  ),
                                  const SizedBox(height: 20),
                                  ElevatedButton.icon(
                                    onPressed: _isUploading ? null : _uploadQrisImage,
                                    icon: _isUploading
                                        ? const SizedBox(
                                            width: 18,
                                            height: 18,
                                            child: CircularProgressIndicator(
                                              strokeWidth: 2,
                                              color: Colors.black,
                                            ),
                                          )
                                        : const Icon(Icons.upload_file),
                                    label: Text(_isUploading ? 'Uploading...' : 'Upload QRIS'),
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: accentColor,
                                      foregroundColor: Colors.black,
                                    ),
                                  ),
                                ],
                              )
                            : Column(
                                children: [
                                  Expanded(
                                    child: ClipRRect(
                                      borderRadius: BorderRadius.circular(16),
                                      child: Image.network(
                                        _qrisImageUrl!,
                                        fit: BoxFit.contain,
                                        errorBuilder: (_, __, ___) => Center(
                                          child: Text(
                                            'Gagal memuat gambar QRIS',
                                            style: TextStyle(color: secondaryTextColor),
                                          ),
                                        ),
                                      ),
                                    ),
                                  ),
                                  const SizedBox(height: 12),
                                  Text(
                                    'Silakan minta pembeli scan QRIS di atas',
                                    style: TextStyle(color: secondaryTextColor),
                                  ),
                                ],
                              ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton(
                            onPressed: _isFinishing ? null : () => Navigator.pop(context),
                            child: const Text('Batal'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: ElevatedButton(
                            onPressed: (_qrisImageUrl == null || _qrisImageUrl!.isEmpty || _isFinishing)
                                ? null
                                : _finishPayment,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: accentColor,
                              foregroundColor: Colors.black,
                            ),
                            child: _isFinishing
                                ? const SizedBox(
                                    width: 18,
                                    height: 18,
                                    child: CircularProgressIndicator(
                                      strokeWidth: 2,
                                      color: Colors.black,
                                    ),
                                  )
                                : const Text('Sudah Dibayar'),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
    );
  }
}
