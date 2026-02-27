import 'package:flutter/material.dart';
import '../services/api_service.dart';

class SocialProvider extends ChangeNotifier {
  List<dynamic> _posts = [];
  bool _isLoading = false;
  String? _error;
  String _generatedCaption = '';
  List<String> _suggestedHashtags = [];
  bool _isGenerating = false;

  List<dynamic> get posts => _posts;
  bool get isLoading => _isLoading;
  String? get error => _error;
  String get generatedCaption => _generatedCaption;
  List<String> get suggestedHashtags => _suggestedHashtags;
  bool get isGenerating => _isGenerating;

  Future<void> loadPosts() async {
    _isLoading = true;
    notifyListeners();

    try {
      // Implementasi
      _posts = [];
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> generateCaption({required String topic, required String tone, required String platform}) async {
    _isGenerating = true;
    notifyListeners();
    // TODO: Implement API call
    await Future.delayed(Duration(seconds: 1));
    _generatedCaption = "Generated caption for $topic on $platform with $tone tone";
    _isGenerating = false;
    notifyListeners();
  }

  Future<void> suggestHashtags({required String topic, required String platform}) async {
    _isGenerating = true;
    notifyListeners();
    // TODO: Implement API call
    await Future.delayed(Duration(seconds: 1));
    _suggestedHashtags = ["#dibs", "#ai", "#indonesia"];
    _isGenerating = false;
    notifyListeners();
  }

  Future<void> deletePost(String postId) async {
    // TODO: Implement API call
    _posts.removeWhere((p) => p['id'] == postId);
    notifyListeners();
  }
}
