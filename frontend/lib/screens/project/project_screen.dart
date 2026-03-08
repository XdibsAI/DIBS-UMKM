import 'package:flutter/material.dart';
import 'dart:io';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../../providers/project_provider.dart';
import '../../services/api_service.dart';
import '../../utils/date_utils.dart';
import '../toko/toko_screen.dart';

class ProjectScreen extends StatefulWidget {
  const ProjectScreen({super.key});

  @override
  State<ProjectScreen> createState() => _ProjectScreenState();
}

class _ProjectScreenState extends State<ProjectScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this); // UBAH: 2 -> 3
    WidgetsBinding.instance.addPostFrameCallback((_) {
      Provider.of<ProjectProvider>(context, listen: false).loadAll();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Projects & Catatan'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(icon: Icon(Icons.video_library), text: 'Video Projects'),
            Tab(icon: Icon(Icons.auto_stories), text: 'Catatan Harian'),
            Tab(icon: Icon(Icons.store), text: 'Toko'), // TAMBAH: Tab Toko
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [
          VideoProjectsTab(),
          KnowledgeTab(),
          TokoScreen(),  // TAMBAHKAN INI
        ],
      ),
    );
  }
}

// ==================== VIDEO PROJECTS TAB ====================
class VideoProjectsTab extends StatelessWidget {
  const VideoProjectsTab({super.key});

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<ProjectProvider>(context);

    if (provider.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (provider.videoProjects.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.video_library_outlined, size: 72, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            Text('Belum ada video project', style: TextStyle(fontSize: 18, color: Colors.grey.shade500, fontWeight: FontWeight.w500)),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => _showCreateVideoDialog(context),
              icon: const Icon(Icons.add),
              label: const Text('Buat Video Project'),
              style: ElevatedButton.styleFrom(backgroundColor: Colors.blue.shade700, foregroundColor: Colors.white, padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12)),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadAll(),
      child: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: provider.videoProjects.length,
        itemBuilder: (context, index) => VideoProjectCard(project: provider.videoProjects[index]),
      ),
    );
  }
}

class VideoProjectCard extends StatelessWidget {
  final Map<String, dynamic> project;
  const VideoProjectCard({super.key, required this.project});

  @override
  Widget build(BuildContext context) {
    final status = project['status'] ?? 'pending';
    final Color statusColor = status == 'completed' ? Colors.green : status == 'failed' ? Colors.red : Colors.orange;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.video_library, color: Colors.blue.shade700),
                const SizedBox(width: 8),
                Expanded(child: Text(project['niche'] ?? 'Video Project', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold))),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(color: statusColor.withOpacity(0.1), borderRadius: BorderRadius.circular(12)),
                  child: Text(status.toUpperCase(), style: TextStyle(fontSize: 10, color: statusColor, fontWeight: FontWeight.bold)),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text('Duration: ${project['duration'] ?? 60}s', style: TextStyle(color: Colors.grey.shade600)),
            Text('Style: ${project['style'] ?? 'engaging'}', style: TextStyle(color: Colors.grey.shade600)),
            if (project['error'] != null) ...[
              const SizedBox(height: 8),
              Text('Error: ${project['error']}', style: const TextStyle(color: Colors.red, fontSize: 12)),
            ],
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                if (status == 'completed')
                  IconButton(
                    icon: const Icon(Icons.download, size: 20),
                    onPressed: () => _downloadVideo(context, project['id']),
                    tooltip: 'Download Video',
                    color: Colors.green.shade700,
                  ),
                if (project['script'] != null)
                  IconButton(
                    icon: const Icon(Icons.description_outlined, size: 20),
                    onPressed: () => _showScriptDialog(context, project),
                    tooltip: 'Lihat Script',
                    color: Colors.blue.shade700,
                  ),
                IconButton(
                  icon: const Icon(Icons.share_outlined, size: 20),
                  onPressed: () => _shareVideoProject(context, project),
                  tooltip: 'Share',
                  color: Colors.blue.shade700,
                ),
                IconButton(
                  icon: const Icon(Icons.delete_outline, size: 20),
                  onPressed: () => _deleteVideoProject(context, project),
                  tooltip: 'Hapus',
                  color: Colors.red.shade700,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

// ==================== KNOWLEDGE TAB ====================
class KnowledgeTab extends StatefulWidget {
  const KnowledgeTab({super.key});

  @override
  State<KnowledgeTab> createState() => _KnowledgeTabState();
}

class _KnowledgeTabState extends State<KnowledgeTab> {
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        context.read<ProjectProvider>().loadKnowledge();
      }
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _showAddDialog(BuildContext context) async {
    final provider = Provider.of<ProjectProvider>(context, listen: false);
    final contentController = TextEditingController();
    String category = 'general';

    await showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Tambah Catatan'),
        content: StatefulBuilder(
          builder: (context, setState) => Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: contentController,
                maxLines: 4,
                decoration: const InputDecoration(
                  labelText: 'Isi catatan',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: category,
                items: const [
                  DropdownMenuItem(value: 'general', child: Text('General')),
                  DropdownMenuItem(value: 'finance', child: Text('Finance')),
                  DropdownMenuItem(value: 'schedule', child: Text('Schedule')),
                  DropdownMenuItem(value: 'technical', child: Text('Technical')),
                  DropdownMenuItem(value: 'health', child: Text('Health')),
                ],
                onChanged: (v) => setState(() => category = v ?? 'general'),
                decoration: const InputDecoration(
                  labelText: 'Kategori',
                  border: OutlineInputBorder(),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () async {
              final ok = await provider.addKnowledge(
                contentController.text.trim(),
                category: category,
              );
              if (!context.mounted) return;
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(ok ? 'Catatan ditambahkan' : 'Gagal menambah catatan'),
                  backgroundColor: ok ? Colors.green : Colors.red,
                ),
              );
            },
            child: const Text('Simpan'),
          ),
        ],
      ),
    );
  }

  Widget _buildBody(ProjectProvider provider, BuildContext context) {
    if (provider.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (provider.knowledge.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.auto_stories_outlined, size: 72, color: Colors.grey.shade300),
            const SizedBox(height: 16),
            Text(
              'Belum ada catatan',
              style: TextStyle(
                fontSize: 18,
                color: Colors.grey.shade500,
                fontWeight: FontWeight.w500,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Ceritakan aktivitasmu ke Dibs\ndan catatan otomatis akan tersimpan di sini',
              style: TextStyle(fontSize: 14, color: Colors.grey.shade400),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: () => _showAddDialog(context),
              icon: const Icon(Icons.add),
              label: const Text('Tambah Catatan'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () => provider.loadKnowledge(search: _searchController.text.trim()),
      child: ListView.builder(
        padding: const EdgeInsets.all(12),
        itemCount: provider.knowledge.length,
        itemBuilder: (context, index) => KnowledgeCard(item: Map<String, dynamic>.from(provider.knowledge[index])),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<ProjectProvider>(context);

    return Scaffold(
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(12, 12, 12, 8),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    onSubmitted: (v) => provider.loadKnowledge(search: v.trim()),
                    decoration: InputDecoration(
                      hintText: 'Cari catatan...',
                      prefixIcon: const Icon(Icons.search),
                      suffixIcon: _searchController.text.isEmpty
                          ? null
                          : IconButton(
                              icon: const Icon(Icons.clear),
                              onPressed: () {
                                _searchController.clear();
                                provider.loadKnowledge();
                                setState(() {});
                              },
                            ),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    onChanged: (_) => setState(() {}),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  onPressed: () => _showAddDialog(context),
                  icon: const Icon(Icons.add),
                ),
              ],
            ),
          ),
          Expanded(child: _buildBody(provider, context)),
        ],
      ),
      floatingActionButton: provider.knowledge.isNotEmpty
          ? FloatingActionButton.extended(
              onPressed: () => _showReportDialog(context, provider),
              icon: const Icon(Icons.assessment_outlined),
              label: const Text('Laporan'),
              backgroundColor: Colors.blue.shade700,
            )
          : null,
    );
  }
}

class KnowledgeCard extends StatelessWidget {
  final Map<String, dynamic> item;
  const KnowledgeCard({super.key, required this.item});

  Color _categoryColor(String category) {
    switch (category) {
      case 'finance':
        return Colors.green;
      case 'health':
        return Colors.red;
      case 'schedule':
        return Colors.blue;
      case 'credential':
        return Colors.purple;
      case 'technical':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  Future<void> _showEditDialog(BuildContext context) async {
    final provider = Provider.of<ProjectProvider>(context, listen: false);
    final contentController = TextEditingController(text: item['content'] ?? '');
    String category = (item['category'] ?? 'general').toString();

    await showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Edit Catatan'),
        content: StatefulBuilder(
          builder: (context, setState) => Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: contentController,
                maxLines: 4,
                decoration: const InputDecoration(
                  labelText: 'Isi catatan',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<String>(
                value: category,
                items: const [
                  DropdownMenuItem(value: 'general', child: Text('General')),
                  DropdownMenuItem(value: 'finance', child: Text('Finance')),
                  DropdownMenuItem(value: 'schedule', child: Text('Schedule')),
                  DropdownMenuItem(value: 'technical', child: Text('Technical')),
                  DropdownMenuItem(value: 'health', child: Text('Health')),
                ],
                onChanged: (v) => setState(() => category = v ?? 'general'),
                decoration: const InputDecoration(
                  labelText: 'Kategori',
                  border: OutlineInputBorder(),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () async {
              final ok = await provider.updateKnowledgeItem(
                int.parse(item['id'].toString()),
                contentController.text.trim(),
                category: category,
              );
              if (!context.mounted) return;
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text(ok ? 'Catatan diupdate' : 'Gagal update catatan'),
                  backgroundColor: ok ? Colors.green : Colors.red,
                ),
              );
            },
            child: const Text('Update'),
          ),
        ],
      ),
    );
  }

  Future<void> _delete(BuildContext context) async {
    final provider = Provider.of<ProjectProvider>(context, listen: false);

    final confirm = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Hapus Catatan'),
        content: const Text('Yakin ingin menghapus catatan ini?'),
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

    if (confirm != true) return;

    final ok = await provider.deleteKnowledgeItem(int.parse(item['id'].toString()));
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(ok ? 'Catatan dihapus' : 'Gagal menghapus catatan'),
        backgroundColor: ok ? Colors.green : Colors.red,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final category = item['category'] ?? 'general';
    final color = _categoryColor(category.toString());

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Chip(
                  label: Text(category.toString()),
                  backgroundColor: color.withOpacity(0.12),
                  labelStyle: TextStyle(color: color, fontWeight: FontWeight.w600),
                ),
                const Spacer(),
                IconButton(
                  icon: const Icon(Icons.edit_outlined),
                  onPressed: () => _showEditDialog(context),
                  tooltip: 'Edit',
                ),
                IconButton(
                  icon: const Icon(Icons.delete_outline),
                  onPressed: () => _delete(context),
                  tooltip: 'Hapus',
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              item['content'] ?? '',
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500),
            ),
            const SizedBox(height: 10),
            Text(
              item['created_at']?.toString() ?? '',
              style: TextStyle(fontSize: 12, color: Colors.grey.shade500),
            ),
          ],
        ),
      ),
    );
  }
}


void _showReportDialog(BuildContext context, ProjectProvider provider) {
  showModalBottomSheet(
    context: context,
    shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
    builder: (ctx) => SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Generate Laporan', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.today),
              title: const Text('Hari Ini'),
              onTap: () {
                Navigator.pop(ctx);
                _generateAndShowReport(context, provider, 'today');
              },
            ),
            ListTile(
              leading: const Icon(Icons.date_range),
              title: const Text('Minggu Ini'),
              onTap: () {
                Navigator.pop(ctx);
                _generateAndShowReport(context, provider, 'week');
              },
            ),
            ListTile(
              leading: const Icon(Icons.calendar_month),
              title: const Text('Bulan Ini'),
              onTap: () {
                Navigator.pop(ctx);
                _generateAndShowReport(context, provider, 'month');
              },
            ),
          ],
        ),
      ),
    ),
  );
}

Future<void> _generateAndShowReport(BuildContext context, ProjectProvider provider, String period) async {
  showDialog(
    context: context,
    barrierDismissible: false,
    builder: (ctx) => const Center(child: CircularProgressIndicator()),
  );
  final reportData = await provider.generateReport(period);
  if (!context.mounted) return;
  Navigator.pop(context);
  if (reportData == null) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(provider.error ?? 'Gagal generate laporan'), backgroundColor: Colors.red),
    );
    return;
  }
  showDialog(
    context: context,
    builder: (ctx) => AlertDialog(
      title: Text(reportData['title'] ?? 'Laporan'),
      content: SingleChildScrollView(child: SelectableText(reportData['report'] ?? '', style: const TextStyle(fontSize: 14, height: 1.6))),
      actions: [
        TextButton(
          onPressed: () {
            Clipboard.setData(ClipboardData(text: reportData['report'] ?? ''));
            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Laporan disalin'), duration: Duration(seconds: 1)));
          },
          child: const Text('Salin'),
        ),
        TextButton(
          onPressed: () async {
            Navigator.pop(ctx);
            await _downloadPDF(context, period);
          },
          style: TextButton.styleFrom(foregroundColor: Colors.blue.shade700),
          child: const Text('Download PDF'),
        ),
        TextButton(
          onPressed: () => Navigator.pop(ctx),
          child: const Text('Tutup'),
        ),
      ],
    ),
  );
}

Future<void> _downloadPDF(BuildContext context, String period) async {
  showDialog(
    context: context,
    barrierDismissible: false,
    builder: (ctx) => const Center(child: Column(mainAxisSize: MainAxisSize.min, children: [CircularProgressIndicator(), SizedBox(height: 16), Text('Membuat PDF...', style: TextStyle(color: Colors.white))])),
  );
  try {
    final pdfBytes = await ApiService.downloadReportPDF(period: period);
    if (!context.mounted) return;
    Navigator.pop(context);
    if (pdfBytes == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Gagal download PDF'), backgroundColor: Colors.red));
      return;
    }
    final directory = Directory('/storage/emulated/0/Download');
    if (!await directory.exists()) await directory.create(recursive: true);
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final file = File('${directory.path}/laporan_${period}_$timestamp.pdf');
    await file.writeAsBytes(pdfBytes);
    if (!context.mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('PDF tersimpan di:\n${file.path}'), duration: const Duration(seconds: 3)));
  } catch (e) {
    if (context.mounted) {
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red));
    }
  }
}

// Video helper functions
Future<void> _downloadVideo(BuildContext context, String projectId) async {
  showDialog(
    context: context,
    barrierDismissible: false,
    builder: (ctx) => const Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text('Downloading video...', style: TextStyle(color: Colors.white)),
        ],
      ),
    ),
  );

  try {
    final videoPath = await ApiService.downloadVideo(projectId);

    if (!context.mounted) return;
    Navigator.pop(context);

    if (videoPath != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Video tersimpan: $videoPath'),
          duration: const Duration(seconds: 3),
          action: SnackBarAction(
            label: 'OK',
            onPressed: () {},
          ),
        ),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Gagal download video'), backgroundColor: Colors.red),
      );
    }
  } catch (e) {
    if (context.mounted) {
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
      );
    }
  }
}

void _showScriptDialog(BuildContext context, Map<String, dynamic> project) {
  final script = project['script'];
  if (script == null) return;

  showDialog(
    context: context,
    builder: (ctx) => AlertDialog(
      title: Text(script['title'] ?? 'Video Script'),
      content: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('HOOK:', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.blue.shade700)),
            Text(script['hook'] ?? ''),
            const SizedBox(height: 12),
            Text('BODY:', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.blue.shade700)),
            Text(script['body'] ?? ''),
            const SizedBox(height: 12),
            Text('CTA:', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.blue.shade700)),
            Text(script['cta'] ?? ''),
          ],
        ),
      ),
      actions: [
        TextButton(
          onPressed: () {
            Clipboard.setData(ClipboardData(text: '${script['hook']}\n\n${script['body']}\n\n${script['cta']}'));
            ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Script disalin')));
          },
          child: const Text('Salin'),
        ),
        TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Tutup')),
      ],
    ),
  );
}

void _shareVideoProject(BuildContext context, Map<String, dynamic> project) {
  final script = project['script'];
  if (script == null) {
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Script belum tersedia')));
    return;
  }

  final shareText = '''🎬 VIDEO SCRIPT: ${script['title']}

📌 HOOK:
${script['hook']}

📝 BODY:
${script['body']}

🎯 CTA:
${script['cta']}

⏱️ Duration: ${project['duration']}s
🎨 Style: ${project['style']}

--- Generated by DIBS AI ---''';

  Clipboard.setData(ClipboardData(text: shareText));
  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Script disalin! Paste ke WhatsApp/Email untuk share'), duration: Duration(seconds: 2)));
}

Future<void> _deleteVideoProject(BuildContext context, Map<String, dynamic> project) async {
  final confirm = await showDialog<bool>(
    context: context,
    builder: (ctx) => AlertDialog(
      title: const Text('Hapus Video Project'),
      content: Text('Yakin ingin menghapus project "${project['niche']}"?'),
      actions: [
        TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Batal')),
        TextButton(
          onPressed: () => Navigator.pop(ctx, true),
          style: TextButton.styleFrom(foregroundColor: Colors.red),
          child: const Text('Hapus'),
        ),
      ],
    ),
  );

  if (confirm != true) return;

  showDialog(
    context: context,
    barrierDismissible: false,
    builder: (ctx) => const Center(child: CircularProgressIndicator()),
  );

  try {
    await ApiService.deleteVideoProject(project['id']);

    if (!context.mounted) return;
    Navigator.pop(context);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('✅ Project dihapus'), duration: Duration(seconds: 1)),
    );

    Provider.of<ProjectProvider>(context, listen: false).loadAll();
  } catch (e) {
    if (context.mounted) {
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
      );
    }
  }
}

void _showCreateVideoDialog(BuildContext context) {
  final nicheController = TextEditingController();
  int duration = 60;

  showDialog(
    context: context,
    builder: (ctx) => StatefulBuilder(
      builder: (context, setState) => AlertDialog(
        title: const Text('Buat Video Project'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: nicheController, decoration: const InputDecoration(labelText: 'Niche/Topic', hintText: 'tips produktivitas')),
            const SizedBox(height: 16),
            Row(
              children: [
                const Text('Duration: '),
                Expanded(
                  child: Slider(
                    value: duration.toDouble(),
                    min: 15,
                    max: 180,
                    divisions: 11,
                    label: '${duration}s',
                    onChanged: (val) => setState(() => duration = val.toInt()),
                  ),
                ),
                Text('${duration}s'),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Batal')),
          ElevatedButton(
            onPressed: () async {
              if (nicheController.text.isEmpty) return;
              Navigator.pop(ctx);
              showDialog(
                context: context,
                barrierDismissible: false,
                builder: (ctx) => const Center(child: CircularProgressIndicator()),
              );
              try {
                final result = await ApiService.createVideoProject(niche: nicheController.text, duration: duration);
                if (!context.mounted) return;
                Navigator.pop(context);
                if (result['status'] == 'success') {
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('✅ Video project dibuat!')));
                  Provider.of<ProjectProvider>(context, listen: false).loadAll();
                }
              } catch (e) {
                if (context.mounted) {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red));
                }
              }
            },
            child: const Text('Buat'),
          ),
        ],
      ),
    ),
  );
}
