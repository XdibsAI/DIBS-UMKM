import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/constants.dart';

class ChatService extends ChangeNotifier {
  String? _token;
  String? _currentRoute;
  BuildContext? _navigationContext;

  ChatService() {
    _loadToken();
  }

  Future<void> _loadToken() async {
    final prefs = await SharedPreferences.getInstance();
    _token = prefs.getString(StorageKeys.token);
  }

  Map<String, String> getAuthHeaders() {
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      if (_token != null && _token!.isNotEmpty) 
        'Authorization': 'Bearer $_token',
    };
  }

  void setNavigationContext(BuildContext context, {required String currentRoute}) {
    _navigationContext = context;
    _currentRoute = currentRoute;
    debugPrint("🔐 Navigation context set for route: $currentRoute");
  }

  void navigateTo(String route) {
    if (_navigationContext != null) {
      Navigator.pushReplacementNamed(_navigationContext!, route);
    } else {
      debugPrint("⚠️ Navigation context not set");
    }
  }

  String? get currentRoute => _currentRoute;
}
