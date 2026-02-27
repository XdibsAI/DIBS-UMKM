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
    // Show confirmation dialog with cyber style
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF12121A),
        title: const Text(
          'Chat Baru',
          style: TextStyle(color: Color(0xFF00FFFF)),
        ),
        content: const Text(
          'Mulai percakapan baru? Chat saat ini akan disimpan ke riwayat.',
          style: TextStyle(color: Color(0xFFE0E0FF)),
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(color: Color(0xFF00FFFF), width: 0.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            style: TextButton.styleFrom(
              foregroundColor: const Color(0xFF8888AA),
            ),
            child: const Text('Batal'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF00FFFF),
              foregroundColor: const Color(0xFF0A0A0F),
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
          const SnackBar(
            content: Text('✨ Chat baru dimulai'),
            duration: Duration(seconds: 1),
            backgroundColor: Color(0xFF12121A),
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.all(Radius.circular(12)),
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
        backgroundColor: const Color(0xFF12121A),
        title: const Text(
          'Hapus Chat',
          style: TextStyle(color: Color(0xFFFF44AA)),
        ),
        content: const Text(
          'Yakin ingin menghapus chat ini?',
          style: TextStyle(color: Color(0xFFE0E0FF)),
        ),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
          side: const BorderSide(color: Color(0xFFFF44AA), width: 0.5),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            style: TextButton.styleFrom(
              foregroundColor: const Color(0xFF8888AA),
            ),
            child: const Text('Batal'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(
              foregroundColor: const Color(0xFFFF44AA),
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
    showModalBottomSheet(
      context: ctx,
      backgroundColor: const Color(0xFF12121A),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        side: BorderSide(color: Color(0xFF00FFFF), width: 0.5),
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
                color: const Color(0xFF00FFFF).withOpacity(0.3),
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            ListTile(
              leading: const Icon(Icons.copy, color: Color(0xFF00FFFF)),
              title: const Text(
                'Salin Pesan',
                style: TextStyle(color: Color(0xFFE0E0FF)),
              ),
              onTap: () {
                Clipboard.setData(ClipboardData(text: content));
                Navigator.pop(sheetCtx);
                ScaffoldMessenger.of(ctx).showSnackBar(
                  const SnackBar(
                    content: Text('Pesan disalin'),
                    duration: Duration(seconds: 1),
                    backgroundColor: Color(0xFF12121A),
                    behavior: SnackBarBehavior.floating,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.all(Radius.circular(12)),
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
                      color: const Color(0xFF00FFFF).withOpacity(_glowAnimation.value),
                      width: 2,
                    ),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF00FFFF).withOpacity(_glowAnimation.value * 0.3),
                        blurRadius: 30,
                        spreadRadius: 10,
                      ),
                    ],
                  ),
                  child: const Icon(
                    Icons.bolt,
                    color: Color(0xFF00FFFF),
                    size: 48,
                  ),
                );
              },
            ),
            const SizedBox(height: 24),
            Text(
              'Halo, $userName! 👋',
              style: const TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: Color(0xFFE0E0FF),
                letterSpacing: -0.5,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              'Ada yang bisa DIBS bantu hari ini?\nSilakan kirim pesan Anda.',
              style: TextStyle(
                fontSize: 16,
                color: const Color(0xFF8888AA).withOpacity(0.8),
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
                _buildSuggestionChip('💡 Bantu saya dengan ide', const Color(0xFFFF44AA)),
                _buildSuggestionChip('📝 Buatkan ringkasan', const Color(0xFF9D4DFF)),
                _buildSuggestionChip('🔍 Cari informasi', const Color(0xFF00FFAA)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSuggestionChip(String label, Color color) {
    return ActionChip(
      label: Text(
        label,
        style: const TextStyle(
          fontSize: 13,
          color: Color(0xFFE0E0FF),
        ),
      ),
      backgroundColor: const Color(0xFF050507),
      side: BorderSide(color: color.withOpacity(0.5), width: 1),
      onPressed: () {
        _messageController.text = label.substring(3);
        _onSend();
      },
    );
  }

  Widget _buildThinkingBubble(String text) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: const Color(0xFF00FFFF).withOpacity(0.1),
              shape: BoxShape.circle,
              border: Border.all(color: const Color(0xFF00FFFF), width: 1),
            ),
            child: const Icon(
              Icons.bolt,
              color: Color(0xFF00FFFF),
              size: 16,
            ),
          ),
          const SizedBox(width: 12),
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: const Color(0xFF12121A),
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(20),
                  topRight: Radius.circular(20),
                  bottomRight: Radius.circular(20),
                  bottomLeft: Radius.circular(4),
                ),
                border: Border.all(
                  color: const Color(0xFF00FFFF).withOpacity(0.3),
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
                        const Color(0xFF00FFFF).withOpacity(_glowAnimation.value),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Flexible(
                    child: Text(
                      text,
                      style: const TextStyle(
                        fontSize: 14,
                        color: Color(0xFFE0E0FF),
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
    final h = message.timestamp.hour.toString().padLeft(2, '0');
    final m = message.timestamp.minute.toString().padLeft(2, '0');
    final timeString = '$h:$m';

    final hasMarkdown = !isUser &&
        (message.content.contains('|') ||
            message.content.contains('**') ||
            message.content.contains('\n-') ||
            message.content.contains('\n#') ||
            message.content.contains('📊'));

    final bubbleColor = isUser 
        ? const Color(0xFFFF44AA).withOpacity(0.15)
        : const Color(0xFF00FFFF).withOpacity(0.15);
    
    final borderColor = isUser
        ? const Color(0xFFFF44AA).withOpacity(0.5)
        : const Color(0xFF00FFFF).withOpacity(0.5);
    
    final textColor = isUser
        ? const Color(0xFFFF44AA)
        : const Color(0xFF00FFFF);

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
                  color: const Color(0xFF00FFFF).withOpacity(0.1),
                  shape: BoxShape.circle,
                  border: Border.all(color: const Color(0xFF00FFFF), width: 1),
                ),
                child: const Icon(
                  Icons.bolt,
                  color: Color(0xFF00FFFF),
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
                            color: isUser ? textColor : const Color(0xFFE0E0FF),
                          ),
                          tableHead: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: isUser ? textColor : const Color(0xFF00FFFF),
                            fontSize: 13,
                          ),
                          tableBody: TextStyle(
                            fontSize: 13,
                            color: isUser ? textColor : const Color(0xFFE0E0FF),
                          ),
                          tableBorder: TableBorder.all(
                            color: isUser 
                                ? const Color(0xFFFF44AA).withOpacity(0.3)
                                : const Color(0xFF00FFFF).withOpacity(0.3),
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
                          color: isUser ? textColor : const Color(0xFFE0E0FF),
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
                            color: isUser
                                ? const Color(0xFFFF44AA).withOpacity(0.5)
                                : const Color(0xFF00FFFF).withOpacity(0.5),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Icon(
                          Icons.copy,
                          size: 12,
                          color: isUser
                              ? const Color(0xFFFF44AA).withOpacity(0.3)
                              : const Color(0xFF00FFFF).withOpacity(0.3),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            if (isUser) ...[
              const SizedBox(width: 12),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFFFF44AA).withOpacity(0.1),
                  shape: BoxShape.circle,
                  border: Border.all(color: const Color(0xFFFF44AA), width: 1),
                ),
                child: const Icon(
                  Icons.person,
                  color: Color(0xFFFF44AA),
                  size: 16,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }


  void _showAttachmentMenu() {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.grey[900],
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'Pilih Jenis File',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
              ),
              const SizedBox(height: 20),
              
              // 🖼️ Gambar untuk analisa
              ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Colors.blue,
                  child: Icon(Icons.image, color: Colors.white),
                ),
                title: const Text('📷 Gambar untuk Analisa', style: TextStyle(color: Colors.white)),
                subtitle: const Text('JPG, PNG - DIBS akan analisa gambar', style: TextStyle(color: Colors.grey, fontSize: 12)),
                onTap: () {
                  Navigator.pop(ctx);
                  _pickImageForAnalysis();
                },
              ),
              
              const Divider(color: Colors.grey),
              
              // 📄 Dokumen
              ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Colors.orange,
                  child: Icon(Icons.description, color: Colors.white),
                ),
                title: const Text('📄 Dokumen', style: TextStyle(color: Colors.white)),
                subtitle: const Text('PDF, DOC, CSV, TXT - DIBS akan baca isi', style: TextStyle(color: Colors.grey, fontSize: 12)),
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

    return Consumer<ChatProvider>(
      builder: (context, chatProvider, _) {
        return Scaffold(
          key: _scaffoldKey,
          appBar: AppBar(
            title: AnimatedBuilder(
              animation: _glowAnimation,
              builder: (context, child) {
                return Text(
                  chatProvider.currentSession?['name'] ?? 'DIBS AI',
                  style: TextStyle(
                    color: const Color(0xFF00FFFF).withOpacity(_glowAnimation.value),
                    fontSize: 20,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 1,
                    shadows: [
                      Shadow(
                        color: const Color(0xFF00FFFF).withOpacity(_glowAnimation.value * 0.5),
                        blurRadius: 10,
                      ),
                    ],
                  ),
                );
              },
            ),
            backgroundColor: const Color(0xFF050507),
            foregroundColor: const Color(0xFFE0E0FF),
            elevation: 0,
            leading: IconButton(
              icon: const Icon(Icons.menu, color: Color(0xFF00FFFF)),
              onPressed: () => _scaffoldKey.currentState?.openDrawer(),
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.add_comment, color: Color(0xFF00FFFF)),
                onPressed: _createNewSession,
                tooltip: 'Chat Baru',
              ),
            ],
          ),
          
          drawer: Drawer(
            backgroundColor: const Color(0xFF0A0A0F),
            child: Column(
              children: [
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.fromLTRB(20, 48, 20, 20),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                      colors: [Color(0xFF00FFFF), Color(0xFF9D4DFF)],
                    ),
                    borderRadius: const BorderRadius.only(
                      bottomLeft: Radius.circular(20),
                      bottomRight: Radius.circular(20),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'DIBS AI',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF0A0A0F),
                          letterSpacing: 2,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        userName,
                        style: const TextStyle(
                          color: Color(0xFF0A0A0F),
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Chat History',
                        style: TextStyle(
                          color: const Color(0xFF0A0A0F).withOpacity(0.7),
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
                Expanded(
                  child: chatProvider.isLoading
                      ? const Center(
                          child: CircularProgressIndicator(
                            valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF00FFFF)),
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
                                    color: const Color(0xFF8888AA).withOpacity(0.5),
                                  ),
                                  const SizedBox(height: 16),
                                  Text(
                                    'Belum ada chat',
                                    style: TextStyle(
                                      color: const Color(0xFF8888AA).withOpacity(0.8),
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
                                        ? const Color(0xFF00FFFF).withOpacity(0.1)
                                        : null,
                                    borderRadius: BorderRadius.circular(12),
                                    border: isSelected
                                        ? Border.all(
                                            color: const Color(0xFF00FFFF),
                                            width: 0.5,
                                          )
                                        : null,
                                  ),
                                  child: ListTile(
                                    leading: Container(
                                      padding: const EdgeInsets.all(8),
                                      decoration: BoxDecoration(
                                        color: isSelected
                                            ? const Color(0xFF00FFFF)
                                            : const Color(0xFF8888AA).withOpacity(0.2),
                                        shape: BoxShape.circle,
                                      ),
                                      child: Icon(
                                        Icons.chat,
                                        size: 16,
                                        color: isSelected
                                            ? const Color(0xFF0A0A0F)
                                            : const Color(0xFF00FFFF),
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
                                            ? const Color(0xFF00FFFF)
                                            : const Color(0xFFE0E0FF),
                                      ),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                    subtitle: Text(
                                      '${session['message_count']} pesan',
                                      style: TextStyle(
                                        fontSize: 12,
                                        color: const Color(0xFF8888AA).withOpacity(0.8),
                                      ),
                                    ),
                                    trailing: IconButton(
                                      icon: Icon(
                                        Icons.delete_outline,
                                        size: 18,
                                        color: isSelected
                                            ? const Color(0xFFFF44AA)
                                            : const Color(0xFF8888AA),
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
                    icon: const Icon(Icons.add, color: Color(0xFF0A0A0F)),
                    label: const Text(
                      'Chat Baru',
                      style: TextStyle(color: Color(0xFF0A0A0F)),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF00FFFF),
                      minimumSize: const Size(double.infinity, 45),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      elevation: 4,
                      shadowColor: const Color(0xFF00FFFF).withOpacity(0.5),
                    ),
                  ),
                ),
              ],
            ),
          ),
          
          body: Container(
            decoration: const BoxDecoration(
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                colors: [Color(0xFF0A0A0F), Color(0xFF050507)],
              ),
            ),
            child: Column(
              children: [
                Expanded(
                  child: chatProvider.isLoading
                      ? const Center(
                          child: CircularProgressIndicator(
                            valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF00FFFF)),
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
                    backgroundColor: const Color(0xFF00FFFF).withOpacity(0.1),
                    valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF00FFFF)),
                  ),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFF050507),
                    border: Border(
                      top: BorderSide(
                        color: const Color(0xFF00FFFF).withOpacity(0.3),
                      ),
                    ),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      // 📎 Upload button
                      IconButton(
                        icon: const Icon(Icons.attach_file, color: Color(0xFF00FFFF), size: 24),
                        onPressed: _showAttachmentMenu,
                        tooltip: 'Upload file',
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
                          style: const TextStyle(color: Color(0xFFE0E0FF)),
                          decoration: InputDecoration(
                            hintText: chatProvider.isSending
                                ? 'Menunggu balasan...'
                                : 'Tulis pesan...',
                            hintStyle: TextStyle(
                              color: const Color(0xFF8888AA).withOpacity(0.5),
                            ),
                            border: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(24),
                              borderSide: const BorderSide(
                                color: Color(0xFF00FFFF),
                                width: 0.5,
                              ),
                            ),
                            enabledBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(24),
                              borderSide: BorderSide(
                                color: const Color(0xFF00FFFF).withOpacity(0.3),
                                width: 0.5,
                              ),
                            ),
                            focusedBorder: OutlineInputBorder(
                              borderRadius: BorderRadius.circular(24),
                              borderSide: const BorderSide(
                                color: Color(0xFF00FFFF),
                                width: 1.5,
                              ),
                            ),
                            filled: true,
                            fillColor: const Color(0xFF0A0A0F),
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
                            color: const Color(0xFF00FFFF).withOpacity(0.1),
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: const Color(0xFF00FFFF).withOpacity(0.3),
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
                                gradient: const RadialGradient(
                                  colors: [Color(0xFF00FFFF), Color(0xFF00FFFF)],
                                ),
                                shape: BoxShape.circle,
                                boxShadow: [
                                  BoxShadow(
                                    color: const Color(0xFF00FFFF).withOpacity(_glowAnimation.value * 0.5),
                                    blurRadius: 15,
                                    spreadRadius: 2,
                                  ),
                                ],
                              ),
                              child: IconButton(
                                icon: const Icon(Icons.send, color: Color(0xFF0A0A0F)),
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
}
