import 'dart:async';

import 'package:flutter/material.dart';

import '../../services/api_service.dart';
import '../../services/video_studio_api.dart';
import '../video_player_screen.dart';
import 'video_studio_screen.dart';

class VideoProjectsScreen extends StatefulWidget {
  const VideoProjectsScreen({super.key});

  @override
  State<VideoProjectsScreen> createState() => _VideoProjectsScreenState();
}

class _VideoProjectsScreenState extends State<VideoProjectsScreen> {
  final List<Map<String, dynamic>> _videos = [];
  bool _isLoading = true;
  Timer? _refreshTimer;

  @override
  void initState() {
    super.initState();
    _loadVideos();
    _refreshTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      if (mounted) {
        _loadVideos(silent: true);
      }
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  String _cleanTitle(String raw) {
    var s = raw.trim();
    s = s.replaceAll('**', '');
    s = s.replaceAll('"', '');
    s = s.replaceFirst(RegExp(r'^judul\s*:\s*', caseSensitive: false), '');
    if (s.contains('\n')) {
      s = s.split('\n').first.trim();
    }
    if (s.length > 60) {
      s = '${s.substring(0, 60)}...';
    }
    return s.isEmpty ? 'Video' : s;
  }

  Future<void> _loadVideos({bool silent = false}) async {
    if (!silent) {
      setState(() => _isLoading = true);
    }

    final res = await VideoStudioApi.getVideoProjects();
    if (!mounted) return;

    final data = List<Map<String, dynamic>>.from(res['data'] ?? []);
    setState(() {
      _videos
        ..clear()
        ..addAll(data);
      _isLoading = false;
    });
  }

  Future<void> _openStudio() async {
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const VideoStudioScreen()),
    );
    if (mounted) {
      _loadVideos();
    }
  }

  Future<void> _downloadVideo(Map<String, dynamic> item) async {
    final id = (item['id'] ?? '').toString();
    if (id.isEmpty) return;

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Sedang menyimpan video ke Download/DIBS_Videos...'),
      ),
    );

    try {
      final videoPath = await ApiService.downloadVideo(id);

      if (!mounted) return;

      if (videoPath != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Video tersimpan di: $videoPath'),
            duration: const Duration(seconds: 4),
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Gagal simpan video'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Gagal simpan video: $e'),
          backgroundColor: Colors.red,
          duration: const Duration(seconds: 5),
        ),
      );
    }
  }

  Future<void> _deleteVideo(Map<String, dynamic> item) async {
    final id = (item['id'] ?? '').toString();
    if (id.isEmpty) return;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Hapus Video'),
        content: const Text('Video ini akan dihapus permanen.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Hapus'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    final res = await VideoStudioApi.deleteVideoProject(id);
    if (!mounted) return;

    final ok = (res['status'] ?? '').toString() == 'success';
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          ok
              ? 'Video dihapus'
              : (res['message']?.toString() ?? 'Gagal hapus video'),
        ),
      ),
    );

    await _loadVideos();
  }

  void _openVideo(Map<String, dynamic> item) {
    final url = (item['video_url'] ?? item['download_url'] ?? '').toString();
    if (url.isEmpty) return;

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => VideoPlayerScreen(
          videoUrl: url,
          title: _cleanTitle(
            (item['prompt'] ?? item['niche'] ?? item['title'] ?? 'Video')
                .toString(),
          ),
        ),
      ),
    );
  }

  Color _statusColor(String status) {
    switch (status) {
      case 'completed':
        return Colors.green;
      case 'failed':
        return Colors.red;
      case 'video_rendering':
        return Colors.orange;
      case 'planning':
      case 'processing':
      case 'script_generating':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  String _statusLabel(String status) {
    switch (status) {
      case 'completed':
        return 'Selesai';
      case 'failed':
        return 'Gagal';
      case 'video_rendering':
        return 'Rendering';
      case 'planning':
        return 'Planning';
      case 'processing':
        return 'Processing';
      case 'script_generating':
        return 'Narasi';
      default:
        return status.isEmpty ? 'Unknown' : status;
    }
  }

  Widget _buildItem(Map<String, dynamic> item) {
    final status = (item['status'] ?? '').toString();
    final title = _cleanTitle(
      (item['prompt'] ?? item['niche'] ?? item['title'] ?? 'Video tanpa judul')
          .toString(),
    );
    final thumb = (item['thumbnail_url'] ?? '').toString();
    final updatedAt = (item['updated_at'] ?? '').toString();

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            ClipRRect(
              borderRadius: BorderRadius.circular(10),
              child: Container(
                width: 92,
                height: 120,
                color: Colors.black12,
                child: thumb.isNotEmpty
                    ? Image.network(
                        thumb,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) =>
                            const Icon(Icons.movie, size: 36),
                      )
                    : const Icon(Icons.movie, size: 36),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: _statusColor(status).withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: Text(
                      _statusLabel(status),
                      style: TextStyle(
                        color: _statusColor(status),
                        fontWeight: FontWeight.w600,
                        fontSize: 12,
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                  if (updatedAt.isNotEmpty)
                    Text(
                      updatedAt,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  const SizedBox(height: 8),
                  if (status == 'completed' ||
                      status == 'failed' ||
                      status == 'failed')
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        ElevatedButton.icon(
                          onPressed: () => _openVideo(item),
                          icon: const Icon(Icons.play_arrow),
                          label: const Text('Lihat'),
                        ),
                        OutlinedButton.icon(
                          onPressed: () => _downloadVideo(item),
                          icon: const Icon(Icons.download),
                          label: const Text('Download'),
                        ),
                        OutlinedButton.icon(
                          onPressed: () => _deleteVideo(item),
                          icon: const Icon(Icons.delete_outline,
                              color: Colors.red),
                          label: const Text('Delete'),
                        ),
                      ],
                    )
                  else if (status == 'failed')
                    Text(
                      (item['error_message'] ?? 'Render gagal').toString(),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(color: Colors.red),
                    )
                  else
                    const Text(
                      'Sedang diproses otomatis...',
                      style: TextStyle(color: Colors.orange),
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Video Saya'),
        actions: [
          IconButton(
            onPressed: _loadVideos,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _videos.isEmpty
              ? const Center(
                  child: Text(
                    'Belum ada video.\nKlik + untuk buat video baru.',
                    textAlign: TextAlign.center,
                  ),
                )
              : RefreshIndicator(
                  onRefresh: _loadVideos,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: _videos.length,
                    itemBuilder: (_, i) => _buildItem(_videos[i]),
                  ),
                ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _openStudio,
        icon: const Icon(Icons.add),
        label: const Text('Buat Video'),
      ),
    );
  }
}
