import 'dart:async';
import 'package:flutter/material.dart';
import '../../services/api_service.dart';

class VideoStudioScreen extends StatefulWidget {
  const VideoStudioScreen({super.key});

  @override
  State<VideoStudioScreen> createState() => _VideoStudioScreenState();
}

class _VideoStudioScreenState extends State<VideoStudioScreen> {
  bool _isLoading = true;
  bool _isCreating = false;
  List<Map<String, dynamic>> _projects = [];
  Timer? _pollTimer;

  @override
  void initState() {
    super.initState();
    _loadProjects();
    _pollTimer = Timer.periodic(const Duration(seconds: 10), (_) {
      _loadProjects(showLoader: false);
    });
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> _loadProjects({bool showLoader = true}) async {
    if (showLoader && mounted) {
      setState(() => _isLoading = true);
    }

    try {
      final res = await ApiService.getVideoProjects();
      final status = res['status']?.toString() ?? '';

      if (status == 'success') {
        final raw = res['data'];
        final items = <Map<String, dynamic>>[];

        if (raw is List) {
          for (final item in raw) {
            if (item is Map) {
              items
                  .add(Map<String, dynamic>.from(item.cast<String, dynamic>()));
            }
          }
        }

        if (mounted) {
          setState(() {
            _projects = items;
          });
        }
      }
    } catch (_) {
      // keep silent, screen already has refresh affordance
    } finally {
      if (showLoader && mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'completed':
        return Colors.green;
      case 'failed':
        return Colors.red;
      case 'planning':
      case 'processing':
      case 'script_generating':
      case 'audio_generating':
      case 'video_rendering':
      case 'pending':
        return Colors.orange;
      default:
        return Colors.blueGrey;
    }
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'pending':
        return 'Menunggu';
      case 'planning':
        return 'Planning';
      case 'processing':
        return 'Processing';
      case 'script_generating':
        return 'Buat Script';
      case 'audio_generating':
        return 'Buat Audio';
      case 'video_rendering':
        return 'Render Video';
      case 'completed':
        return 'Selesai';
      case 'failed':
        return 'Gagal';
      default:
        return status;
    }
  }

  Future<void> _showCreateVideoDialog() async {
    final promptController = TextEditingController();
    final productController = TextEditingController();
    final priceController = TextEditingController();
    final ctaController =
        TextEditingController(text: 'Order via WhatsApp sekarang');
    final brandController = TextEditingController(text: 'Toko DIBS');
    final imageController = TextEditingController();

    int duration = 15;
    String style = 'premium';
    String language = 'id';
    bool advancedOpen = true;

    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: const Color(0xFF121212),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return StatefulBuilder(
          builder: (ctx, setModalState) {
            return Padding(
              padding: EdgeInsets.only(
                left: 20,
                right: 20,
                top: 20,
                bottom: MediaQuery.of(ctx).viewInsets.bottom + 20,
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Video Studio',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 22,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Tulis prompt video. Proses akan jalan di background, kamu tetap bisa pakai fitur lain.',
                      style:
                          TextStyle(color: Colors.grey.shade400, fontSize: 13),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: promptController,
                      maxLines: 4,
                      style: const TextStyle(color: Colors.white),
                      decoration: InputDecoration(
                        hintText:
                            'Contoh: Buat video promo keripik pisang 15 detik gaya premium untuk Ramadan',
                        hintStyle: TextStyle(color: Colors.grey.shade500),
                        filled: true,
                        fillColor: const Color(0xFF1E1E1E),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12),
                          borderSide: BorderSide.none,
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    InkWell(
                      onTap: () =>
                          setModalState(() => advancedOpen = !advancedOpen),
                      child: Row(
                        children: [
                          Icon(
                            advancedOpen
                                ? Icons.expand_less
                                : Icons.expand_more,
                            color: Colors.white70,
                          ),
                          const SizedBox(width: 8),
                          const Text(
                            'Advanced Options',
                            style: TextStyle(
                                color: Colors.white70,
                                fontWeight: FontWeight.w600),
                          ),
                        ],
                      ),
                    ),
                    if (advancedOpen) ...[
                      const SizedBox(height: 12),
                      TextField(
                        controller: productController,
                        style: const TextStyle(color: Colors.white),
                        decoration: _inputDecoration('Nama Produk'),
                      ),
                      const SizedBox(height: 10),
                      TextField(
                        controller: priceController,
                        style: const TextStyle(color: Colors.white),
                        decoration: _inputDecoration(
                            'Harga / Promo (contoh: Rp 12.000)'),
                      ),
                      const SizedBox(height: 10),
                      TextField(
                        controller: ctaController,
                        style: const TextStyle(color: Colors.white),
                        decoration: _inputDecoration('CTA'),
                      ),
                      const SizedBox(height: 10),
                      TextField(
                        controller: brandController,
                        style: const TextStyle(color: Colors.white),
                        decoration: _inputDecoration('Brand / Nama Toko'),
                      ),
                      const SizedBox(height: 10),
                      TextField(
                        controller: imageController,
                        style: const TextStyle(color: Colors.white),
                        decoration: _inputDecoration(
                            'Product Image URL / path (opsional)'),
                      ),
                      const SizedBox(height: 14),
                      Row(
                        children: [
                          Expanded(
                            child: DropdownButtonFormField<int>(
                              value: duration,
                              dropdownColor: const Color(0xFF1E1E1E),
                              style: const TextStyle(color: Colors.white),
                              decoration: _inputDecoration('Durasi'),
                              items: const [
                                DropdownMenuItem(
                                    value: 15, child: Text('15 detik')),
                                DropdownMenuItem(
                                    value: 30, child: Text('30 detik')),
                                DropdownMenuItem(
                                    value: 60, child: Text('60 detik')),
                              ],
                              onChanged: (v) =>
                                  setModalState(() => duration = v ?? 15),
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: DropdownButtonFormField<String>(
                              value: style,
                              dropdownColor: const Color(0xFF1E1E1E),
                              style: const TextStyle(color: Colors.white),
                              decoration: _inputDecoration('Style'),
                              items: const [
                                DropdownMenuItem(
                                    value: 'premium', child: Text('Premium')),
                                DropdownMenuItem(
                                    value: 'engaging', child: Text('Engaging')),
                                DropdownMenuItem(
                                    value: 'cinematic',
                                    child: Text('Cinematic')),
                                DropdownMenuItem(
                                    value: 'formal', child: Text('Formal')),
                              ],
                              onChanged: (v) =>
                                  setModalState(() => style = v ?? 'premium'),
                            ),
                          ),
                        ],
                      ),
                    ],
                    const SizedBox(height: 20),
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: _isCreating
                            ? null
                            : () async {
                                final prompt = promptController.text.trim();
                                if (prompt.isEmpty) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(
                                        content: Text('Prompt wajib diisi')),
                                  );
                                  return;
                                }

                                Navigator.pop(ctx);

                                setState(() => _isCreating = true);

                                try {
                                  final res =
                                      await ApiService.createVideoProject(
                                    prompt: prompt,
                                    duration: duration,
                                    style: style,
                                    language: language,
                                    productName: productController.text.trim(),
                                    priceText: priceController.text.trim(),
                                    ctaText: ctaController.text.trim(),
                                    brandName: brandController.text.trim(),
                                    productImageUrl:
                                        imageController.text.trim(),
                                  );

                                  final ok =
                                      res['status']?.toString() == 'success';
                                  if (!mounted) return;

                                  if (ok) {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      const SnackBar(
                                        content: Text(
                                            'Video sedang dibuat di background'),
                                        behavior: SnackBarBehavior.floating,
                                      ),
                                    );
                                    await _loadProjects(showLoader: false);
                                  } else {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      SnackBar(
                                        content: Text(
                                            res['message']?.toString() ??
                                                'Gagal membuat video'),
                                        backgroundColor: Colors.red,
                                      ),
                                    );
                                  }
                                } finally {
                                  if (mounted) {
                                    setState(() => _isCreating = false);
                                  }
                                }
                              },
                        icon: _isCreating
                            ? const SizedBox(
                                width: 18,
                                height: 18,
                                child:
                                    CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.auto_awesome),
                        label:
                            Text(_isCreating ? 'Memproses...' : 'Buat Video'),
                      ),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  InputDecoration _inputDecoration(String label) {
    return InputDecoration(
      labelText: label,
      labelStyle: TextStyle(color: Colors.grey.shade400),
      filled: true,
      fillColor: const Color(0xFF1E1E1E),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide.none,
      ),
    );
  }

  Future<void> _downloadProject(Map<String, dynamic> project) async {
    final projectId =
        project['project_id']?.toString() ?? project['id']?.toString() ?? '';
    if (projectId.isEmpty) return;

    final path = await ApiService.downloadVideo(projectId);
    if (!mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          path != null ? 'Video disimpan: $path' : 'Gagal download video',
        ),
        backgroundColor: path != null ? null : Colors.red,
      ),
    );
  }

  Future<void> _deleteProject(Map<String, dynamic> project) async {
    final projectId =
        project['project_id']?.toString() ?? project['id']?.toString() ?? '';
    if (projectId.isEmpty) return;

    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Hapus Project'),
        content: const Text('Yakin mau hapus project video ini?'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Batal')),
          ElevatedButton(
              onPressed: () => Navigator.pop(ctx, true),
              child: const Text('Hapus')),
        ],
      ),
    );

    if (ok != true) return;

    final res = await ApiService.deleteVideoProject(projectId);
    if (!mounted) return;

    final success = res['status']?.toString() == 'success';
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(success ? 'Project dihapus' : 'Gagal hapus project'),
        backgroundColor: success ? null : Colors.red,
      ),
    );

    if (success) {
      await _loadProjects(showLoader: false);
    }
  }

  Widget _buildProjectCard(Map<String, dynamic> project) {
    final status = project['status']?.toString() ?? '-';
    final thumbnailUrl = project['thumbnail_url']?.toString();
    final prompt = project['prompt']?.toString() ??
        project['niche']?.toString() ??
        'Untitled';
    final type = project['type']?.toString() ?? 'general';
    final duration = project['duration']?.toString() ?? '-';
    final updatedAt = project['updated_at']?.toString() ?? '';

    return Card(
      color: const Color(0xFF171717),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      margin: const EdgeInsets.only(bottom: 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (thumbnailUrl != null && thumbnailUrl.isNotEmpty)
            ClipRRect(
              borderRadius:
                  const BorderRadius.vertical(top: Radius.circular(16)),
              child: SizedBox(
                height: 180,
                width: double.infinity,
                child: Image.network(
                  thumbnailUrl,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => _thumbFallback(),
                ),
              ),
            )
          else
            _thumbFallback(),
          Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: [
                    _chip(type.toUpperCase(), Colors.blueGrey),
                    _chip(_statusLabel(status), _statusColor(status)),
                    _chip('$duration dtk', Colors.deepPurple),
                  ],
                ),
                const SizedBox(height: 10),
                Text(
                  prompt,
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                  ),
                ),
                const SizedBox(height: 8),
                if (updatedAt.isNotEmpty)
                  Text(
                    'Updated: $updatedAt',
                    style: TextStyle(color: Colors.grey.shade500, fontSize: 12),
                  ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    if (status == 'completed')
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () => _downloadProject(project),
                          icon: const Icon(Icons.download),
                          label: const Text('Download'),
                        ),
                      )
                    else
                      Expanded(
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              vertical: 12, horizontal: 12),
                          decoration: BoxDecoration(
                            color: const Color(0xFF232323),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            'Video sedang dibuat di background. Kamu bisa lanjut pakai fitur lain.',
                            style: TextStyle(
                              color: Colors.grey.shade300,
                              fontSize: 12,
                            ),
                          ),
                        ),
                      ),
                    const SizedBox(width: 10),
                    IconButton(
                      onPressed: () => _deleteProject(project),
                      icon: const Icon(Icons.delete_outline,
                          color: Colors.redAccent),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _thumbFallback() {
    return Container(
      height: 180,
      width: double.infinity,
      decoration: const BoxDecoration(
        color: Color(0xFF222222),
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      child: const Center(
        child: Icon(Icons.movie_creation_outlined,
            color: Colors.white54, size: 46),
      ),
    );
  }

  Widget _chip(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.16),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withOpacity(0.55)),
      ),
      child: Text(
        text,
        style:
            TextStyle(color: color, fontWeight: FontWeight.w700, fontSize: 11),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF101010),
      appBar: AppBar(
        title: const Text('Video Studio'),
        backgroundColor: const Color(0xFF101010),
        actions: [
          IconButton(
            onPressed: () => _loadProjects(),
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showCreateVideoDialog,
        icon: const Icon(Icons.auto_awesome),
        label: const Text('Buat Video'),
      ),
      body: RefreshIndicator(
        onRefresh: _loadProjects,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : _projects.isEmpty
                ? ListView(
                    padding: const EdgeInsets.all(24),
                    children: [
                      const SizedBox(height: 80),
                      Icon(Icons.movie_filter_outlined,
                          size: 64, color: Colors.grey.shade600),
                      const SizedBox(height: 16),
                      const Text(
                        'Belum ada project video',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 18,
                            fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Mulai dari prompt. Video akan dibuat di background dan thumbnail akan muncul di sini.',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Colors.grey.shade400),
                      ),
                    ],
                  )
                : ListView.builder(
                    padding: const EdgeInsets.fromLTRB(16, 16, 16, 100),
                    itemCount: _projects.length,
                    itemBuilder: (_, i) => _buildProjectCard(_projects[i]),
                  ),
      ),
    );
  }
}
