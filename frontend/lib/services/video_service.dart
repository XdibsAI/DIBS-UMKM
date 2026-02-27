import 'package:http/http.dart' as http;
import 'dart:convert';
import '../models/video_project.dart';

class VideoService {
  static const String baseUrl = 'http://94.100.26.128:8081/api/v1';
  static String? _token;

  static Future<void> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'email': email,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      _token = data['data']['token'];
    } else {
      throw Exception('Login failed');
    }
  }

  static Future<List<VideoProject>> getVideoProjects() async {
    if (_token == null) {
      throw Exception('Not authenticated');
    }

    final response = await http.get(
      Uri.parse('$baseUrl/video/list'),
      headers: {
        'Authorization': 'Bearer $_token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final List<dynamic> projectList = data['data'] ?? [];
      return projectList
          .map((json) => VideoProject.fromJson(json))
          .toList();
    } else {
      throw Exception('Failed to fetch videos');
    }
  }

  static Future<VideoProject> getVideoDetail(String projectId) async {
    if (_token == null) {
      throw Exception('Not authenticated');
    }

    final response = await http.get(
      Uri.parse('$baseUrl/video/status/$projectId'),
      headers: {
        'Authorization': 'Bearer $_token',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return VideoProject.fromJson(data['data']);
    } else {
      throw Exception('Failed to fetch video details');
    }
  }

  static Future<void> deleteVideo(String projectId) async {
    if (_token == null) {
      throw Exception('Not authenticated');
    }

    final response = await http.delete(
      Uri.parse('$baseUrl/video/$projectId'),
      headers: {
        'Authorization': 'Bearer $_token',
      },
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to delete video');
    }
  }
}
