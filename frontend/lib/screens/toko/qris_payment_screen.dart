import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';

import '../../services/api_service.dart';

class QrisPaymentScreen extends StatefulWidget {
  final int totalAmount;
  final List<Map<String, dynamic>> cartItems;
  final Future<Map<String, dynamic>> Function(String paymentMethod) onPaymentConfirmed;

  const QrisPaymentScreen({
    super.key,
    required this.totalAmount,
    required this.cartItems,
    required this.onPaymentConfirmed,
  });

  @override
  State<QrisPaymentScreen> createState() => _QrisPaymentScreenState();
}

class _QrisPaymentScreenState extends State<QrisPaymentScreen> {
  bool _isLoading = true;
  bool _isUploading = false;
  bool _isSavingBank = false;
  bool _isFinishing = false;

  String? _qrisImageUrl;
  String _selectedMethod = 'qris';

  final _bankNameController = TextEditingController();
  final _accountNameController = TextEditingController();
  final _accountNumberController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadPaymentSettings();
  }

  @override
  void dispose() {
    _bankNameController.dispose();
    _accountNameController.dispose();
    _accountNumberController.dispose();
    super.dispose();
  }

  Future<void> _loadPaymentSettings() async {
    setState(() => _isLoading = true);

    try {
      final res = await ApiService.getTokoPaymentSettings();
      final data = Map<String, dynamic>.from(res['data'] ?? {});

      _qrisImageUrl = data['qris_image_url']?.toString();
      _bankNameController.text = data['bank_name']?.toString() ?? '';
      _accountNameController.text = data['account_name']?.toString() ?? '';
      _accountNumberController.text = data['account_number']?.toString() ?? '';

      if (_qrisImageUrl == null || _qrisImageUrl!.isEmpty) {
        _selectedMethod = 'transfer';
      } else {
        _selectedMethod = 'qris';
      }
    } catch (_) {}

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
        'bank_name': _bankNameController.text.trim(),
        'account_name': _accountNameController.text.trim(),
        'account_number': _accountNumberController.text.trim(),
      });

      if (saveRes['status'] != 'success') {
        throw Exception(saveRes['message'] ?? 'Gagal menyimpan QRIS');
      }

      if (!mounted) return;

      setState(() {
        _qrisImageUrl = publicUrl;
        _selectedMethod = 'qris';
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

  Future<void> _saveBankSettings() async {
    setState(() => _isSavingBank = true);

    try {
      final saveRes = await ApiService.saveTokoPaymentSettings({
        'qris_image_url': _qrisImageUrl,
        'bank_name': _bankNameController.text.trim(),
        'account_name': _accountNameController.text.trim(),
        'account_number': _accountNumberController.text.trim(),
      });

      if (saveRes['status'] != 'success') {
        throw Exception(saveRes['message'] ?? 'Gagal menyimpan rekening');
      }

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Data rekening berhasil disimpan'),
          backgroundColor: Colors.green,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Gagal menyimpan rekening: $e'),
          backgroundColor: Colors.red,
        ),
      );
    } finally {
      if (mounted) {
        setState(() => _isSavingBank = false);
      }
    }
  }

  Future<void> _showReceiptDialog(String paymentMethod, String? saleId) async {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textColor = isDark ? Colors.white : Colors.black87;
    final secondaryTextColor = isDark ? Colors.grey.shade400 : Colors.grey.shade700;
    final surfaceColor = isDark ? const Color(0xFF1A1A2E) : Colors.white;

    await showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        backgroundColor: surfaceColor,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text('Struk Pembayaran', style: TextStyle(color: textColor)),
        content: SizedBox(
          width: double.maxFinite,
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                if (saleId != null && saleId.isNotEmpty)
                  Text('ID Transaksi: $saleId', style: TextStyle(color: secondaryTextColor, fontSize: 12)),
                const SizedBox(height: 8),
                Text(
                  'Metode: ${paymentMethod == 'qris' ? 'QRIS' : 'Transfer'}',
                  style: TextStyle(color: secondaryTextColor),
                ),
                const SizedBox(height: 12),
                ...widget.cartItems.map((item) => Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Expanded(
                            child: Text(
                              '${item['name'] ?? 'Produk'} x${item['quantity'] ?? 1}',
                              style: TextStyle(color: textColor),
                            ),
                          ),
                          Text(
                            'Rp ${item['subtotal'] ?? 0}',
                            style: TextStyle(color: textColor, fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                    )),
                const Divider(),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('Total', style: TextStyle(color: textColor, fontWeight: FontWeight.bold)),
                    Text(
                      'Rp ${widget.totalAmount}',
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
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF00FFFF),
              foregroundColor: Colors.black,
            ),
            child: const Text('Selesai'),
          ),
        ],
      ),
    );
  }

  bool get _canPayWithTransfer {
    return _bankNameController.text.trim().isNotEmpty &&
        _accountNameController.text.trim().isNotEmpty &&
        _accountNumberController.text.trim().isNotEmpty;
  }

  Future<void> _finishPayment() async {
    if (_selectedMethod == 'qris' && (_qrisImageUrl == null || _qrisImageUrl!.isEmpty)) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Upload QRIS dulu'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    if (_selectedMethod == 'transfer' && !_canPayWithTransfer) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Lengkapi data rekening dulu'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() => _isFinishing = true);

    try {
      final result = await widget.onPaymentConfirmed(_selectedMethod);
      final saleId = result['sale_id']?.toString();

      if (!mounted) return;

      await _showReceiptDialog(_selectedMethod, saleId);

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

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDark ? const Color(0xFF0A0A0F) : const Color(0xFFF5F5F5);
    final surfaceColor = isDark ? const Color(0xFF1A1A2E) : Colors.white;
    final textColor = isDark ? Colors.white : Colors.black87;
    final secondaryTextColor = isDark ? Colors.grey.shade400 : Colors.grey.shade700;
    const accentColor = Color(0xFF00FFFF);

    return Scaffold(
      backgroundColor: bgColor,
      appBar: AppBar(
        title: const Text('Pembayaran'),
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
                            style: TextStyle(color: secondaryTextColor),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Rp ${widget.totalAmount}',
                            style: const TextStyle(
                              color: accentColor,
                              fontWeight: FontWeight.bold,
                              fontSize: 28,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: surfaceColor,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Row(
                        children: [
                          Expanded(
                            child: RadioListTile<String>(
                              value: 'qris',
                              groupValue: _selectedMethod,
                              onChanged: (_) => setState(() => _selectedMethod = 'qris'),
                              title: const Text('QRIS'),
                              contentPadding: EdgeInsets.zero,
                            ),
                          ),
                          Expanded(
                            child: RadioListTile<String>(
                              value: 'transfer',
                              groupValue: _selectedMethod,
                              onChanged: (_) => setState(() => _selectedMethod = 'transfer'),
                              title: const Text('Transfer'),
                              contentPadding: EdgeInsets.zero,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),
                    Expanded(
                      child: SingleChildScrollView(
                        child: Column(
                          children: [
                            if (_selectedMethod == 'qris')
                              Container(
                                width: double.infinity,
                                padding: const EdgeInsets.all(16),
                                decoration: BoxDecoration(
                                  color: surfaceColor,
                                  borderRadius: BorderRadius.circular(16),
                                ),
                                child: _qrisImageUrl == null || _qrisImageUrl!.isEmpty
                                    ? Column(
                                        children: [
                                          Icon(Icons.qr_code_2, size: 80, color: secondaryTextColor),
                                          const SizedBox(height: 12),
                                          Text(
                                            'QRIS belum diatur',
                                            style: TextStyle(
                                              color: textColor,
                                              fontWeight: FontWeight.bold,
                                              fontSize: 18,
                                            ),
                                          ),
                                          const SizedBox(height: 8),
                                          Text(
                                            'Upload QRIS milik penjual agar pembeli bisa scan.',
                                            textAlign: TextAlign.center,
                                            style: TextStyle(color: secondaryTextColor),
                                          ),
                                          const SizedBox(height: 16),
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
                                          ClipRRect(
                                            borderRadius: BorderRadius.circular(16),
                                            child: Image.network(
                                              _qrisImageUrl!,
                                              height: 320,
                                              fit: BoxFit.contain,
                                              errorBuilder: (_, __, ___) => Padding(
                                                padding: const EdgeInsets.all(32),
                                                child: Text(
                                                  'Gagal memuat gambar QRIS',
                                                  style: TextStyle(color: secondaryTextColor),
                                                ),
                                              ),
                                            ),
                                          ),
                                          const SizedBox(height: 12),
                                          Text(
                                            'Minta pembeli scan QRIS di atas',
                                            style: TextStyle(color: secondaryTextColor),
                                          ),
                                          const SizedBox(height: 12),
                                          OutlinedButton.icon(
                                            onPressed: _isUploading ? null : _uploadQrisImage,
                                            icon: const Icon(Icons.edit),
                                            label: const Text('Ganti QRIS'),
                                          ),
                                        ],
                                      ),
                              ),
                            if (_selectedMethod == 'transfer')
                              Container(
                                width: double.infinity,
                                padding: const EdgeInsets.all(16),
                                decoration: BoxDecoration(
                                  color: surfaceColor,
                                  borderRadius: BorderRadius.circular(16),
                                ),
                                child: Column(
                                  children: [
                                    TextField(
                                      controller: _bankNameController,
                                      decoration: const InputDecoration(
                                        labelText: 'Nama Bank',
                                        border: OutlineInputBorder(),
                                      ),
                                    ),
                                    const SizedBox(height: 12),
                                    TextField(
                                      controller: _accountNameController,
                                      decoration: const InputDecoration(
                                        labelText: 'Nama Pemilik Rekening',
                                        border: OutlineInputBorder(),
                                      ),
                                    ),
                                    const SizedBox(height: 12),
                                    TextField(
                                      controller: _accountNumberController,
                                      keyboardType: TextInputType.number,
                                      decoration: const InputDecoration(
                                        labelText: 'Nomor Rekening',
                                        border: OutlineInputBorder(),
                                      ),
                                    ),
                                    const SizedBox(height: 12),
                                    SizedBox(
                                      width: double.infinity,
                                      child: ElevatedButton.icon(
                                        onPressed: _isSavingBank ? null : _saveBankSettings,
                                        icon: _isSavingBank
                                            ? const SizedBox(
                                                width: 18,
                                                height: 18,
                                                child: CircularProgressIndicator(
                                                  strokeWidth: 2,
                                                  color: Colors.black,
                                                ),
                                              )
                                            : const Icon(Icons.save),
                                        label: Text(_isSavingBank ? 'Menyimpan...' : 'Simpan Rekening'),
                                        style: ElevatedButton.styleFrom(
                                          backgroundColor: accentColor,
                                          foregroundColor: Colors.black,
                                        ),
                                      ),
                                    ),
                                    if (_canPayWithTransfer) ...[
                                      const SizedBox(height: 16),
                                      const Divider(),
                                      const SizedBox(height: 8),
                                      Text(
                                        _bankNameController.text.trim(),
                                        style: TextStyle(
                                          color: textColor,
                                          fontSize: 18,
                                          fontWeight: FontWeight.bold,
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        _accountNameController.text.trim(),
                                        style: TextStyle(color: secondaryTextColor),
                                      ),
                                      const SizedBox(height: 4),
                                      Text(
                                        _accountNumberController.text.trim(),
                                        style: const TextStyle(
                                          color: accentColor,
                                          fontWeight: FontWeight.bold,
                                          fontSize: 18,
                                        ),
                                      ),
                                    ],
                                  ],
                                ),
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
                            onPressed: _isFinishing ? null : _finishPayment,
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
