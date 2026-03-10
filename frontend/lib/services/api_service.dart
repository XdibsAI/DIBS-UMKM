import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiConfig {
  // API URL dari environment variable, fallback ke IP server untuk production
  static const String baseUrl = String.fromEnvironment(
    'API_URL',
    defaultValue: 'http://94.100.26.128:8081/api/v1',
  );

  // Download URL untuk video & APK
  static const String downloadUrl = String.fromEnvironment(
    'DOWNLOAD_URL',
    defaultValue: 'http://94.100.26.128:9091',
  );

  // Timeouts
  static const int connectionTimeout = 30; // seconds
  static const int videoTimeout = 300; // 5 menit untuk download video
}

class ApiService {
  static Future<Map<String, String>> _getHeaders() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('auth_token') ?? '';
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    };
  }

  static Future<Map<String, dynamic>> _post(
      String endpoint, Map<String, dynamic> body) async {
    final headers = await _getHeaders();
    final url = '${ApiConfig.baseUrl}$endpoint';
    try {
      final res = await http
          .post(
            Uri.parse(url),
            headers: headers,
            body: jsonEncode(body),
          )
          .timeout(Duration(seconds: ApiConfig.connectionTimeout));
      return jsonDecode(res.body);
    } catch (e) {
      debugPrint('POST error to $endpoint: $e');
      return {'success': false, 'error': 'Connection error'};
    }
  }

  static Future<Map<String, dynamic>> _get(String endpoint) async {
    final headers = await _getHeaders();
    final url = '${ApiConfig.baseUrl}$endpoint';
    try {
      final res = await http
          .get(
            Uri.parse(url),
            headers: headers,
          )
          .timeout(Duration(seconds: ApiConfig.connectionTimeout));
      return jsonDecode(res.body);
    } catch (e) {
      debugPrint('GET error to $endpoint: $e');
      return {'success': false, 'error': 'Connection error'};
    }
  }

  static Future<Map<String, dynamic>> _put(
      String endpoint, Map<String, dynamic> body) async {
    final headers = await _getHeaders();
    final url = '${ApiConfig.baseUrl}$endpoint';
    try {
      final res = await http
          .put(
            Uri.parse(url),
            headers: headers,
            body: jsonEncode(body),
          )
          .timeout(Duration(seconds: ApiConfig.connectionTimeout));
      return jsonDecode(res.body);
    } catch (e) {
      debugPrint('PUT error to $endpoint: $e');
      return {'success': false, 'error': 'Connection error'};
    }
  }

  static Future<Map<String, dynamic>> _delete(String endpoint) async {
    final headers = await _getHeaders();
    final url = '${ApiConfig.baseUrl}$endpoint';
    try {
      final res = await http
          .delete(
            Uri.parse(url),
            headers: headers,
          )
          .timeout(Duration(seconds: ApiConfig.connectionTimeout));
      return jsonDecode(res.body);
    } catch (e) {
      debugPrint('DELETE error to $endpoint: $e');
      return {'success': false, 'error': 'Connection error'};
    }
  }

  // Public wrappers for other services
  static Future<Map<String, dynamic>> get(String endpoint) async {
    return _get(endpoint);
  }

  static Future<Map<String, dynamic>> post(
      String endpoint, Map<String, dynamic> body) async {
    return _post(endpoint, body);
  }

  static Future<Map<String, dynamic>> put(
      String endpoint, Map<String, dynamic> body) async {
    return _put(endpoint, body);
  }

  static Future<Map<String, dynamic>> delete(String endpoint) async {
    return _delete(endpoint);
  }

  // ==================== AUTH ====================
  static Future<Map<String, dynamic>> login(
      String email, String password) async {
    return _post('/auth/login', {'email': email, 'password': password});
  }

  static Future<Map<String, dynamic>> register(
      String email, String password, String displayName) async {
    return _post('/auth/register',
        {'email': email, 'password': password, 'display_name': displayName});
  }

  static Future<Map<String, dynamic>> resetPassword(
    String email,
    String oldPassword,
    String newPassword,
  ) async {
    final encodedEmail = Uri.encodeComponent(email);
    final encodedOldPassword = Uri.encodeComponent(oldPassword);
    final encodedNewPassword = Uri.encodeComponent(newPassword);

    final res = await http.post(
      Uri.parse(
        '${ApiConfig.baseUrl}/auth/reset-password'
        '?email=$encodedEmail'
        '&old_password=$encodedOldPassword'
        '&new_password=$encodedNewPassword',
      ),
      headers: {'Content-Type': 'application/json'},
    ).timeout(Duration(seconds: ApiConfig.connectionTimeout));

    return jsonDecode(res.body);
  }

  // ==================== CHAT ====================
  static Future<Map<String, dynamic>> getChatSessions() async {
    return _get('/chat/sessions');
  }

  static Future<Map<String, dynamic>> createChatSession({String? name}) async {
    return _post('/chat/sessions', {'name': name ?? 'New Chat'});
  }

  static Future<Map<String, dynamic>> getChatSession(String id) async {
    return _get('/chat/sessions/$id');
  }

  static Future<Map<String, dynamic>> sendChatMessage(
      String sessionId, String message) async {
    return _post('/chat/sessions/$sessionId/messages', {'message': message});
  }

  static Future<Map<String, dynamic>> deleteChatSession(String id) async {
    return _delete('/chat/sessions/$id');
  }

  // ==================== KNOWLEDGE ====================
  static Future<Map<String, dynamic>> getKnowledge() async {
    return _get('/knowledge');
  }

  static Future<Map<String, dynamic>> addKnowledge(
      Map<String, dynamic> data) async {
    return _post('/knowledge', data);
  }

  static Future<Map<String, dynamic>> updateKnowledge(
      int id, Map<String, dynamic> data) async {
    return _put('/knowledge/$id', data);
  }

  static Future<Map<String, dynamic>> deleteKnowledge(int id) async {
    return _delete('/knowledge/$id');
  }

  static Future<Map<String, dynamic>> searchKnowledge(String query) async {
    return _get('/knowledge?search=${Uri.encodeComponent(query)}');
  }

  static Future<Map<String, dynamic>> generateKnowledgeReport(
      {required String period}) async {
    return _post('/knowledge/report', {'period': period});
  }

  // ==================== REPORT PDF ====================
  static Future<List<int>?> downloadReportPDF({required String period}) async {
    try {
      final headers = await _getHeaders();
      final res = await http
          .post(
            Uri.parse('${ApiConfig.baseUrl}/knowledge/report/pdf'),
            headers: headers,
            body: jsonEncode({'period': period}),
          )
          .timeout(Duration(seconds: ApiConfig.connectionTimeout));

      if (res.statusCode == 200) return res.bodyBytes;
      return null;
    } catch (e) {
      debugPrint('PDF download error: $e');
      return null;
    }
  }

  // ==================== PROJECTS ====================
  static Future<Map<String, dynamic>> getProjects() async {
    return _get('/projects');
  }

  static Future<Map<String, dynamic>> getVideoProjects() async {
    return _get('/video/list');
  }

  static Future<Map<String, dynamic>> deleteProject(String id) async {
    return _delete('/projects/$id');
  }

  // ==================== SETTINGS ====================
  static Future<Map<String, dynamic>> getSettings() async {
    return _get('/settings');
  }

  static Future<Map<String, dynamic>> updateSettings(
      Map<String, dynamic> data) async {
    return _put('/settings', data);
  }

  // ==================== VIDEO ====================
  static Future<Map<String, dynamic>> createVideoProject({
    String? prompt,
    String? niche,
    required int duration,
    String style = 'engaging',
    String language = 'id',
    String? productName,
    String? priceText,
    String? ctaText,
    String? brandName,
    String? productImageUrl,
  }) async {
    final payload = <String, dynamic>{
      'duration': duration,
      'style': style,
      'language': language,
    };

    if (prompt != null && prompt.trim().isNotEmpty) {
      payload['prompt'] = prompt.trim();
    }

    if (niche != null && niche.trim().isNotEmpty) {
      payload['niche'] = niche.trim();
    }

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

    return _post('/video/create', payload);
  }

  static Future<Map<String, dynamic>> getVideoStatus(String projectId) async {
    return _get('/video/status/$projectId');
  }

  static Future<Map<String, dynamic>> deleteVideoProject(
      String projectId) async {
    return _delete('/video/delete/$projectId');
  }

  static Future<String?> downloadVideo(String projectId) async {
    try {
      final headers = await _getHeaders();
      final res = await http
          .get(
            Uri.parse('${ApiConfig.baseUrl}/video/download/$projectId'),
            headers: headers,
          )
          .timeout(Duration(seconds: ApiConfig.videoTimeout));

      if (res.statusCode == 200) {
        final dir = Directory('/storage/emulated/0/Download/DIBS_Videos');
        if (!await dir.exists()) await dir.create(recursive: true);

        final timestamp = DateTime.now().millisecondsSinceEpoch;
        final file = File('${dir.path}/video_${projectId}_$timestamp.mp4');
        await file.writeAsBytes(res.bodyBytes);

        return file.path;
      }
      return null;
    } catch (e) {
      debugPrint('Download video error: $e');
      return null;
    }
  }

  // ==================== TOKO MODULE ====================
  static Future<Map<String, dynamic>> getTokoProducts(
      {String? category}) async {
    String endpoint = '/toko/products';
    if (category != null) endpoint += '?category=$category';
    return _get(endpoint);
  }

  static Future<Map<String, dynamic>> getTokoProduct(String productId) async {
    return _get('/toko/products/$productId');
  }

  static Future<Map<String, dynamic>> createTokoProduct(
      Map<String, dynamic> data) async {
    return _post('/toko/products', data);
  }

  static Future<Map<String, dynamic>> updateTokoProduct(
      String productId, Map<String, dynamic> data) async {
    return _put('/toko/products/$productId', data);
  }

  static Future<Map<String, dynamic>> deleteTokoProduct(
      String productId) async {
    return _delete('/toko/products/$productId');
  }

  static Future<Map<String, dynamic>> getTokoSales({int limit = 10}) async {
    return _get('/toko/sales?limit=$limit');
  }

  static Future<Map<String, dynamic>> getTokoDashboard() async {
    return _get('/toko/dashboard');
  }

  static Future<Map<String, dynamic>> scanVoice(String text,
      {bool autoSave = true}) async {
    return _post('/toko/sales/scan', {
      'text': text,
      'auto_save': autoSave,
    });
  }

  static Future<Map<String, dynamic>> createTokoSale(
      Map<String, dynamic> data) async {
    return _post('/toko/sales', data);
  }

  static Future<Map<String, dynamic>> getLowStockProducts() async {
    return _get('/toko/inventory/low-stock');
  }

  static Future<Map<String, dynamic>> scanBarcodeForStock(
      String barcode, int quantity,
      {String type = 'stock_in'}) async {
    return _post('/toko/stock/scan', {
      'barcode': barcode,
      'quantity': quantity,
      'type': type,
    });
  }

  static Future<Map<String, dynamic>> scanBarcodeForSale(
      String barcode, int quantity) async {
    return _post('/toko/sales/scan-barcode', {
      'barcode': barcode,
      'quantity': quantity,
    });
  }

  // ==================== UPLOAD ====================
  static Future<Map<String, dynamic>> uploadFile(String filePath) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('${ApiConfig.baseUrl}/chat/upload'),
    );

    request.headers.addAll(await _getHeaders());
    request.files.add(await http.MultipartFile.fromPath('file', filePath));

    var response = await request.send();
    var responseBody = await response.stream.bytesToString();

    return jsonDecode(responseBody);
  }

  static Future<Map<String, dynamic>> analyzeImage(String filePath) async {
    return uploadFile(filePath);
  }

  static Future<Map<String, dynamic>> analyzeDocument(String filePath) async {
    return uploadFile(filePath);
  }

  // ===== SOCIAL MEDIA =====
  static Future<Map<String, dynamic>> getSocialAccounts() async {
    return _get('/social/accounts');
  }

  static Future<Map<String, dynamic>> connectSocialAccount(
      Map<String, dynamic> data) async {
    return _post('/social/accounts', data);
  }

  static Future<Map<String, dynamic>> getSocialPosts(
      {String? platform, String? status}) async {
    String query = '';
    if (platform != null) query += 'platform=$platform&';
    if (status != null) query += 'status=$status&';
    if (query.isNotEmpty) query = '?' + query.substring(0, query.length - 1);

    return _get('/social/posts$query');
  }

  static Future<Map<String, dynamic>> createSocialPost(
      Map<String, dynamic> data) async {
    return _post('/social/posts', data);
  }

  static Future<Map<String, dynamic>> deleteSocialPost(String postId) async {
    return _delete('/social/posts/$postId');
  }

  static Future<Map<String, dynamic>> generateSocialCaption(
      Map<String, dynamic> data) async {
    return _post('/social/generate-caption', data);
  }

  static Future<Map<String, dynamic>> getSocialAnalytics(
      {String? platform, String period = '7days'}) async {
    String query = 'period=$period';
    if (platform != null) query += '&platform=$platform';

    return _get('/social/analytics?$query');
  }

  static Future<Map<String, dynamic>> disconnectSocialAccount(
      String accountId) async {
    return _delete('/social/accounts/$accountId');
  }

  // ==================== BARCODE LOOKUP ====================
  static Future<Map<String, dynamic>?> lookupProductByBarcode(
      String barcode) async {
    try {
      final url = 'https://world.openfoodfacts.org/api/v2/product/$barcode.json'
          '?fields=product_name,product_name_en,generic_name,generic_name_en,brands';

      final res = await http.get(Uri.parse(url));

      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);

        if (data['status'] == 1) {
          final product = Map<String, dynamic>.from(data['product'] ?? {});

          String pick(dynamic value) => (value ?? '').toString().trim();

          final name = [
            pick(product['product_name']),
            pick(product['product_name_en']),
            pick(product['generic_name']),
            pick(product['generic_name_en']),
          ].firstWhere(
            (v) => v.isNotEmpty,
            orElse: () => '',
          );

          final brand = pick(product['brands']);

          return {
            'name': name,
            'brand': brand,
          };
        }
      }
    } catch (e) {
      debugPrint("Barcode lookup error: $e");
    }

    return null;
  }

  // ==================== TOKO PAYMENT ====================
  static Future<Map<String, dynamic>> getTokoPaymentSettings() async {
    return _get('/toko/payment-settings');
  }

  static Future<Map<String, dynamic>> saveTokoPaymentSettings(
      Map<String, dynamic> data) async {
    return _post('/toko/payment-settings', data);
  }

  // ==================== INVENTORY AI IMPORT / EXPORT ====================
  static Future<Map<String, dynamic>> importProductsCSV(String filePath) async {
    try {
      final headers = await _getHeaders();

      final request = http.MultipartRequest(
        'POST',
        Uri.parse('${ApiConfig.baseUrl}/inventory-ai/products/import'),
      );

      request.headers.addAll({
        'Authorization': headers['Authorization'] ?? '',
      });

      request.files.add(await http.MultipartFile.fromPath('file', filePath));

      final response = await request.send().timeout(
            Duration(seconds: ApiConfig.connectionTimeout * 3),
          );

      final body = await response.stream.bytesToString();
      return jsonDecode(body);
    } catch (e) {
      debugPrint('Import CSV error: $e');
      return {'status': 'error', 'message': 'Import CSV gagal: $e'};
    }
  }

  static Future<Uint8List?> exportProductsCSV() async {
    try {
      final headers = await _getHeaders();

      final res = await http
          .get(
            Uri.parse('${ApiConfig.baseUrl}/inventory-ai/products/export'),
            headers: headers,
          )
          .timeout(Duration(seconds: ApiConfig.connectionTimeout));

      if (res.statusCode == 200) {
        return res.bodyBytes;
      }

      debugPrint('Export CSV failed: ${res.statusCode} ${res.body}');
      return null;
    } catch (e) {
      debugPrint('Export CSV error: $e');
      return null;
    }
  }

  // ==================== BUSINESS BRAIN ====================
  static Future<Map<String, dynamic>> classifyBusinessNote(String text) async {
    return _post('/business-brain/classify-note', {'text': text});
  }

  static Future<Map<String, dynamic>> getDailyBusinessSummary() async {
    return _get('/business-brain/daily-summary');
  }

  static Future<Map<String, dynamic>> getSalesInsight(
      {String period = 'today'}) async {
    return _get('/business-brain/sales-insight?period=$period');
  }
}
