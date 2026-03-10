import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../../services/video_studio_api.dart';

class VideoStudioScreen extends StatefulWidget {
  const VideoStudioScreen({super.key});

  @override
  State<VideoStudioScreen> createState() => _VideoStudioScreenState();
}

class _VideoStudioScreenState extends State<VideoStudioScreen> {
  final _promptController = TextEditingController();
  final _productNameController = TextEditingController();
  final _priceController = TextEditingController();
  final _ctaController = TextEditingController(text: 'Order sekarang');
  final _brandController = TextEditingController(text: 'Dibs AI');

  final _imagePicker = ImagePicker();

  bool _isSubmitting = false;
  bool _isUploadingImages = false;
  String _selectedStyle = 'premium';
  String _selectedLanguage = 'id';

  final List<String> _selectedImagePaths = [];
  List<String> _uploadedImagePaths = [];
  Map<String, dynamic>? _lastCreatedProject;

  Future<void> _pickAndUploadImages() async {
    try {
      final files = await _imagePicker.pickMultiImage(imageQuality: 92);
      if (files.isEmpty) return;

      setState(() {
        _isUploadingImages = true;
        _selectedImagePaths
          ..clear()
          ..addAll(files.map((e) => e.path));
      });

      final res = await VideoStudioApi.uploadVideoImages(_selectedImagePaths);
      if (!mounted) return;

      if ((res['status']?.toString() ?? '') == 'success') {
        final data = Map<String, dynamic>.from(res['data'] ?? {});
        final imagePaths = List<String>.from(data['image_paths'] ?? []);

        setState(() {
          _uploadedImagePaths = imagePaths;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content: Text('${imagePaths.length} gambar berhasil diupload')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(res['message']?.toString() ?? 'Upload gagal')),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Upload gagal: $e')),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isUploadingImages = false;
        });
      }
    }
  }

  void _removeSelectedImage(int index) {
    setState(() {
      if (index >= 0 && index < _selectedImagePaths.length) {
        _selectedImagePaths.removeAt(index);
      }
      if (index >= 0 && index < _uploadedImagePaths.length) {
        _uploadedImagePaths.removeAt(index);
      }
    });
  }

  Future<void> _submit() async {
    final prompt = _promptController.text.trim();
    if (prompt.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Prompt wajib diisi')),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      final result = await VideoStudioApi.createVideoProject(
        niche: prompt,
        duration: 15,
        style: _selectedStyle,
        language: _selectedLanguage,
        prompt: prompt,
        productName: _productNameController.text.trim().isEmpty
            ? null
            : _productNameController.text.trim(),
        priceText: _priceController.text.trim().isEmpty
            ? null
            : _priceController.text.trim(),
        ctaText: _ctaController.text.trim().isEmpty
            ? null
            : _ctaController.text.trim(),
        brandName: _brandController.text.trim().isEmpty
            ? null
            : _brandController.text.trim(),
        uploadedImagePath:
            _uploadedImagePaths.isNotEmpty ? _uploadedImagePaths.first : null,
        uploadedImagePaths:
            _uploadedImagePaths.isNotEmpty ? _uploadedImagePaths : null,
      );

      if (!mounted) return;

      if ((result['status']?.toString() ?? '') == 'success') {
        final data = Map<String, dynamic>.from(result['data'] ?? {});
        setState(() {
          _lastCreatedProject = data;
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content: Text(
                  'Project dibuat: ${data['project_id'] ?? data['id'] ?? '-'}')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content:
                  Text(result['message']?.toString() ?? 'Gagal membuat video')),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Gagal membuat video: $e')),
      );
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  Widget _buildPreviewGrid() {
    if (_selectedImagePaths.isEmpty) {
      return const SizedBox.shrink();
    }

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: _selectedImagePaths.length,
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        crossAxisSpacing: 10,
        mainAxisSpacing: 10,
      ),
      itemBuilder: (context, index) {
        final path = _selectedImagePaths[index];
        return Stack(
          children: [
            Positioned.fill(
              child: ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.file(
                  File(path),
                  fit: BoxFit.cover,
                ),
              ),
            ),
            Positioned(
              right: 4,
              top: 4,
              child: InkWell(
                onTap: () => _removeSelectedImage(index),
                child: Container(
                  padding: const EdgeInsets.all(4),
                  decoration: const BoxDecoration(
                    color: Colors.black54,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.close, color: Colors.white, size: 16),
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  @override
  void dispose() {
    _promptController.dispose();
    _productNameController.dispose();
    _priceController.dispose();
    _ctaController.dispose();
    _brandController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final projectId = _lastCreatedProject?['project_id']?.toString() ??
        _lastCreatedProject?['id']?.toString();

    return Scaffold(
      appBar: AppBar(title: const Text('Video Studio')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextField(
            controller: _promptController,
            minLines: 4,
            maxLines: 8,
            decoration: const InputDecoration(
              labelText: 'Prompt Video Lengkap',
              hintText:
                  'Bisa promo, motivasi, edukasi, tutorial. Bisa format: Judul, Durasi, Tema, Struktur Narasi, Visual & Musik, Tips Produksi.',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _productNameController,
            decoration: const InputDecoration(
              labelText: 'Nama Produk / Subjek',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _priceController,
            decoration: const InputDecoration(
              labelText: 'Harga',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _ctaController,
            decoration: const InputDecoration(
              labelText: 'CTA',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _brandController,
            decoration: const InputDecoration(
              labelText: 'Brand',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            initialValue: _selectedStyle,
            decoration: const InputDecoration(
              labelText: 'Style',
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(value: 'premium', child: Text('Premium')),
              DropdownMenuItem(value: 'engaging', child: Text('Engaging')),
              DropdownMenuItem(value: 'clean', child: Text('Clean')),
            ],
            onChanged: (v) {
              if (v != null) setState(() => _selectedStyle = v);
            },
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<String>(
            initialValue: _selectedLanguage,
            decoration: const InputDecoration(
              labelText: 'Bahasa',
              border: OutlineInputBorder(),
            ),
            items: const [
              DropdownMenuItem(value: 'id', child: Text('Indonesia')),
              DropdownMenuItem(value: 'en', child: Text('English')),
            ],
            onChanged: (v) {
              if (v != null) setState(() => _selectedLanguage = v);
            },
          ),
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              border: Border.all(color: Colors.cyanAccent),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'Gambar untuk dijadikan video',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 10),
                OutlinedButton.icon(
                  onPressed: (_isSubmitting || _isUploadingImages)
                      ? null
                      : _pickAndUploadImages,
                  icon: _isUploadingImages
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2))
                      : const Icon(Icons.collections_outlined),
                  label: Text(
                    _selectedImagePaths.isNotEmpty
                        ? 'Tambah / Ganti Gambar'
                        : 'Upload Banyak Gambar',
                  ),
                ),
                if (_selectedImagePaths.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  _buildPreviewGrid(),
                ],
                if (_uploadedImagePaths.isNotEmpty) ...[
                  const SizedBox(height: 10),
                  Text(
                    '${_uploadedImagePaths.length} gambar siap dipakai untuk auto scene',
                    style: TextStyle(
                      color: Colors.green.shade400,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: _isSubmitting ? null : _submit,
            icon: _isSubmitting
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.movie_creation_outlined),
            label: Text(_isSubmitting ? 'Memproses...' : 'Buat Video'),
          ),
          if (projectId != null) ...[
            const SizedBox(height: 20),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Text('Project ID: $projectId'),
              ),
            ),
          ],
        ],
      ),
    );
  }
}
