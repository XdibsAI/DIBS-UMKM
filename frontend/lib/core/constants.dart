import 'package:flutter/material.dart';

class AppConstants {
  static const String appName = 'DIBS1';
  static const String apiUrl = 'http://94.100.26.128:8081';

  static const Color primaryColor = Color(0xFF00E676);
  static const Color secondaryColor = Color(0xFF2979FF);
  static const Color accentColor = Color(0xFFFF3D00);
  static const Color darkBg = Color(0xFF121212);
  static const Color darkSurface = Color(0xFF1E1E1E);
  static const Color lightBg = Color(0xFFF5F5F5);
  static const Color lightSurface = Color(0xFFFFFFFF);
}

class StorageKeys {
  static const String token = 'auth_token';
  static const String userId = 'user_id';
  static const String theme = 'theme_mode';
  static const String language = 'language';
}
