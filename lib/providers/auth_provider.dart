import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/user.dart';
import '../services/api_service.dart';

class AuthProvider extends ChangeNotifier {
  User? _user;
  String? _token;
  bool _isLoading = false;
  bool _isInitializing = true;
  String? _error;

  User? get user => _user;
  bool get isLoading => _isLoading;
  bool get isInitializing => _isInitializing;
  String? get error => _error;
  bool get isAuthenticated => _token != null;

  Future<void> tryAutoLogin() async {
    _isInitializing = true;
    notifyListeners();

    try {
      final prefs = await SharedPreferences.getInstance();
      final savedToken = prefs.getString('token');

      if (savedToken != null && savedToken.isNotEmpty) {
        _token = savedToken;
        final savedEmail = prefs.getString('user_email');
        final savedName = prefs.getString('user_name');
        final savedId = prefs.getString('user_id');

        if (savedEmail != null) {
          _user = User(
            id: savedId ?? '',
            email: savedEmail,
            displayName: savedName ?? 'User',
            createdAt: DateTime.now(),
          );
        }
      }
    } catch (e) {
      debugPrint('tryAutoLogin error: $e');
    }

    _isInitializing = false;
    notifyListeners();
  }

  Future<bool> login({required String email, required String password}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final res = await ApiService.login(email, password);

      if (res['status'] == 'success' && res['data'] != null) {
        final data = res['data'];
        _token = data['token'];

        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('auth_token', _token!);
        await prefs.setString('user_id', data['user_id'] ?? '');

        _user = User(
          id: data['user_id'] ?? '',
          email: email,
          displayName: data['display_name'] ?? 'User',
          createdAt: DateTime.now(),
        );

        await _saveToStorage();
        _isLoading = false;
        notifyListeners();
        return true;
      }

      _error = res['message'] ?? 'Login gagal';
      return false;
    } catch (e) {
      _error = 'Connection error: $e';
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> register({
    required String displayName,
    required String email,
    required String password,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final res = await ApiService.register(email, password, displayName);

      if (res['status'] == 'success' && res['data'] != null) {
        final data = res['data'];

        if (data['token'] != null) {
          _token = data['token'];
          _user = User(
            id: data['user_id'] ?? '',
            email: email,
            displayName: displayName,
            createdAt: DateTime.now(),
          );
          await _saveToStorage();
          _isLoading = false;
          notifyListeners();
          return true;
        }

        _isLoading = false;
        notifyListeners();
        return await login(email: email, password: password);
      }

      _error = res['message'] ?? 'Registrasi gagal';
      return false;
    } catch (e) {
      _error = 'Connection error: $e';
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> logout() async {
    _token = null;
    _user = null;
    await _clearStorage();
    notifyListeners();
  }

  Future<void> _saveToStorage() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('token', _token!);
    await prefs.setString('user_email', _user?.email ?? '');
    await prefs.setString('user_name', _user?.displayName ?? 'User');
    await prefs.setString('user_id', _user?.id ?? '');
  }

  Future<void> _clearStorage() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('token');
    await prefs.remove('user_email');
    await prefs.remove('user_name');
    await prefs.remove('user_id');
  }
}
