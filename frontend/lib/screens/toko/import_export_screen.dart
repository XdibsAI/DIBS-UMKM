import 'dart:io';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import '../../services/api_service.dart';

class ImportExportScreen extends StatefulWidget {
  const ImportExportScreen({super.key});

  @override
  State<ImportExportScreen> createState() => _ImportExportScreenState();
}

class _ImportExportScreenState extends State<ImportExportScreen> {
  bool _isImporting = false;
  bool _isExporting = false;
  String? _lastResult;

  Future<void> _importCSV() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['csv'],
      );

      if (result == null || result.files.single.path == null) return;

      setState(() {
        _isImporting = true;
        _lastResult = null;
      });

      final filePath = result.files.single.path!;
      final res = await ApiService.importProductsCSV(filePath);

      final status = res['status']?.toString() ?? '';
      if (!mounted) return;

      if (status == 'success') {
        final data = Map<String, dynamic>.from(res['data'] ?? {});
        final inserted = data['inserted'] ?? 0;
        final updated = data['updated'] ?? 0;
        final skipped = data['skipped'] ?? 0;
        final total = data['total_processed'] ?? 0;

        setState(() {
          _lastResult =
              'Import berhasil\n'
              'Inserted: $inserted\n'
              'Updated: $updated\n'
              'Skipped: $skipped\n'
              'Total: $total';
        });

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Import CSV berhasil'),
            behavior: SnackBarBehavior.floating,
          ),
        );

        await Future.delayed(const Duration(milliseconds: 300));
        if (!mounted) return;
        Navigator.pop(context, true);
      } else {
        final message = res['message']?.toString() ??
            res['detail']?.toString() ??
            'Import CSV gagal';

        setState(() {
          _lastResult = message;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(message),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _lastResult = 'Import error: $e';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Import error: $e'),
          backgroundColor: Colors.red,
          behavior: SnackBarBehavior.floating,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isImporting = false;
        });
      }
    }
  }

  Future<void> _exportCSV() async {
    try {
      setState(() {
        _isExporting = true;
        _lastResult = null;
      });

      final bytes = await ApiService.exportProductsCSV();
      if (!mounted) return;

      if (bytes == null) {
        throw Exception('Gagal export CSV');
      }

      Directory targetDir;
      final downloadDir = Directory('/storage/emulated/0/Download');
      if (await downloadDir.exists()) {
        targetDir = downloadDir;
      } else {
        targetDir = await getApplicationDocumentsDirectory();
      }

      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final file = File('${targetDir.path}/dibs_products_backup_$timestamp.csv');
      await file.writeAsBytes(bytes);

      setState(() {
        _lastResult = 'Export berhasil\nFile: ${file.path}';
      });

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Backup CSV disimpan di ${file.path}'),
          behavior: SnackBarBehavior.floating,
        ),
      );
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _lastResult = 'Export error: $e';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Export error: $e'),
          backgroundColor: Colors.red,
          behavior: SnackBarBehavior.floating,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isExporting = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final isBusy = _isImporting || _isExporting;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Import / Export Produk'),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const Text(
            'Kelola backup dan import produk toko',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 20),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Import CSV',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Pilih file CSV untuk insert/update produk secara massal.',
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: isBusy ? null : _importCSV,
                      icon: _isImporting
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.upload_file),
                      label: Text(_isImporting ? 'Mengimpor...' : 'Import CSV Produk'),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Export CSV',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Backup semua produk toko ke file CSV.',
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: isBusy ? null : _exportCSV,
                      icon: _isExporting
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Icon(Icons.download),
                      label: Text(_isExporting ? 'Mengekspor...' : 'Export Backup CSV'),
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (_lastResult != null) ...[
            const SizedBox(height: 16),
            Card(
              color: Colors.black12,
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Text(_lastResult!),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
