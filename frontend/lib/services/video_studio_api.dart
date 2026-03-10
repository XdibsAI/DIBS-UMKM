import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import 'api_service.dart';

class VideoStudioApi {
  static Future<String?> getAccessToken() async {
    return _getToken();
  }

  static Future<Map<String, String>> authHeaders({bool json = false}) async {
    return _headers(json: json);
  }

  static Future<String?> _getToken() async {
    final prefs = await SharedPreferences.getInstance();
    final candidates = [
      prefs.getString('token'),
      prefs.getString('access_token'),
      prefs.getString('auth_token'),
      prefs.getString('jwt'),
    ];
    for (final item in candidates) {
      if (item != null && item.trim().isNotEmpty) {
        return item.trim();
      }
    }
    return null;
  }

  static Future<Map<String, String>> _headers({bool json = true}) async {
    final token = await _getToken();
    final headers = <String, String>{};
    if (json) {
      headers['Content-Type'] = 'application/json';
    }
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  static Future<Map<String, dynamic>> uploadVideoImage(String filePath) async {
    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('${ApiConfig.baseUrl}/video/upload-image'),
      );

      final token = await _getToken();
      if (token != null && token.isNotEmpty) {
        request.headers['Authorization'] = 'Bearer $token';
      }

      request.files.add(await http.MultipartFile.fromPath('file', filePath));

      final response = await request.send();
      final responseBody = await response.stream.bytesToString();
      return jsonDecode(responseBody) as Map<String, dynamic>;
    } catch (e) {
      debugPrint('Upload video image error: $e');
      return {'status': 'error', 'message': 'Upload image gagal'};
    }
  }

  static Future<Map<String, dynamic>> uploadVideoImages(
      List<String> filePaths) async {
    try {
      final uploadedPaths = <String>[];

      for (final filePath in filePaths) {
        final res = await uploadVideoImage(filePath);
        if ((res['status']?.toString() ?? '') == 'success') {
          final data = Map<String, dynamic>.from(res['data'] ?? {});
          final imagePath = data['image_path']?.toString();
          if (imagePath != null && imagePath.isNotEmpty) {
            uploadedPaths.add(imagePath);
          }
        }
      }

      return {
        'status': 'success',
        'data': {
          'image_paths': uploadedPaths,
        }
      };
    } catch (e) {
      debugPrint('Upload video images error: $e');
      return {'status': 'error', 'message': 'Upload images gagal'};
    }
  }

  static Future<Map<String, dynamic>> createVideoProject({
    required String niche,
    required int duration,
    String style = 'premium',
    String language = 'id',
    String? prompt,
    String? productName,
    String? priceText,
    String? ctaText,
    String? brandName,
    String? productImageUrl,
    String? uploadedImagePath,
    List<String>? uploadedImagePaths,
  }) async {
    try {
      final payload = <String, dynamic>{
        'niche': niche,
        'duration': duration,
        'style': style,
        'language': language,
        'prompt': prompt ?? niche,
      };

      if (productName != null && productName.trim().isNotEmpty) {
        payload['product_name'] = productName.trim();
      }
      if (priceText != null && priceText.trim().isNotEmpty) {
        payload['price_text'] = priceText.trim();
      }
      if (ctaText != null && ctaText.trim().isNotEmpty) {
        payload['cta_text'] = ctaText.trim();
      }
      if (brandName != null && brandName.trim().isNotEmpty) {
        payload['brand_name'] = brandName.trim();
      }
      if (productImageUrl != null && productImageUrl.trim().isNotEmpty) {
        payload['product_image_url'] = productImageUrl.trim();
      }
      if (uploadedImagePath != null && uploadedImagePath.trim().isNotEmpty) {
        payload['uploaded_image_path'] = uploadedImagePath.trim();
      }
      if (uploadedImagePaths != null && uploadedImagePaths.isNotEmpty) {
        payload['uploaded_image_paths'] = uploadedImagePaths;
      }

      final res = await http.post(
        Uri.parse('${ApiConfig.baseUrl}/video/create'),
        headers: await _headers(),
        body: jsonEncode(payload),
      );

      return jsonDecode(res.body) as Map<String, dynamic>;
    } catch (e) {
      debugPrint('Create video project error: $e');
      return {'status': 'error', 'message': 'Gagal membuat video'};
    }
  }

  static Future<Map<String, dynamic>> deleteVideoProject(String id) async {
    try {
      final res = await http.delete(
        Uri.parse('${ApiConfig.baseUrl}/video/delete/$id'),
        headers: await _headers(json: false),
      );

      return jsonDecode(res.body) as Map<String, dynamic>;
    } catch (e) {
      debugPrint('Delete video error: $e');
      return {'status': 'error', 'message': 'Gagal delete video'};
    }
  }

  static Future<Map<String, dynamic>> getVideoProjects() async {
    try {
      final res = await http.get(
        Uri.parse('${ApiConfig.baseUrl}/video/list'),
        headers: await _headers(json: false),
      );
      return jsonDecode(res.body) as Map<String, dynamic>;
    } catch (e) {
      debugPrint('Get video projects error: $e');
      return {'status': 'error', 'message': 'Gagal mengambil video'};
    }
  }
}
