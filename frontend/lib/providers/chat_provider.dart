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
  bool _useNvidia = false;

  List<dynamic> get sessions => _sessions;
  List<ChatMessage> get messages => _messages;
  Map<String, dynamic>? get currentSession => _currentSession;
  bool get isLoading => _isLoading;
  bool get isSending => _isSending;
  bool get isThinking => _isThinking;
  String get thinkingText => _thinkingText;
  String? get error => _error;

  bool hasValidSession() {
    return _currentSession != null && _currentSession!['session_id'] != null;
  }

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
        _sessions = res['data'] ?? [];
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
        
        // Parse messages
        final List<dynamic> messagesData = res['data']['messages'] ?? [];
        _messages = messagesData.map((m) {
          return ChatMessage(
            content: m['content'] ?? '',
            role: m['role'] ?? 'assistant',
            timestamp: DateTime.parse(m['created_at'] ?? DateTime.now().toIso8601String()),
          );
        }).toList();
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> sendMessage(String text) async {
    if (_currentSession == null) return false;

    _isSending = true;
    _isThinking = true;
    _thinkingText = 'Sedang mengetik...';
    notifyListeners();

    try {
      final res = await ApiService.sendChatMessage(_currentSession!['session_id'], text);

      if (res['status'] == 'success') {
        // User message (dibuat manual)
        final userMessage = ChatMessage(
          content: text,
          role: 'user',
          timestamp: DateTime.now(),
        );
        _messages.add(userMessage);

        // Assistant message dari response
        final assistantData = res['data']['assistant_message'];
        final assistantMessage = ChatMessage(
          content: assistantData['content'],
          role: assistantData['role'],
          timestamp: DateTime.parse(assistantData['created_at']),
        );
        _messages.add(assistantMessage);

        _isSending = false;
        _isThinking = false;
        notifyListeners();
        return true;
      } else {
        _error = res['message'] ?? 'Gagal mengirim pesan';
        _isSending = false;
        _isThinking = false;
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = e.toString();
      _isSending = false;
      _isThinking = false;
      notifyListeners();
      return false;
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
      _error = e.toString();
      return false;
    }
  }

  void silentWarmup() {
    // Implementasi warmup
  }
}
