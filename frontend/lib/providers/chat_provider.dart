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

  bool hasValidSession() => _currentSession != null && _currentSession!['session_id'] != null;

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
    } catch (e) { _error = e.toString(); }
    notifyListeners();
  }

  Future<void> createSession({String? name}) async {
    try {
      final res = await ApiService.createChatSession(name: name);
      if (res['status'] == 'success') {
        await loadSessions();
        await loadSession(res['data']['session_id']);
      }
    } catch (e) { _error = e.toString(); }
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
        _messages = messagesData.map((m) => ChatMessage(
          content: m['content'] ?? '',
          role: m['role'] ?? 'assistant',
          timestamp: DateTime.parse(m['created_at'] ?? DateTime.now().toIso8601String()),
        )).toList();
      }
    } catch (e) { _error = e.toString(); }
    finally { _isLoading = false; notifyListeners(); }
  }

  Future<bool> sendMessage(String text) async {
    // === DIBS SMART INTERCEPTOR ===
    final lowerText = text.toLowerCase();
    
    // 1. Logic Simpan
    if (lowerText.contains('simpan dulu')) {
      final contentToSave = text.replaceAll(RegExp(r'(?i)simpan dulu'), '').trim();
      if (contentToSave.isNotEmpty) {
        await ApiService.addKnowledge({'content': contentToSave, 'category': 'manual'});
      }
    }

    // 2. Logic Recall (Flexible & Smart)
    final recallMatch = RegExp(r'(munculkan|tampilkan|lihat|cek|buka|mana)\s+(knowledge|catatan|info)(?:\s+(?:tentang|soal|mengenai)\s+(.+))?').firstMatch(lowerText);
    if (recallMatch != null) {
      final query = recallMatch.group(3);
      final res = await ApiService.getKnowledge();
      if (res['status'] == 'success') {
        List data = res['data'] ?? [];
        if (query != null && query.isNotEmpty) {
          data = data.where((e) => e['content'].toString().toLowerCase().contains(query.toLowerCase())).toList();
        }
        if (data.isNotEmpty) {
          final summary = data.take(10).map((e) => "- ${e['content']}").join('\n');
          text = "User ingin melihat knowledge ${query ?? 'terbaru'}. Datanya:\n$summary\n\nTolong rangkum dengan gaya bahasa Dibs.";
        } else {
          text = "Knowledge tentang '$query' tidak ditemukan. Beritahu user dengan santai.";
        }
      }
    }

    if (_currentSession == null) return false;
    _isSending = true;
    _isThinking = true;
    _thinkingText = 'Sedang mengetik...';
    notifyListeners();

    try {
      final res = await ApiService.sendChatMessage(_currentSession!['session_id'], text);
      if (res['status'] == 'success') {
        _messages.add(ChatMessage(content: text, role: 'user', timestamp: DateTime.now()));
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
    } catch (e) { return false; }
  }

  Future<void> silentWarmup() async {}
}
