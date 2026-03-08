import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/chat.dart';

class ChatProvider extends ChangeNotifier {
  List<dynamic> _sessions = [];
  List<ChatMessage> _messages = [];
  Map<String, dynamic>? _currentSession;
  bool _isLoading = false;
  bool _isSending = false;
  bool _isThinking = false;
  String _thinkingText = '';
  String? _error;

  List<dynamic> get sessions => _sessions;
  List<ChatMessage> get messages => _messages;
  Map<String, dynamic>? get currentSession => _currentSession;
  bool get isLoading => _isLoading;
  bool get isSending => _isSending;
  bool get isThinking => _isThinking;
  String get thinkingText => _thinkingText;
  String? get error => _error;

  bool hasValidSession() =>
      _currentSession != null && _currentSession!['session_id'] != null;

  Future<void> initializeUserSession() async {
    _isLoading = true;
    notifyListeners();

    try {
      await loadSessions();

      if (_sessions.isEmpty) {
        await createSession();
      } else {
        await loadSession(_sessions.first['session_id']);
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadSessions() async {
    try {
      final res = await ApiService.getChatSessions();
      if (res['status'] == 'success') {
        _sessions = res['data']['data'] ?? [];
      }
    } catch (e) {
      _error = e.toString();
    }
    notifyListeners();
  }

  Future<void> createSession({String? name}) async {
    try {
      final res = await ApiService.createChatSession(name: name);
      if (res['status'] == 'success') {
        await loadSessions();
        await loadSession(res['data']['session_id']);
      }
    } catch (e) {
      _error = e.toString();
    }
    notifyListeners();
  }

  Future<void> loadSession(String sessionId) async {
    _isLoading = true;
    notifyListeners();

    try {
      final res = await ApiService.getChatSession(sessionId);
      if (res['status'] == 'success') {
        _currentSession = res['data'];
        final List<dynamic> messagesData = res['data']['messages'] ?? [];
        _messages = messagesData
            .map((m) => ChatMessage(
                  content: m['content'] ?? '',
                  role: m['role'] ?? 'assistant',
                  timestamp: DateTime.parse(
                    m['created_at'] ?? DateTime.now().toIso8601String(),
                  ),
                ))
            .toList();
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  void _appendLocalReply(String userText, String assistantText) {
    _messages.add(ChatMessage(
      content: userText,
      role: 'user',
      timestamp: DateTime.now(),
    ));
    _messages.add(ChatMessage(
      content: assistantText,
      role: 'assistant',
      timestamp: DateTime.now(),
    ));
    notifyListeners();
  }

  Future<bool> sendMessage(String text) async {
    final originalText = text.trim();
    final lowerText = originalText.toLowerCase();

    // ==============================
    // QUICK FINANCE / BUSINESS NOTE
    // ==============================
    final financeLike = RegExp(
      r'(beli|bayar|pengeluaran|keluar uang|modal|utang|pemasukan|jual).*(rp\s?[\d\.\,]+)',
      caseSensitive: false,
    ).hasMatch(originalText);

    if (financeLike) {
      try {
        final classifyRes = await ApiService.classifyBusinessNote(originalText);
        final category =
            classifyRes['data']?['category']?.toString() ?? 'finance';

        await ApiService.addKnowledge({
          'content': originalText,
          'category': category,
        });

        _appendLocalReply(
          originalText,
          'Siap, saya catat sebagai ${category == 'finance' ? 'catatan keuangan' : 'catatan bisnis'}.',
        );
        return true;
      } catch (e) {
        print("⚠️ Quick finance save failed: $e");
      }
    }

    // ==============================
    // SIMPAN MANUAL
    // ==============================
    if (lowerText.contains('simpan dulu')) {
      final content =
          originalText.replaceAll(RegExp(r'(?i)simpan dulu'), '').trim();

      if (content.isNotEmpty) {
        await ApiService.addKnowledge({
          'content': content,
          'category': 'manual',
        });

        _appendLocalReply(originalText, 'Siap, catatan berhasil disimpan.');
        return true;
      }
    }

    // ==============================
    // BUSINESS BRAIN QUICK CFO
    // ==============================
    if (lowerText.contains('ringkasan bisnis') ||
        lowerText.contains('summary bisnis') ||
        lowerText.contains('profit hari ini') ||
        lowerText.contains('pengeluaran hari ini')) {
      final res = await ApiService.getDailyBusinessSummary();

      if (res['status'] == 'success') {
        final d = Map<String, dynamic>.from(res['data'] ?? {});

        final top = ((d['top_products'] as List?) ?? []).take(3).map((e) {
          final item = Map<String, dynamic>.from(e);
          return '- ${item['name']} x${item['qty']}';
        }).join('\n');

        final low = ((d['low_stock_products'] as List?) ?? []).take(3).map((e) {
          final item = Map<String, dynamic>.from(e);
          return '- ${item['name']} (${item['stock']})';
        }).join('\n');

        final recs = ((d['recommendations'] as List?) ?? [])
            .take(3)
            .map((e) => '• $e')
            .join('\n');

        _appendLocalReply(
          originalText,
          """Ringkasan bisnis hari ini:

Omzet: Rp ${d['total_sales'] ?? 0}
Transaksi: ${d['total_transactions'] ?? 0}
Pengeluaran tercatat: Rp ${d['finance_notes_total'] ?? 0}
Profit hari ini: Rp ${d['profit_today'] ?? 0}

Top products:
${top.isEmpty ? '-' : top}

Low stock:
${low.isEmpty ? '-' : low}

Rekomendasi:
${recs.isEmpty ? '-' : recs}
""",
        );
        return true;
      }
    }

    if (lowerText.contains('produk paling laku minggu ini') ||
        lowerText.contains('produk terlaris minggu ini')) {
      final res = await ApiService.getSalesInsight(period: 'week');

      if (res['status'] == 'success') {
        final d = Map<String, dynamic>.from(res['data'] ?? {});
        final top = ((d['top_products'] as List?) ?? []).take(5).map((e) {
          final item = Map<String, dynamic>.from(e);
          return '- ${item['name']} x${item['qty']}';
        }).join('\n');

        _appendLocalReply(
          originalText,
          """Produk paling laku minggu ini:

${top.isEmpty ? '-' : top}

Total omzet minggu ini: Rp ${d['total_sales'] ?? 0}
Total transaksi: ${d['total_transactions'] ?? 0}
""",
        );
        return true;
      }
    }

    // ==============================
    // RECALL KNOWLEDGE
    // ==============================
    String processedText = originalText;

    final recallMatch = RegExp(
      r'(munculkan|tampilkan|lihat|cek|buka|mana)\s+(knowledge|catatan|info)(?:\s+(?:tentang|soal|mengenai)\s+(.+))?',
    ).firstMatch(lowerText);

    if (recallMatch != null) {
      final query = recallMatch.group(3);
      final res = await ApiService.getKnowledge();

      if (res['status'] == 'success') {
        List data = res['data'] ?? [];

        if (query != null && query.isNotEmpty) {
          data = data.where((e) {
            return e['content']
                .toString()
                .toLowerCase()
                .contains(query.toLowerCase());
          }).toList();
        }

        if (data.isNotEmpty) {
          final summary =
              data.take(10).map((e) => "- ${e['content']}").join('\n');
          processedText =
              "User ingin melihat knowledge ${query ?? 'terbaru'}:\n$summary\n\nTolong rangkum dengan gaya bahasa Dibs.";
        } else {
          processedText =
              "Knowledge tentang '$query' tidak ditemukan. Jawab dengan santai.";
        }
      }
    }

    if (_currentSession == null) return false;

    _isSending = true;
    _isThinking = true;
    _thinkingText = 'Sedang mengetik...';
    notifyListeners();

    try {
      final res = await ApiService.sendChatMessage(
        _currentSession!['session_id'],
        processedText,
      );

      if (res['status'] == 'success') {
        _messages.add(ChatMessage(
          content: originalText,
          role: 'user',
          timestamp: DateTime.now(),
        ));

        final assistantData = res['data']['assistant_message'];
        _messages.add(ChatMessage(
          content: assistantData['content'],
          role: assistantData['role'],
          timestamp: DateTime.parse(assistantData['created_at']),
        ));

        return true;
      }

      return false;
    } catch (e) {
      _error = e.toString();
      return false;
    } finally {
      _isSending = false;
      _isThinking = false;
      notifyListeners();
    }
  }

  Future<bool> deleteSession(String sessionId) async {
    try {
      final res = await ApiService.deleteChatSession(sessionId);
      if (res['status'] == 'success') {
        await loadSessions();
        if (_currentSession?['session_id'] == sessionId) {
          _currentSession = null;
          _messages = [];
        }
        return true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  Future<void> silentWarmup() async {}
}
