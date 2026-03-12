import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ProjectProvider extends ChangeNotifier {
  List<dynamic> _projects = [];
  List<dynamic> _videoProjects = [];
  List<dynamic> _knowledge = [];
  bool _isLoading = false;
  String? _error;
  String _lastSearchQuery = '';

  List<dynamic> get projects => _projects;
  List<dynamic> get videoProjects => _videoProjects;
  List<dynamic> get knowledge => _knowledge;
  bool get isLoading => _isLoading;
  String? get error => _error;
  String get lastSearchQuery => _lastSearchQuery;

  Future<void> loadAll() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final projectRes = await ApiService.getProjects();
      if (projectRes['status'] == 'success') {
        _projects = projectRes['data'] ?? [];
        _videoProjects = _projects.where((p) => p['type'] == 'video').toList();
      }

      final knowledgeRes = await ApiService.getKnowledge();
      if (knowledgeRes['status'] == 'success') {
        _knowledge = knowledgeRes['data'] ?? [];
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> loadKnowledge({String search = ''}) async {
    _isLoading = true;
    _lastSearchQuery = search;
    notifyListeners();

    try {
      final res = search.trim().isEmpty
          ? await ApiService.getKnowledge()
          : await ApiService.searchKnowledge(search);

      if (res['status'] == 'success') {
        _knowledge = res['data'] ?? [];
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> addKnowledge(String content,
      {String category = 'general'}) async {
    try {
      final res = await ApiService.addKnowledge({
        'content': content,
        'category': category,
      });

      if (res['status'] == 'success') {
        await loadKnowledge(search: _lastSearchQuery);
        return true;
      }
      return false;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> updateKnowledgeItem(int id, String content,
      {String category = 'general'}) async {
    try {
      final res = await ApiService.updateKnowledge(id, {
        'content': content,
        'category': category,
      });

      if (res['status'] == 'success') {
        await loadKnowledge(search: _lastSearchQuery);
        return true;
      }
      return false;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<bool> deleteKnowledgeItem(int id) async {
    try {
      final res = await ApiService.deleteKnowledge(id);
      if (res['status'] == 'success') {
        await loadKnowledge(search: _lastSearchQuery);
        return true;
      }
      return false;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }

  Future<Map<String, dynamic>?> generateReport(String period) async {
    try {
      final res = await ApiService.generateKnowledgeReport(period: period);
      if (res['status'] == 'success') {
        return res['data'];
      }
      return null;
    } catch (e) {
      _error = e.toString();
      return null;
    }
  }
}
