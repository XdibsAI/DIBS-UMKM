import 'package:flutter/material.dart';
import '../services/api_service.dart';

class ProjectProvider extends ChangeNotifier {
  List<dynamic> _projects = [];
  List<dynamic> _videoProjects = [];
  List<dynamic> _knowledge = [];
  bool _isLoading = false;
  String? _error;

  List<dynamic> get projects => _projects;
  List<dynamic> get videoProjects => _videoProjects;
  List<dynamic> get knowledge => _knowledge;
  bool get isLoading => _isLoading;
  String? get error => _error;

  Future<void> loadAll() async {
    _isLoading = true;
    notifyListeners();

    try {
      final res = await ApiService.getProjects();
      if (res['status'] == 'success') {
        _projects = res['data'] ?? [];
        _videoProjects = _projects.where((p) => p['type'] == 'video').toList();
        _knowledge = _projects.where((p) => p['type'] == 'knowledge').toList();
      }
    } catch (e) {
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
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
