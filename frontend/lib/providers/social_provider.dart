import 'package:flutter/material.dart';
import '../services/api_service.dart';

class SocialProvider extends ChangeNotifier {
  List<Map<String, dynamic>> _posts = [];
  List<Map<String, dynamic>> _accounts = [];
  Map<String, dynamic> _analytics = {};
  
  bool _isLoading = false;
  bool _isGenerating = false;
  String? _error;
  String _generatedCaption = '';
  List<String> _suggestedHashtags = [];

  // Getters
  List<Map<String, dynamic>> get posts => _posts;
  List<Map<String, dynamic>> get accounts => _accounts;
  Map<String, dynamic> get analytics => _analytics;
  bool get isLoading => _isLoading;
  bool get isGenerating => _isGenerating;
  String? get error => _error;
  String get generatedCaption => _generatedCaption;
  List<String> get suggestedHashtags => _suggestedHashtags;

  // Load connected accounts
  Future<void> loadAccounts() async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await ApiService.getSocialAccounts();
      
      if (response['status'] == 'success') {
        _accounts = List<Map<String, dynamic>>.from(response['data'] ?? []);
      }
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Load accounts error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Load posts
  Future<void> loadPosts({String? platform, String? status}) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await ApiService.getSocialPosts(
        platform: platform,
        status: status,
      );
      
      if (response['status'] == 'success') {
        _posts = List<Map<String, dynamic>>.from(response['data'] ?? []);
      }
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Load posts error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Create/schedule post
  Future<bool> createPost({
    required String platform,
    required String content,
    String? mediaUrl,
    DateTime? scheduledAt,
  }) async {
    try {
      final data = {
        'platform': platform,
        'content': content,
        'media_url': mediaUrl,
        'scheduled_at': scheduledAt?.toIso8601String() ?? DateTime.now().toIso8601String(),
      };
      
      final response = await ApiService.createSocialPost(data);
      
      if (response['status'] == 'success') {
        await loadPosts();
        return true;
      }
      
      return false;
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Create post error: $e');
      return false;
    }
  }

  // Delete post
  Future<bool> deletePost(String postId) async {
    try {
      final response = await ApiService.deleteSocialPost(postId);
      
      if (response['status'] == 'success') {
        _posts.removeWhere((p) => p['id'] == postId);
        notifyListeners();
        return true;
      }
      
      return false;
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Delete post error: $e');
      return false;
    }
  }

  // Generate AI caption
  Future<void> generateCaption({
    required String topic,
    required String platform,
    String tone = 'friendly',
  }) async {
    _isGenerating = true;
    _error = null;
    notifyListeners();

    try {
      final response = await ApiService.generateSocialCaption({
        'topic': topic,
        'platform': platform,
        'tone': tone,
      });
      
      if (response['status'] == 'success') {
        _generatedCaption = response['data']['caption'] ?? '';
        _suggestedHashtags = List<String>.from(response['data']['hashtags'] ?? []);
      } else {
        _error = response['message'];
      }
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Generate caption error: $e');
    } finally {
      _isGenerating = false;
      notifyListeners();
    }
  }

  // Load analytics
  Future<void> loadAnalytics({String? platform, String period = '7days'}) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await ApiService.getSocialAnalytics(
        platform: platform,
        period: period,
      );
      
      if (response['status'] == 'success') {
        _analytics = response['data'] ?? {};
      }
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Load analytics error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Connect account
  Future<bool> connectAccount({
    required String platform,
    required String username,
    String accessToken = '',
  }) async {
    try {
      final response = await ApiService.connectSocialAccount({
        'platform': platform,
        'username': username,
        'access_token': accessToken,
      });
      
      if (response['status'] == 'success') {
        await loadAccounts();
        return true;
      }
      
      return false;
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Connect account error: $e');
      return false;
    }
  }

  void clearGeneratedContent() {
    _generatedCaption = '';
    _suggestedHashtags = [];
    notifyListeners();
  }
}
