import '../toko/voice_scan_dialog.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import '../../utils/date_utils.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import '../../providers/chat_provider.dart';
import '../../providers/auth_provider.dart';
import '../../models/chat.dart';
import 'package:file_picker/file_picker.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> with SingleTickerProviderStateMixin {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  // Animation untuk efek cyber
  late AnimationController _glowController;
  late Animation<double> _glowAnimation;

  @override
  void initState() {
    super.initState();

    // Setup glow animation
    _glowController = AnimationController(
      duration: const Duration(seconds: 2),
      vsync: this,
    )..repeat(reverse: true);

    _glowAnimation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(parent: _glowController, curve: Curves.easeInOut),
    );

    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = Provider.of<ChatProvider>(context, listen: false);
      if (!provider.hasValidSession()) {
        provider.initializeUserSession();
      } else {
        provider.loadSessions();
      }
    });
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    _glowController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    if (_scrollController.hasClients) {
      _scrollController.animateTo(
        0,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }

  Future<void> _onSend() async {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;

    final provider = Provider.of<ChatProvider>(context, listen: false);
    _messageController.clear();

    final success = await provider.sendMessage(text);

    if (success) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _scrollToBottom();
      });
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(provider.error ?? 'Gagal mengirim pesan'),
            backgroundColor: Colors.red,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        );
      }
    }
  }

  Future<void> _createNewSession() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: Theme.of(context).brightness == Brightness.dark 
            ? const Color(0xFF12121A) 
            : Colors.white,
        title: Text(
          'Chat Baru',
          style: TextStyle(
            color: Theme.of(context).brightness == Brightness.dark 
                ? const Color(0xFF00FFFF) 
                : const Color(0xFF0088CC),
          ),
        ),
        content: Text(
          'Mulai percakapan baru? Chat saat ini akan disimpan ke riwayat.',
          style: TextStyle(
            color: Theme.of(context).brightness == Brightness.dark 
                ? const Color(0xFFE0E0FF) 
                : Colors.black87,
          ),
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: BorderSide(
            color: Theme.of(context).brightness == Brightness.dark 
                ? const Color(0xFF00FFFF) 
                : const Color(0xFF0088CC),
            width: 0.5,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            style: TextButton.styleFrom(
              foregroundColor: Theme.of(context).brightness == Brightness.dark 
                  ? const Color(0xFF8888AA) 
                  : Colors.grey.shade700,
            ),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: Theme.of(context).brightness == Brightness.dark 
                  ? const Color(0xFF00FFFF) 
                  : const Color(0xFF0088CC),
              foregroundColor: Theme.of(context).brightness == Brightness.dark 
                  ? const Color(0xFF0A0A0F) 
                  : Colors.white,
            ),
            child: const Text('Chat Baru'),
          ),
        ],
      ),
    );

    if (confirm == true && mounted) {
      final provider = Provider.of<ChatProvider>(context, listen: false);
      await provider.createSession();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('✨ Chat baru dimulai'),
            duration: Duration(seconds: 1),
            backgroundColor: Theme.of(context).brightness == Brightness.dark 
                ? const Color(0xFF12121A) 
                : Colors.white,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.all(Radius.circular(12)),
              side: BorderSide(
                color: Theme.of(context).brightness == Brightness.dark 
                    ? const Color(0xFF00FFFF) 
                    : const Color(0xFF0088CC),
                width: 0.5,
              ),
            ),
          ),
        );
      }
    }
  }

  Future<void> _deleteSession(String sessionId) async {
    final provider = Provider.of<ChatProvider>(context, listen: false);

    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Theme.of(context).brightness == Brightness.dark 
            ? const Color(0xFF12121A) 
            : Colors.white,
        title: Text(
          'Hapus Chat',
          style: TextStyle(
            color: Theme.of(context).brightness == Brightness.dark 
                ? const Color(0xFFFF44AA) 
                : Colors.red,
          ),
        ),
        content: Text(
          'Yakin ingin menghapus chat ini?',
          style: TextStyle(
            color: Theme.of(context).brightness == Brightness.dark 
                ? const Color(0xFFE0E0FF) 
                : Colors.black87,
          ),
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: BorderSide(
            color: Theme.of(context).brightness == Brightness.dark 
                ? const Color(0xFFFF44AA) 
                : Colors.red.shade300,
            width: 0.5,
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            style: TextButton.styleFrom(
              foregroundColor: Theme.of(context).brightness == Brightness.dark 
                  ? const Color(0xFF8888AA) 
                  : Colors.grey.shade700,
            ),
            child: const Text('Batal'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(
              foregroundColor: Theme.of(context).brightness == Brightness.dark 
                  ? const Color(0xFFFF44AA) 
                  : Colors.red,
            ),
            child: const Text('Hapus'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    final success = await provider.deleteSession(sessionId);
    if (!success && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(provider.error ?? 'Gagal menghapus'),
          backgroundColor: Colors.red,
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      );
    }
  }

  void _showCopyMenu(BuildContext ctx, String content) {
    final isDark = Theme.of(ctx).brightness == Brightness.dark;
    
    showModalBottomSheet(
      context: ctx,
      backgroundColor: isDark ? const Color(0xFF12121A) : Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        side: BorderSide(
          color: isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
          width: 0.5,
        ),
      ),
      builder: (sheetCtx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 8),
            Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: isDark 
                    ? const Color(0xFF00FFFF).withOpacity(0.3)
                    : Colors.grey.shade300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            ListTile(
              leading: Icon(
                Icons.copy, 
                color: isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
              ),
              title: Text(
                'Salin Pesan',
                style: TextStyle(
                  color: isDark ? const Color(0xFFE0E0FF) : Colors.black87,
                ),
              ),
              onTap: () {
                Clipboard.setData(ClipboardData(text: content));
                Navigator.pop(sheetCtx);
                ScaffoldMessenger.of(ctx).showSnackBar(
                  SnackBar(
                    content: Text('Pesan disalin'),
                    duration: Duration(seconds: 1),
                    backgroundColor: isDark ? const Color(0xFF12121A) : Colors.white,
                    behavior: SnackBarBehavior.floating,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.all(Radius.circular(12)),
                      side: BorderSide(
                        color: isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
                        width: 0.5,
                      ),
                    ),
                  ),
                );
              },
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }

  Widget _buildWelcome(String userName) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            AnimatedBuilder(
              animation: _glowAnimation,
              builder: (context, child) {
                return Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: (isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC))
                          .withOpacity(_glowAnimation.value),
                      width: 2,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: (isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC))
                            .withOpacity(_glowAnimation.value * 0.3),
                        blurRadius: 30,
                        spreadRadius: 10,
                      ),
                    ],
                  ),
                  child: Icon(
                    Icons.bolt,
                    color: isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
                    size: 48,
                  ),
                );
              },
            ),
            const SizedBox(height: 24),
            Text(
              'Halo, $userName! 👋',
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: isDark ? const Color(0xFFE0E0FF) : Colors.black87,
                letterSpacing: -0.5,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              'Ada yang bisa DIBS bantu hari ini?\nSilakan kirim pesan Anda.',
              style: TextStyle(
                fontSize: 16,
                color: isDark 
                    ? const Color(0xFF8888AA).withOpacity(0.8)
                    : Colors.grey.shade600,
                height: 1.5,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 32),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              alignment: WrapAlignment.center,
              children: [
                _buildSuggestionChip('💡 Bantu saya dengan ide', 
                    isDark ? const Color(0xFFFF44AA) : Colors.blue),
                _buildSuggestionChip('📝 Buatkan ringkasan', 
                    isDark ? const Color(0xFF9D4DFF) : Colors.purple),
                _buildSuggestionChip('🔍 Cari informasi', 
                    isDark ? const Color(0xFF00FFAA) : Colors.green),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSuggestionChip(String label, Color color) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return ActionChip(
      label: Text(
        label,
        style: TextStyle(
          fontSize: 13,
          color: isDark ? const Color(0xFFE0E0FF) : Colors.black87,
        ),
      ),
      backgroundColor: isDark ? const Color(0xFF050507) : Colors.grey.shade200,
      side: BorderSide(color: color.withOpacity(0.5), width: 1),
      onPressed: () {
        _messageController.text = label.substring(3);
        _onSend();
      },
    );
  }

  Widget _buildThinkingBubble(String text) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: (isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC))
                  .withOpacity(0.1),
              shape: BoxShape.circle,
              border: Border.all(
                color: isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
                width: 1,
              ),
            ),
            child: Icon(
              Icons.bolt,
              color: isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
              size: 16,
            ),
          ),
          const SizedBox(width: 12),
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF12121A) : Colors.grey.shade100,
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(20),
                  topRight: Radius.circular(20),
                  bottomRight: Radius.circular(20),
                  bottomLeft: Radius.circular(4),
                ),
                border: Border.all(
                  color: (isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC))
                      .withOpacity(0.3),
                  width: 0.5,
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation<Color>(
                        (isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC))
                            .withOpacity(_glowAnimation.value),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Flexible(
                    child: Text(
                      text,
                      style: TextStyle(
                        fontSize: 14,
                        color: isDark ? const Color(0xFFE0E0FF) : Colors.black87,
                        fontStyle: FontStyle.italic,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBubble(ChatMessage message) {
    final isUser = message.role == 'user';
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final h = message.timestamp.hour.toString().padLeft(2, '0');
    final m = message.timestamp.minute.toString().padLeft(2, '0');
    final timeString = '$h:$m';

    final hasMarkdown = !isUser &&
        (message.content.contains('|') ||
            message.content.contains('**') ||
            message.content.contains('\n-') ||
            message.content.contains('\n#') ||
            message.content.contains('📊'));

    // User bubble: abu-abu di dark mode, putih di light mode
    // AI bubble: cyan di dark mode, biru di light mode
    final bubbleColor = isUser
        ? (isDark ? Colors.grey.shade800 : Colors.grey.shade200)
        : (isDark 
            ? const Color(0xFF00FFFF).withOpacity(0.15) 
            : const Color(0xFF0088CC).withOpacity(0.1));

    final borderColor = isUser
        ? Colors.transparent
        : (isDark 
            ? const Color(0xFF00FFFF).withOpacity(0.5)
            : const Color(0xFF0088CC).withOpacity(0.5));

    final textColor = isUser
        ? (isDark ? Colors.white : Colors.black87)
        : (isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC));

    final timeTextColor = isUser
        ? (isDark ? Colors.grey.shade500 : Colors.grey.shade600)
        : (isDark 
            ? const Color(0xFF00FFFF).withOpacity(0.5)
            : const Color(0xFF0088CC).withOpacity(0.5));

    final copyIconColor = isUser
        ? (isDark ? Colors.grey.shade600 : Colors.grey.shade500)
        : (isDark 
            ? const Color(0xFF00FFFF).withOpacity(0.3)
            : const Color(0xFF0088CC).withOpacity(0.3));

    return GestureDetector(
      onLongPress: () => _showCopyMenu(context, message.content),
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
        child: Row(
          mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (!isUser) ...[
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: (isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC))
                      .withOpacity(0.1),
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
                    width: 1,
                  ),
                ),
                child: Icon(
                  Icons.bolt,
                  color: isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
                  size: 16,
                ),
              ),
              const SizedBox(width: 12),
            ],
            Flexible(
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: bubbleColor,
                  borderRadius: BorderRadius.only(
                    topLeft: const Radius.circular(20),
                    topRight: const Radius.circular(20),
                    bottomLeft: Radius.circular(isUser ? 20 : 4),
                    bottomRight: Radius.circular(isUser ? 4 : 20),
                  ),
                  border: Border.all(
                    color: borderColor,
                    width: 0.5,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (hasMarkdown)
                      MarkdownBody(
                        data: message.content,
                        selectable: true,
                        styleSheet: MarkdownStyleSheet(
                          p: TextStyle(
                            fontSize: 14,
                            color: isUser 
                                ? (isDark ? Colors.white : Colors.black87)
                                : (isDark ? const Color(0xFFE0E0FF) : Colors.black87),
                          ),
                          tableHead: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: isUser 
                                ? (isDark ? Colors.white : Colors.black87)
                                : (isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC)),
                            fontSize: 13,
                          ),
                          tableBody: TextStyle(
                            fontSize: 13,
                            color: isUser 
                                ? (isDark ? Colors.white70 : Colors.black87)
                                : (isDark ? const Color(0xFFE0E0FF) : Colors.black87),
                          ),
                          tableBorder: TableBorder.all(
                            color: isUser
                                ? (isDark ? Colors.grey.shade700 : Colors.grey.shade300)
                                : (isDark 
                                    ? const Color(0xFF00FFFF).withOpacity(0.3)
                                    : const Color(0xFF0088CC).withOpacity(0.3)),
                            width: 1,
                          ),
                          tableColumnWidth: const FlexColumnWidth(),
                          tableCellsPadding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                        ),
                      )
                    else
                      SelectableText(
                        message.content,
                        style: TextStyle(
                          fontSize: 14,
                          color: isUser 
                              ? (isDark ? Colors.white : Colors.black87)
                              : (isDark ? const Color(0xFFE0E0FF) : Colors.black87),
                          height: 1.5,
                        ),
                      ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          timeString,
                          style: TextStyle(
                            fontSize: 10,
                            color: timeTextColor,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Icon(
                          Icons.copy,
                          size: 12,
                          color: copyIconColor,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            if (isUser) ...[
              const SizedBox(width: 12),
              CircleAvatar(
                radius: 16,
                backgroundColor: isDark ? Colors.grey.shade700 : Colors.grey.shade300,
                child: Icon(
                  Icons.person,
                  size: 14,
                  color: isDark ? Colors.white : Colors.black54,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }


  void _showAttachmentMenu() {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    showModalBottomSheet(
      context: context,
      backgroundColor: isDark ? Colors.grey.shade900 : Colors.white,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'Pilih Jenis File',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: isDark ? Colors.white : Colors.black87,
                ),
              ),
              const SizedBox(height: 20),

              // 🖼️ Gambar untuk analisa
              ListTile(
                leading: CircleAvatar(
                  backgroundColor: Colors.blue,
                  child: const Icon(Icons.image, color: Colors.white),
                ),
                title: Text(
                  '📷 Gambar untuk Analisa',
                  style: TextStyle(color: isDark ? Colors.white : Colors.black87),
                ),
                subtitle: Text(
                  'JPG, PNG - DIBS akan analisa gambar',
                  style: TextStyle(
                    color: isDark ? Colors.grey.shade400 : Colors.grey.shade600,
                    fontSize: 12,
                  ),
                ),
                onTap: () {
                  Navigator.pop(ctx);
                  _pickImageForAnalysis();
                },
              ),

              Divider(color: isDark ? Colors.grey.shade800 : Colors.grey.shade300),

              // 📄 Dokumen
              ListTile(
                leading: CircleAvatar(
                  backgroundColor: Colors.orange,
                  child: const Icon(Icons.description, color: Colors.white),
                ),
                title: Text(
                  '📄 Dokumen',
                  style: TextStyle(color: isDark ? Colors.white : Colors.black87),
                ),
                subtitle: Text(
                  'PDF, DOC, CSV, TXT - DIBS akan baca isi',
                  style: TextStyle(
                    color: isDark ? Colors.grey.shade400 : Colors.grey.shade600,
                    fontSize: 12,
                  ),
                ),
                onTap: () {
                  Navigator.pop(ctx);
                  _pickDocument();
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _pickImageForAnalysis() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.image,
        allowMultiple: false,
      );

      if (result != null && result.files.isNotEmpty) {
        final fileName = result.files.single.name;

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('📤 Mengunggah gambar...')),
        );

        // TODO: Upload ke backend untuk analisa
        setState(() {
          _messageController.text = '🖼️ [Gambar terlampir: $fileName] - Tolong analisa gambar ini';
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('✅ Gambar siap dianalisa: $fileName')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('❌ Error: $e'), backgroundColor: Colors.red),
      );
    }
  }

  Future<void> _pickDocument() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf', 'doc', 'docx', 'csv', 'txt'],
        allowMultiple: false,
      );

      if (result != null && result.files.isNotEmpty) {
        final fileName = result.files.single.name;
        final fileSize = result.files.single.size;
        final fileSizeMB = (fileSize / 1024 / 1024).toStringAsFixed(2);

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('📤 Mengunggah dokumen...')),
        );

        // TODO: Upload ke backend
        setState(() {
          _messageController.text = '📄 [Dokumen terlampir: $fileName ($fileSizeMB MB)] - Tolong baca dan ringkas isi dokumen ini';
        });

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('✅ Dokumen siap dibaca: $fileName')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('❌ Error: $e'), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final auth = Provider.of<AuthProvider>(context, listen: false);
    final userName = auth.user?.displayName ?? 'Pengguna';
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Consumer<ChatProvider>(
      builder: (context, chatProvider, _) {
        return Scaffold(
          key: _scaffoldKey,
          backgroundColor: isDark ? const Color(0xFF0A0A0F) : const Color(0xFFF5F5F5),
          appBar: AppBar(
            title: AnimatedBuilder(
              animation: _glowAnimation,
              builder: (context, child) {
                return Text(
                  chatProvider.currentSession?['name'] ?? 'DIBS AI',
                  style: TextStyle(
                    color: (isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC))
                        .withOpacity(_glowAnimation.value),
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 1,
                    shadows: [
                      Shadow(
                        color: (isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC))
                            .withOpacity(_glowAnimation.value * 0.5),
                        blurRadius: 10,
                      ),
                    ],
                  ),
                );
              },
            ),
            backgroundColor: isDark ? const Color(0xFF050507) : Colors.white,
            foregroundColor: isDark ? const Color(0xFFE0E0FF) : Colors.black87,
            elevation: 0,
            leading: IconButton(
              icon: Icon(
                Icons.menu,
                color: isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
              ),
              onPressed: () => _scaffoldKey.currentState?.openDrawer(),
            ),
            actions: [
              IconButton(
                icon: Icon(
                  Icons.add_comment,
                  color: isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
                ),
                onPressed: _createNewSession,
                tooltip: 'Chat Baru',
              ),
            ],
          ),

          drawer: Drawer(
            backgroundColor: isDark ? const Color(0xFF0A0A0F) : Colors.white,
            child: Column(
              children: [
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.fromLTRB(20, 48, 20, 20),
                  decoration: BoxDecoration(
                    gradient: isDark
                        ? const LinearGradient(
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                            colors: [Color(0xFF00FFFF), Color(0xFF9D4DFF)],
                          )
                        : LinearGradient(
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                            colors: [const Color(0xFF0088CC), Colors.purple.shade300],
                          ),
                    borderRadius: const BorderRadius.only(
                      bottomLeft: Radius.circular(20),
                      bottomRight: Radius.circular(20),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'DIBS AI',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: isDark ? const Color(0xFF0A0A0F) : Colors.white,
                          letterSpacing: 2,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        userName,
                        style: TextStyle(
                          color: isDark ? const Color(0xFF0A0A0F) : Colors.white,
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Chat History',
                        style: TextStyle(
                          color: (isDark ? const Color(0xFF0A0A0F) : Colors.white)
                              .withOpacity(0.7),
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: chatProvider.isLoading
                      ? Center(
                          child: CircularProgressIndicator(
                            valueColor: AlwaysStoppedAnimation<Color>(
                              isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
                            ),
                          ),
                        )
                      : chatProvider.sessions.isEmpty
                          ? Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.history,
                                    size: 48,
                                    color: isDark 
                                        ? const Color(0xFF8888AA).withOpacity(0.5)
                                        : Colors.grey.shade400,
                                  ),
                                  const SizedBox(height: 16),
                                  Text(
                                    'Belum ada chat',
                                    style: TextStyle(
                                      color: isDark 
                                          ? const Color(0xFF8888AA).withOpacity(0.8)
                                          : Colors.grey.shade600,
                                    ),
                                  ),
                                ],
                              ),
                            )
                          : ListView.builder(
                              padding: const EdgeInsets.all(8),
                              itemCount: chatProvider.sessions.length,
                              itemBuilder: (context, index) {
                                final session = chatProvider.sessions[index];
                                final isSelected =
                                    chatProvider.currentSession?['session_id'] ==
                                        session['session_id'];

                                return Container(
                                  margin: const EdgeInsets.only(bottom: 4),
                                  decoration: BoxDecoration(
                                    color: isSelected
                                        ? (isDark 
                                            ? const Color(0xFF00FFFF).withOpacity(0.1)
                                            : const Color(0xFF0088CC).withOpacity(0.1))
                                        : null,
                                    borderRadius: BorderRadius.circular(12),
                                    border: isSelected
                                        ? Border.all(
                                            color: isDark 
                                                ? const Color(0xFF00FFFF)
                                                : const Color(0xFF0088CC),
                                            width: 0.5,
                                          )
                                        : null,
                                  ),
                                  child: ListTile(
                                    leading: Container(
                                      padding: const EdgeInsets.all(8),
                                      decoration: BoxDecoration(
                                        color: isSelected
                                            ? (isDark 
                                                ? const Color(0xFF00FFFF)
                                                : const Color(0xFF0088CC))
                                            : (isDark 
                                                ? const Color(0xFF8888AA).withOpacity(0.2)
                                                : Colors.grey.shade200),
                                        shape: BoxShape.circle,
                                      ),
                                      child: Icon(
                                        Icons.chat,
                                        size: 16,
                                        color: isSelected
                                            ? (isDark 
                                                ? const Color(0xFF0A0A0F)
                                                : Colors.white)
                                            : (isDark 
                                                ? const Color(0xFF00FFFF)
                                                : const Color(0xFF0088CC)),
                                      ),
                                    ),
                                    title: Text(
                                      session['name'],
                                      style: TextStyle(
                                        fontWeight: isSelected
                                            ? FontWeight.bold
                                            : FontWeight.normal,
                                        fontSize: 14,
                                        color: isSelected
                                            ? (isDark 
                                                ? const Color(0xFF00FFFF)
                                                : const Color(0xFF0088CC))
                                            : (isDark 
                                                ? const Color(0xFFE0E0FF)
                                                : Colors.black87),
                                      ),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                    subtitle: Text(
                                      '${session['message_count']} pesan',
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: isDark 
                                            ? const Color(0xFF8888AA).withOpacity(0.8)
                                            : Colors.grey.shade600,
                                      ),
                                    ),
                                    trailing: IconButton(
                                      icon: Icon(
                                        Icons.delete_outline,
                                        size: 18,
                                        color: isSelected
                                            ? (isDark 
                                                ? const Color(0xFFFF44AA)
                                                : Colors.red)
                                            : (isDark 
                                                ? const Color(0xFF8888AA)
                                                : Colors.grey.shade500),
                                      ),
                                      onPressed: () =>
                                          _deleteSession(session['session_id']),
                                    ),
                                    onTap: () {
                                      chatProvider.loadSession(session['session_id']);
                                      Navigator.pop(context);
                                    },
                                  ),
                                );
                              },
                            ),
                ),
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: ElevatedButton.icon(
                    onPressed: () {
                      Navigator.pop(context);
                      _createNewSession();
                    },
                    icon: Icon(
                      Icons.add,
                      color: isDark ? const Color(0xFF0A0A0F) : Colors.white,
                    ),
                    label: Text(
                      'Chat Baru',
                      style: TextStyle(
                        color: isDark ? const Color(0xFF0A0A0F) : Colors.white,
                      ),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: isDark 
                          ? const Color(0xFF00FFFF)
                          : const Color(0xFF0088CC),
                      minimumSize: const Size(double.infinity, 45),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      elevation: 4,
                      shadowColor: (isDark 
                          ? const Color(0xFF00FFFF)
                          : const Color(0xFF0088CC)).withOpacity(0.5),
                    ),
                  ),
                ),
              ],
            ),
          ),

          body: Container(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: isDark
                    ? [const Color(0xFF0A0A0F), const Color(0xFF050507)]
                    : [const Color(0xFFF5F5F5), Colors.white],
              ),
            ),
            child: Column(
              children: [
                Expanded(
                  child: chatProvider.isLoading
                      ? Center(
                          child: CircularProgressIndicator(
                            valueColor: AlwaysStoppedAnimation<Color>(
                              isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
                            ),
                          ),
                        )
                      : chatProvider.messages.isEmpty && !chatProvider.isThinking
                          ? _buildWelcome(userName)
                          : ListView.builder(
                              controller: _scrollController,
                              reverse: true,
                              padding: const EdgeInsets.all(12),
                              itemCount: chatProvider.messages.length +
                                  (chatProvider.isThinking ? 1 : 0),
                              itemBuilder: (context, index) {
                                if (chatProvider.isThinking && index == 0) {
                                  return _buildThinkingBubble(
                                      chatProvider.thinkingText);
                                }
                                final msgIndex =
                                    chatProvider.isThinking ? index - 1 : index;
                                final message = chatProvider.messages[
                                    chatProvider.messages.length - 1 - msgIndex];
                                return _buildBubble(message);
                              },
                            ),
                ),
                if (chatProvider.isSending)
                  LinearProgressIndicator(
                    backgroundColor: (isDark 
                        ? const Color(0xFF00FFFF)
                        : const Color(0xFF0088CC)).withOpacity(0.1),
                    valueColor: AlwaysStoppedAnimation<Color>(
                      isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
                    ),
                  ),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: isDark ? const Color(0xFF050507) : Colors.white,
                    border: Border(
                      top: BorderSide(
                        color: (isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC))
                            .withOpacity(0.3),
                      ),
                    ),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      // 📎 Upload button
                      IconButton(
                        icon: Icon(
                          Icons.attach_file,
                          color: isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
                          size: 24,
                        ),
                        onPressed: _showAttachmentMenu,
                        tooltip: 'Upload file',
                        padding: const EdgeInsets.all(8),
                      ),
                      // 🎤 Voice input button by Dibs
                      IconButton(
                        icon: Icon(
                          Icons.mic_rounded,
                          color: isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
                          size: 24,
                        ),
                        onPressed: () async {
                          final result = await showModalBottomSheet<String>(
                            context: context,
                            isScrollControlled: true,
                            backgroundColor: Colors.transparent,
                            builder: (context) => VoiceScanDialog(),
                          );
                          if (result != null && result.isNotEmpty) {
                            _messageController.text = result;
                            _onSend(); 
                          }
                        },
                        tooltip: 'Kirim pesan suara',
                        padding: const EdgeInsets.all(8),
                      ),
                      const SizedBox(width: 4),
                      Expanded(
                        child: TextField(
                          controller: _messageController,
                          maxLines: 5,
                          keyboardType: TextInputType.multiline,
                          minLines: 1,
                          enabled: !chatProvider.isSending,
                          style: TextStyle(
                            color: isDark ? const Color(0xFFE0E0FF) : Colors.black87,
                          ),
                          decoration: InputDecoration(
                            hintText: chatProvider.isSending
                                ? 'Menunggu balasan...'
                                : 'Tulis pesan...',
                            hintStyle: TextStyle(
                              color: isDark 
                                  ? const Color(0xFF8888AA).withOpacity(0.5)
                                  : Colors.grey.shade500,
                            ),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(24),
                              borderSide: BorderSide(
                                color: isDark 
                                    ? const Color(0xFF00FFFF)
                                    : const Color(0xFF0088CC),
                                width: 0.5,
                              ),
                            ),
                            enabledBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(24),
                              borderSide: BorderSide(
                                color: (isDark 
                                    ? const Color(0xFF00FFFF)
                                    : const Color(0xFF0088CC)).withOpacity(0.3),
                                width: 0.5,
                              ),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(24),
                              borderSide: BorderSide(
                                color: isDark 
                                    ? const Color(0xFF00FFFF)
                                    : const Color(0xFF0088CC),
                                width: 1.5,
                              ),
                            ),
                            filled: true,
                            fillColor: isDark 
                                ? const Color(0xFF0A0A0F)
                                : Colors.grey.shade100,
                            contentPadding: const EdgeInsets.symmetric(
                              horizontal: 20,
                              vertical: 12,
                            ),
                          ),
                          textInputAction: TextInputAction.newline,
                        ),
                      ),
                      const SizedBox(width: 12),
                      if (chatProvider.isSending)
                        Container(
                          width: 48,
                          height: 48,
                          decoration: BoxDecoration(
                            color: (isDark 
                                ? const Color(0xFF00FFFF)
                                : const Color(0xFF0088CC)).withOpacity(0.1),
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: (isDark 
                                  ? const Color(0xFF00FFFF)
                                  : const Color(0xFF0088CC)).withOpacity(0.3),
                              width: 1,
                            ),
                          ),
                          child: const Center(
                            child: SizedBox(
                              width: 24,
                              height: 24,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF00FFFF)),
                              ),
                            ),
                          ),
                        )
                      else
                        AnimatedBuilder(
                          animation: _glowAnimation,
                          builder: (context, child) {
                            return Container(
                              decoration: BoxDecoration(
                                gradient: RadialGradient(
                                  colors: [
                                    isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
                                    isDark ? const Color(0xFF00FFFF) : const Color(0xFF0088CC),
                                  ],
                                ),
                                shape: BoxShape.circle,
                                boxShadow: [
                                  BoxShadow(
                                    color: (isDark 
                                        ? const Color(0xFF00FFFF)
                                        : const Color(0xFF0088CC))
                                        .withOpacity(_glowAnimation.value * 0.5),
                                    blurRadius: 15,
                                    spreadRadius: 2,
                                  ),
                                ],
                              ),
                              child: IconButton(
                                icon: Icon(
                                  Icons.send,
                                  color: isDark ? const Color(0xFF0A0A0F) : Colors.white,
                                ),
                                onPressed: _onSend,
                              ),
                            );
                          },
                        ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  String _formatTablesForMobile(String text) {
    // Simple check - if has table markers, add note
    if (text.contains('|') && text.contains('-|-')) {
      return '💡 _Tip: Untuk melihat data lebih jelas, scroll horizontal pada tabel_\n\n' + text;
    }
    return text;
  }

}
