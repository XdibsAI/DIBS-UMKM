import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class TokoProvider extends ChangeNotifier {
  static const String _baseUrl = 'http://94.100.26.128:8081/api/v1/toko';

  String? _authToken;
  List<Map<String, dynamic>> _products = [];
  List<Map<String, dynamic>> _cartItems = [];
  List<Map<String, dynamic>> _recentSales = [];
  Map<String, dynamic> _dashboard = {};
  bool _isLoading = false;
  String _lastVoiceText = '';

  List<Map<String, dynamic>> get products => _products;
  List<Map<String, dynamic>> get cartItems => _cartItems;
  List<Map<String, dynamic>> get cart => _cartItems;
  List<Map<String, dynamic>> get recentSales => _recentSales;
  Map<String, dynamic> get dashboard => _dashboard;
  bool get isLoading => _isLoading;
  String get lastVoiceText => _lastVoiceText;

  int get cartTotal =>
      _cartItems.fold(0, (sum, item) => sum + (item['subtotal'] as int? ?? 0));

  void setAuthToken(String token) {
    _authToken = token;
  }

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (_authToken != null) 'Authorization': 'Bearer $_authToken',
      };

  Future<void> loadDashboard() async {
    _isLoading = true;
    notifyListeners();
    try {
      final response =
          await http.get(Uri.parse('$_baseUrl/dashboard'), headers: _headers);
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _dashboard = data['data'] ?? {};
        _recentSales =
            List<Map<String, dynamic>>.from(data['data']['recent_sales'] ?? []);
      }
    } catch (e) {
      print('Error loading dashboard: $e');
    }
    _isLoading = false;
    notifyListeners();
  }

  Future<void> loadProducts() async {
    print('🔵 [LOAD] loadProducts() called');
    print('🔵 [LOAD] Auth token: ${_authToken?.substring(0, 20)}...');
    print('🔵 [LOAD] URL: $_baseUrl/products');

    _isLoading = true;
    notifyListeners();

    try {
      final response = await http.get(
        Uri.parse('$_baseUrl/products'),
        headers: _headers,
      );

      print('🔵 [LOAD] Status: ${response.statusCode}');
      print('🔵 [LOAD] Response: ${response.body.substring(0, 200)}...');

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _products = List<Map<String, dynamic>>.from(data['data'] ?? []);
        print('🔵 [LOAD] Loaded ${_products.length} products');
        print('🔵 [LOAD] Products: ${_products.map((p) => p['name']).toList()}');
      } else {
        print('🔴 [LOAD] Failed: ${response.statusCode}');
      }
    } catch (e) {
      print('🔴 [LOAD] Error: $e');
    }

    _isLoading = false;
    notifyListeners();
    print('🔵 [LOAD] Final _products.length: ${_products.length}');
  }

  Future<void> addProduct(Map<String, dynamic> data) async {
    try {
      await http.post(
        Uri.parse('$_baseUrl/products'),
        headers: _headers,
        body: json.encode(data),
      );
      await loadProducts();
      await loadDashboard();
    } catch (e) {
      print('Error adding product: $e');
    }
  }

  Future<void> updateProduct(dynamic id, Map<String, dynamic> data) async {
    try {
      await http.put(
        Uri.parse('$_baseUrl/products/$id'),
        headers: _headers,
        body: json.encode(data),
      );
      await loadProducts();
    } catch (e) {
      print('Error updating product: $e');
    }
  }

  Future<void> deleteProduct(dynamic id) async {
    try {
      await http.delete(
        Uri.parse('$_baseUrl/products/$id'),
        headers: _headers,
      );
      await loadProducts();
    } catch (e) {
      print('Error deleting product: $e');
    }
  }

  void searchProducts(String query) {
    notifyListeners();
  }

  int _asInt(dynamic value) {
    if (value is int) return value;
    if (value is double) return value.toInt();
    if (value is String) {
      return int.tryParse(value) ?? double.tryParse(value)?.toInt() ?? 0;
    }
    return 0;
  }

  String _normalizeText(String text) {
    var normalized = text.toLowerCase().trim();

    const replacements = {
      'á': 'a',
      'à': 'a',
      'â': 'a',
      'ä': 'a',
      'é': 'e',
      'è': 'e',
      'ê': 'e',
      'ë': 'e',
      'í': 'i',
      'ì': 'i',
      'î': 'i',
      'ï': 'i',
      'ó': 'o',
      'ò': 'o',
      'ô': 'o',
      'ö': 'o',
      'ú': 'u',
      'ù': 'u',
      'û': 'u',
      'ü': 'u',
    };

    replacements.forEach((k, v) {
      normalized = normalized.replaceAll(k, v);
    });

    normalized = normalized.replaceAll(RegExp(r'[^a-z0-9\s]'), ' ');
    normalized = normalized.replaceAll(RegExp(r'\s+'), ' ').trim();
    return normalized;
  }

  int _extractQuantity(String text) {
    final normalized = _normalizeText(text);

    final digitMatch = RegExp(r'\b(\d+)\b').firstMatch(normalized);
    if (digitMatch != null) {
      return int.tryParse(digitMatch.group(1)!) ?? 1;
    }

    const wordsToNumber = {
      'satu': 1,
      'dua': 2,
      'tiga': 3,
      'empat': 4,
      'lima': 5,
      'enam': 6,
      'tujuh': 7,
      'delapan': 8,
      'sembilan': 9,
      'sepuluh': 10,
    };

    for (final entry in wordsToNumber.entries) {
      if (normalized.contains(entry.key)) {
        return entry.value;
      }
    }

    return 1;
  }

  int _scoreProductMatch(String inputText, Map<String, dynamic> product) {
    final input = _normalizeText(inputText);
    final productName = _normalizeText(product['name']?.toString() ?? '');
    final barcode = _normalizeText(product['barcode']?.toString() ?? '');

    if (productName.isEmpty) return 0;

    if (input == productName) return 100;
    if (barcode.isNotEmpty && input.contains(barcode)) return 95;
    if (input.contains(productName)) return 90;
    if (productName.contains(input) && input.length >= 4) return 75;

    final inputWords = input.split(' ').where((e) => e.isNotEmpty).toSet();
    final productWords = productName.split(' ').where((e) => e.isNotEmpty).toSet();

    if (inputWords.isEmpty || productWords.isEmpty) return 0;

    int score = 0;
    for (final word in productWords) {
      if (inputWords.contains(word)) {
        score += 20;
      } else {
        for (final inputWord in inputWords) {
          if (inputWord.length >= 4 &&
              word.length >= 4 &&
              (word.contains(inputWord) || inputWord.contains(word))) {
            score += 10;
            break;
          }
        }
      }
    }

    return score;
  }

  void addToCart(Map<String, dynamic> product, int quantity) {
    final existingIndex =
        _cartItems.indexWhere((item) => item['id'] == product['id']);
    final price = _asInt(product['price']);

    if (existingIndex >= 0) {
      _cartItems[existingIndex]['quantity'] += quantity;
      _cartItems[existingIndex]['subtotal'] =
          _cartItems[existingIndex]['quantity'] * _asInt(_cartItems[existingIndex]['price']);
    } else {
      _cartItems.add({
        'id': product['id'],
        'name': product['name'],
        'price': price,
        'quantity': quantity,
        'subtotal': quantity * price,
      });
    }

    print('🛒 Added to cart: ${product['name']} x$quantity');
    print('🛒 Cart now has: ${_cartItems.length} items');
    notifyListeners();
  }

  void incrementCartItem(dynamic productId) {
    final index = _cartItems.indexWhere((item) => item['id'] == productId);
    if (index >= 0) {
      _cartItems[index]['quantity']++;
      _cartItems[index]['subtotal'] =
          _cartItems[index]['quantity'] * _asInt(_cartItems[index]['price']);
      notifyListeners();
    }
  }

  void decrementCartItem(dynamic productId) {
    final index = _cartItems.indexWhere((item) => item['id'] == productId);
    if (index >= 0) {
      if (_cartItems[index]['quantity'] > 1) {
        _cartItems[index]['quantity']--;
        _cartItems[index]['subtotal'] =
            _cartItems[index]['quantity'] * _asInt(_cartItems[index]['price']);
      } else {
        _cartItems.removeAt(index);
      }
      notifyListeners();
    }
  }

  void clearCart() {
    _cartItems.clear();
    notifyListeners();
  }

  Future<Map<String, dynamic>> checkout({String paymentMethod = 'cash'}) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/sales'),
        headers: _headers,
        body: json.encode({
          'items': _cartItems,
          'total': cartTotal,
          'payment_method': paymentMethod,
        }),
      );

      final data = json.decode(response.body);

      if (response.statusCode == 200 && data['status'] == 'success') {
        clearCart();
        await loadDashboard();
        await loadProducts();
        return Map<String, dynamic>.from(data);
      }

      throw Exception(data['detail'] ?? data['message'] ?? 'Checkout gagal');
    } catch (e) {
      print('Error checkout: $e');
      rethrow;
    }
  }


  Future<Map<String, dynamic>> processVoiceScan(String text) async {
    print('🎤 [VOICE] Input: "$text"');
    _lastVoiceText = text;

    print('📦 [VOICE] Force loading products...');
    await loadProducts();
    print('📦 [VOICE] Loaded ${_products.length} products');

    if (_products.isEmpty) {
      const result = {
        'matched': false,
        'addedCount': 0,
        'message': 'Produk belum tersedia untuk diproses',
        'items': <Map<String, dynamic>>[],
      };
      print('❌ [VOICE] No products after load!');
      notifyListeners();
      return result;
    }

    final cleanText = _normalizeText(text);
    final quantity = _extractQuantity(cleanText);

    print('🔍 [VOICE] Searching normalized: "$cleanText"');
    print('🔢 [VOICE] Quantity: $quantity');
    print('📦 [VOICE] Available: ${_products.map((p) => p['name']).toList()}');

    Map<String, dynamic>? bestProduct;
    int bestScore = 0;

    for (final product in _products) {
      final score = _scoreProductMatch(cleanText, product);
      print('🧠 [VOICE] Score ${product['name']}: $score');

      if (score > bestScore) {
        bestScore = score;
        bestProduct = product;
      }
    }

    if (bestProduct == null || bestScore < 25) {
      final result = {
        'matched': false,
        'addedCount': 0,
        'message': 'Produk tidak dikenali dari input: "$text"',
        'items': <Map<String, dynamic>>[],
        'normalizedText': cleanText,
        'score': bestScore,
      };
      print('❌ [VOICE] No match for "$cleanText"');
      notifyListeners();
      return result;
    }

    addToCart(bestProduct, quantity);

    final result = {
      'matched': true,
      'addedCount': 1,
      'message': 'Menambahkan ${bestProduct['name']} x$quantity',
      'items': [
        {
          'id': bestProduct['id'],
          'name': bestProduct['name'],
          'quantity': quantity,
          'score': bestScore,
        }
      ],
      'normalizedText': cleanText,
      'score': bestScore,
    };

    print('✅ [VOICE] MATCH: ${bestProduct['name']} x$quantity | score=$bestScore');
    notifyListeners();
    return result;
  }

  Future<Map<String, dynamic>> scanBarcode(String barcode, {int quantity = 1}) async {
    try {
      final response = await http.post(
        Uri.parse('$_baseUrl/sales/scan-barcode'),
        headers: _headers,
        body: json.encode({
          'barcode': barcode,
          'quantity': quantity,
        }),
      );

      final data = json.decode(response.body);

      if (response.statusCode == 200) {
        return Map<String, dynamic>.from(data);
      }

      throw Exception(data['detail'] ?? data['message'] ?? 'Gagal scan barcode');
    } catch (e) {
      print('❌ [BARCODE] Error: $e');
      rethrow;
    }
  }

  Future<Map<String, dynamic>> processVoiceCommand(String text) =>
      processVoiceScan(text);
}
