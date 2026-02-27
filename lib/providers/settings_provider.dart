import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SettingsProvider extends ChangeNotifier {
  String _theme = 'dark';
  bool _isLoading = false;

  String get theme => _theme;
  bool get isLoading => _isLoading;

  SettingsProvider() {
    loadSettings();
  }

  Future<void> loadSettings() async {
    _isLoading = true;
    notifyListeners();

    try {
      final prefs = await SharedPreferences.getInstance();
      _theme = prefs.getString('theme') ?? 'dark';
    } catch (e) {
      debugPrint('Error loading settings: $e');
    }

    _isLoading = false;
    notifyListeners();
  }

  Future<void> updateSetting(String key, dynamic value) async {
    if (key == 'theme') {
      _theme = value as String;
    }
    
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(key, value.toString());
    notifyListeners();
  }
}
