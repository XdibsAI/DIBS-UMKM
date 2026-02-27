import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/social_provider.dart';
import 'package:flutter/services.dart'; // Tambahkan ini

class SocialScreen extends StatefulWidget {
  const SocialScreen({super.key});

  @override
  State<SocialScreen> createState() => _SocialScreenState();
}

class _SocialScreenState extends State<SocialScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  late AnimationController _glowController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    
    _glowController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat(reverse: true);

    // Load posts on init
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<SocialProvider>().loadPosts();
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _glowController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0A0A0F),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF0A0A0F), Color(0xFF050507)],
          ),
        ),
        child: NestedScrollView(
          headerSliverBuilder: (context, innerBoxIsScrolled) {
            return [
              SliverAppBar(
                expandedHeight: 120,
                floating: false,
                pinned: true,
                backgroundColor: const Color(0xFF050507),
                flexibleSpace: FlexibleSpaceBar(
                  title: const Text(
                    'SOCIAL MEDIA',
                    style: TextStyle(
                      color: Color(0xFFFF44AA),
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 2,
                    ),
                  ),
                  background: Container(
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                        colors: [Color(0xFFFF44AA), Color(0xFF9D4DFF)],
                      ).withOpacity(0.1),
                    ),
                  ),
                ),
                bottom: TabBar(
                  controller: _tabController,
                  indicatorColor: const Color(0xFFFF44AA),
                  indicatorWeight: 3,
                  labelColor: const Color(0xFFFF44AA),
                  unselectedLabelColor: const Color(0xFF8888AA),
                  tabs: const [
                    Tab(text: 'POSTS'),
                    Tab(text: 'AI TOOLS'),
                    Tab(text: 'SCHEDULE'),
                  ],
                ),
              ),
            ];
          },
          body: Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topCenter,
                end: Alignment.bottomCenter,
                colors: [Color(0xFF0A0A0F), Color(0xFF050507)],
              ),
            ),
            child: TabBarView(
              controller: _tabController,
              children: const [
                PostsTab(),
                AIToolsTab(),
                ScheduleTab(),
              ],
            ),
          ),
        ),
      ),
      floatingActionButton: AnimatedBuilder(
        animation: _glowController,
        builder: (context, child) {
          return Container(
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFFFF44AA).withOpacity(_glowController.value * 0.5),
                  blurRadius: 20,
                  spreadRadius: 5,
                ),
              ],
            ),
            child: FloatingActionButton(
              onPressed: () => _showCreatePostDialog(context),
              backgroundColor: const Color(0xFFFF44AA),
              child: const Icon(Icons.add, color: Color(0xFF0A0A0F)),
            ),
          );
        },
      ),
    );
  }

  void _showCreatePostDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => const CreatePostDialog(),
    );
  }
}

// Posts Tab
class PostsTab extends StatelessWidget {
  const PostsTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<SocialProvider>(
      builder: (context, provider, child) {
        if (provider.isLoading) {
          return const Center(
            child: CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Color(0xFFFF44AA)),
            ),
          );
        }

        if (provider.posts.isEmpty) {
          return Center(
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
                    Icons.photo_library_outlined,
                    size: 64,
                    color: Color(0xFFFF44AA),
                  ),
                ),
                const SizedBox(height: 24),
                const Text(
                  'BELUM ADA POSTS',
                  style: TextStyle(
                    color: Color(0xFFFF44AA),
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 2,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Buat post pertama Anda!',
                  style: TextStyle(
                    color: const Color(0xFF8888AA).withOpacity(0.8),
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          );
        }

        return RefreshIndicator(
          onRefresh: () => provider.loadPosts(),
          color: const Color(0xFFFF44AA),
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: provider.posts.length,
            itemBuilder: (context, index) {
              final post = provider.posts[index];
              return PostCard(post: post);
            },
          ),
        );
      },
    );
  }
}

// AI Tools Tab
class AIToolsTab extends StatefulWidget {
  const AIToolsTab({super.key});

  @override
  State<AIToolsTab> createState() => _AIToolsTabState();
}

class _AIToolsTabState extends State<AIToolsTab> with SingleTickerProviderStateMixin {
  final _topicController = TextEditingController();
  String _selectedPlatform = 'instagram';
  String _selectedTone = 'casual';
  
  late AnimationController _glowController;
  late Animation<double> _glowAnimation;

  @override
  void initState() {
    super.initState();
    _glowController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat(reverse: true);
    
    _glowAnimation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(parent: _glowController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _topicController.dispose();
    _glowController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<SocialProvider>(
      builder: (context, provider, child) {
        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Topic Input dengan style cyber
              Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: const Color(0xFFFF44AA).withOpacity(0.3),
                  ),
                ),
                child: TextField(
                  controller: _topicController,
                  style: const TextStyle(color: Color(0xFFE0E0FF)),
                  decoration: InputDecoration(
                    labelText: 'TOPIC / DESCRIPTION',
                    labelStyle: const TextStyle(color: Color(0xFFFF44AA)),
                    hintText: 'Contoh: sunset di pantai, promo produk baru...',
                    hintStyle: TextStyle(
                      color: const Color(0xFF8888AA).withOpacity(0.5),
                    ),
                    filled: true,
                    fillColor: const Color(0xFF050507),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.all(16),
                  ),
                  maxLines: 3,
                ),
              ),
              const SizedBox(height: 20),

              // Platform Selector
              Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: const Color(0xFFFF44AA).withOpacity(0.3),
                  ),
                ),
                child: DropdownButtonFormField<String>(
                  value: _selectedPlatform,
                  dropdownColor: const Color(0xFF12121A),
                  style: const TextStyle(color: Color(0xFFE0E0FF)),
                  decoration: InputDecoration(
                    labelText: 'PLATFORM',
                    labelStyle: const TextStyle(color: Color(0xFFFF44AA)),
                    filled: true,
                    fillColor: const Color(0xFF050507),
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(12),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  ),
                  items: ['instagram', 'facebook', 'twitter', 'linkedin', 'tiktok']
                      .map((p) => DropdownMenuItem(
                            value: p,
                            child: Row(
                              children: [
                                _getPlatformIcon(p),
                                const SizedBox(width: 8),
                                Text(p.toUpperCase()),
                              ],
                            ),
                          ))
                      .toList(),
                  onChanged: (val) => setState(() => _selectedPlatform = val!),
                ),
              ),
              const SizedBox(height: 24),

              // Generate Caption Button dengan efek glow
              AnimatedBuilder(
                animation: _glowAnimation,
                builder: (context, child) {
                  return Container(
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFFFF44AA).withOpacity(_glowAnimation.value * 0.3),
                          blurRadius: 15,
                          spreadRadius: 2,
                        ),
                      ],
                    ),
                    child: ElevatedButton.icon(
                      onPressed: provider.isGenerating
                          ? null
                          : () {
                              if (_topicController.text.isNotEmpty) {
                                provider.generateCaption(
                                  topic: _topicController.text,
                                  tone: _selectedTone,
                                  platform: _selectedPlatform,
                                );
                              }
                            },
                      icon: provider.isGenerating
                          ? const SizedBox(
                              width: 20,
                              height: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF0A0A0F)),
                              ),
                            )
                          : const Icon(Icons.auto_awesome, color: Color(0xFF0A0A0F)),
                      label: Text(
                        provider.isGenerating ? 'GENERATING...' : 'GENERATE CAPTION',
                        style: const TextStyle(
                          color: Color(0xFF0A0A0F),
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1,
                        ),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFFF44AA),
                        padding: const EdgeInsets.all(16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        elevation: 0,
                      ),
                    ),
                  );
                },
              ),
              const SizedBox(height: 12),

              // Generate Hashtags Button
              ElevatedButton.icon(
                onPressed: provider.isGenerating
                    ? null
                    : () {
                        if (_topicController.text.isNotEmpty) {
                          provider.suggestHashtags(
                            topic: _topicController.text,
                            platform: _selectedPlatform,
                          );
                        }
                      },
                icon: const Icon(Icons.tag, color: Color(0xFFE0E0FF)),
                label: const Text(
                  'SUGGEST HASHTAGS',
                  style: TextStyle(
                    color: Color(0xFFE0E0FF),
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF9D4DFF),
                  padding: const EdgeInsets.all(16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  elevation: 4,
                  shadowColor: const Color(0xFF9D4DFF).withOpacity(0.5),
                ),
              ),
              const SizedBox(height: 24),

              // Results
              if (provider.generatedCaption.isNotEmpty) ...[
                _buildResultSection(
                  title: 'GENERATED CAPTION',
                  color: const Color(0xFFFF44AA),
                  content: provider.generatedCaption,
                  onCopy: () {
                    // Copy functionality
                  },
                ),
                const SizedBox(height: 16),
              ],

              if (provider.suggestedHashtags.isNotEmpty) ...[
                _buildResultSection(
                  title: 'SUGGESTED HASHTAGS',
                  color: const Color(0xFF9D4DFF),
                  hashtags: provider.suggestedHashtags,
                ),
              ],
            ],
          ),
        );
      },
    );
  }

  Widget _getPlatformIcon(String platform) {
    IconData iconData;
    switch (platform) {
      case 'instagram':
        iconData = Icons.photo_camera;
        break;
      case 'facebook':
        iconData = Icons.facebook;
        break;
      case 'twitter':
        iconData = Icons.alternate_email;
        break;
      case 'linkedin':
        iconData = Icons.business_center;
        break;
      case 'tiktok':
        iconData = Icons.music_note;
        break;
      default:
        iconData = Icons.public;
    }
    return Icon(iconData, color: const Color(0xFFFF44AA), size: 18);
  }

  Widget _buildResultSection({
    required String title,
    required Color color,
    String? content,
    List<String>? hashtags,
    VoidCallback? onCopy,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [color.withOpacity(0.1), const Color(0xFF050507)],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3), width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: TextStyle(
                  color: color,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1,
                ),
              ),
              if (content != null)
                IconButton(
                  icon: Icon(Icons.copy, color: color, size: 20),
                  onPressed: onCopy,
                ),
            ],
          ),
          const SizedBox(height: 12),
          if (content != null)
            SelectableText(
              content,
              style: const TextStyle(
                color: Color(0xFFE0E0FF),
                fontSize: 14,
                height: 1.6,
              ),
            ),
          if (hashtags != null)
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: hashtags.map((tag) => Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: color.withOpacity(0.3)),
                ),
                child: Text(
                  tag,
                  style: TextStyle(color: color, fontSize: 13),
                ),
              )).toList(),
            ),
        ],
      ),
    );
  }
}

// Schedule Tab
class ScheduleTab extends StatelessWidget {
  const ScheduleTab({super.key});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(
                color: const Color(0xFF00FFFF).withOpacity(0.3),
                width: 2,
              ),
            ),
            child: const Icon(
              Icons.calendar_month,
              size: 64,
              color: Color(0xFF00FFFF),
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'SCHEDULE CALENDAR',
            style: TextStyle(
              color: Color(0xFF00FFFF),
              fontSize: 18,
              fontWeight: FontWeight.bold,
              letterSpacing: 2,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Coming Soon',
            style: TextStyle(
              color: const Color(0xFF8888AA).withOpacity(0.8),
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }
}

// Post Card Widget
class PostCard extends StatelessWidget {
  final Map<String, dynamic> post;

  const PostCard({super.key, required this.post});

  Color _getPlatformColor(String platform) {
    switch (platform.toLowerCase()) {
      case 'instagram':
        return const Color(0xFFFF44AA);
      case 'facebook':
        return const Color(0xFF00D9FF);
      case 'twitter':
        return const Color(0xFF00FFFF);
      case 'linkedin':
        return const Color(0xFF9D4DFF);
      case 'tiktok':
        return const Color(0xFF00FFAA);
      default:
        return const Color(0xFFFF44AA);
    }
  }

  @override
  Widget build(BuildContext context) {
    final platform = post['platform'] ?? 'unknown';
    final platformColor = _getPlatformColor(platform);

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF12121A), Color(0xFF0A0A0F)],
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: platformColor.withOpacity(0.3), width: 1),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: platformColor.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: platformColor.withOpacity(0.3)),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        _getPlatformIcon(platform),
                        color: platformColor,
                        size: 14,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        platform.toUpperCase(),
                        style: TextStyle(
                          color: platformColor,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.delete_outline, color: Colors.red),
                  onPressed: () {
                    showDialog(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        backgroundColor: const Color(0xFF12121A),
                        title: const Text(
                          'HAPUS POST',
                          style: TextStyle(color: Color(0xFFFF44AA)),
                        ),
                        content: const Text(
                          'Yakin ingin menghapus post ini?',
                          style: TextStyle(color: Color(0xFFE0E0FF)),
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(20),
                          side: const BorderSide(color: Color(0xFFFF44AA), width: 0.5),
                        ),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.pop(ctx),
                            style: TextButton.styleFrom(
                              foregroundColor: const Color(0xFF8888AA),
                            ),
                            child: const Text('BATAL'),
                          ),
                          TextButton(
                            onPressed: () {
                              Navigator.pop(ctx);
                              context.read<SocialProvider>().deletePost(post['id']);
                            },
                            style: TextButton.styleFrom(
                              foregroundColor: const Color(0xFFFF44AA),
                            ),
                            child: const Text('HAPUS'),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              post['caption'] ?? '',
              style: const TextStyle(
                color: Color(0xFFE0E0FF),
                fontSize: 14,
                height: 1.5,
              ),
              maxLines: 3,
              overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: post['status'] == 'published'
                        ? const Color(0xFF00FFAA).withOpacity(0.15)
                        : const Color(0xFFFF44AA).withOpacity(0.15),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: post['status'] == 'published'
                          ? const Color(0xFF00FFAA).withOpacity(0.3)
                          : const Color(0xFFFF44AA).withOpacity(0.3),
                    ),
                  ),
                  child: Text(
                    'Status: ${post['status'] ?? 'draft'}'.toUpperCase(),
                    style: TextStyle(
                      color: post['status'] == 'published'
                          ? const Color(0xFF00FFAA)
                          : const Color(0xFFFF44AA),
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  IconData _getPlatformIcon(String platform) {
    switch (platform.toLowerCase()) {
      case 'instagram':
        return Icons.photo_camera;
      case 'facebook':
        return Icons.facebook;
      case 'twitter':
        return Icons.alternate_email;
      case 'linkedin':
        return Icons.business_center;
      case 'tiktok':
        return Icons.music_note;
      default:
        return Icons.public;
    }
  }
}

// Create Post Dialog
class CreatePostDialog extends StatefulWidget {
  const CreatePostDialog({super.key});

  @override
  State<CreatePostDialog> createState() => _CreatePostDialogState();
}

class _CreatePostDialogState extends State<CreatePostDialog> {
  final _captionController = TextEditingController();
  String _selectedPlatform = 'instagram';
  bool _isSaving = false;

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      backgroundColor: const Color(0xFF12121A),
      title: const Text(
        'BUAT POST BARU',
        style: TextStyle(
          color: Color(0xFFFF44AA),
          fontWeight: FontWeight.bold,
          letterSpacing: 1,
        ),
      ),
      content: SingleChildScrollView(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Platform Selector
            Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: const Color(0xFFFF44AA).withOpacity(0.3),
                ),
              ),
              child: DropdownButtonFormField<String>(
                value: _selectedPlatform,
                dropdownColor: const Color(0xFF12121A),
                style: const TextStyle(color: Color(0xFFE0E0FF)),
                decoration: InputDecoration(
                  labelText: 'PLATFORM',
                  labelStyle: const TextStyle(color: Color(0xFFFF44AA)),
                  filled: true,
                  fillColor: const Color(0xFF050507),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                ),
                items: ['instagram', 'facebook', 'twitter', 'linkedin', 'tiktok']
                    .map((p) => DropdownMenuItem(
                          value: p,
                          child: Text(p.toUpperCase()),
                        ))
                    .toList(),
                onChanged: (val) => setState(() => _selectedPlatform = val!),
              ),
            ),
            const SizedBox(height: 16),

            // Caption Input
            Container(
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: const Color(0xFFFF44AA).withOpacity(0.3),
                ),
              ),
              child: TextField(
                controller: _captionController,
                style: const TextStyle(color: Color(0xFFE0E0FF)),
                decoration: InputDecoration(
                  labelText: 'CAPTION',
                  labelStyle: const TextStyle(color: Color(0xFFFF44AA)),
                  hintText: 'Tulis caption post Anda...',
                  hintStyle: TextStyle(
                    color: const Color(0xFF8888AA).withOpacity(0.5),
                  ),
                  filled: true,
                  fillColor: const Color(0xFF050507),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: BorderSide.none,
                  ),
                  contentPadding: const EdgeInsets.all(16),
                ),
                maxLines: 5,
              ),
            ),
          ],
        ),
      ),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: Color(0xFFFF44AA), width: 0.5),
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          style: TextButton.styleFrom(
            foregroundColor: const Color(0xFF8888AA),
          ),
          child: const Text('BATAL'),
        ),
        ElevatedButton(
          onPressed: _isSaving
              ? null
              : () async {
                  if (_captionController.text.isEmpty) return;
                  
                  setState(() => _isSaving = true);
                  
                  // Simulate saving
                  await Future.delayed(const Duration(seconds: 1));
                  
                  if (!context.mounted) return;
                  Navigator.pop(context);
                  
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('✅ Post berhasil dibuat'),
                      backgroundColor: Color(0xFF12121A),
                      behavior: SnackBarBehavior.floating,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.all(Radius.circular(12)),
                        side: BorderSide(color: Color(0xFFFF44AA), width: 0.5),
                      ),
                    ),
                  );
                },
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFFFF44AA),
            foregroundColor: const Color(0xFF0A0A0F),
          ),
          child: _isSaving
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF0A0A0F)),
                  ),
                )
              : const Text('BUAT'),
        ),
      ],
    );
  }

  @override
  void dispose() {
    _captionController.dispose();
    super.dispose();
  }
}
