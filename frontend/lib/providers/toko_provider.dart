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
  
  int get cartTotal => _cartItems.fold(0, (sum, item) => sum + (item['subtotal'] as int? ?? 0));

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
      final response = await http.get(Uri.parse('$_baseUrl/dashboard'), headers: _headers);
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _dashboard = data['data'] ?? {};
        _recentSales = List<Map<String, dynamic>>.from(data['data']['recent_sales'] ?? []);
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
        headers: _headers
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
      await http.post(Uri.parse('$_baseUrl/products'), headers: _headers, body: json.encode(data));
      await loadProducts();
      await loadDashboard();
    } catch (e) {
      print('Error adding product: $e');
    }
  }

  Future<void> updateProduct(dynamic id, Map<String, dynamic> data) async {
    try {
      await http.put(Uri.parse('$_baseUrl/products/$id'), headers: _headers, body: json.encode(data));
      await loadProducts();
    } catch (e) {
      print('Error updating product: $e');
    }
  }

  Future<void> deleteProduct(dynamic id) async {
    try {
      await http.delete(Uri.parse('$_baseUrl/products/$id'), headers: _headers);
      await loadProducts();
    } catch (e) {
      print('Error deleting product: $e');
    }
  }

  void searchProducts(String query) {
    notifyListeners();
  }

  void addToCart(Map<String, dynamic> product, int quantity) {
    final existingIndex = _cartItems.indexWhere((item) => item['id'] == product['id']);
    if (existingIndex >= 0) {
      _cartItems[existingIndex]['quantity'] += quantity;
      _cartItems[existingIndex]['subtotal'] = _cartItems[existingIndex]['quantity'] * _cartItems[existingIndex]['price'];
    } else {
      _cartItems.add({
        'id': product['id'],
        'name': product['name'],
        'price': product['price'],
        'quantity': quantity,
        'subtotal': quantity * (product['price'] as num).toInt(),
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
      _cartItems[index]['subtotal'] = _cartItems[index]['quantity'] * _cartItems[index]['price'];
      notifyListeners();
    }
  }

  void decrementCartItem(dynamic productId) {
    final index = _cartItems.indexWhere((item) => item['id'] == productId);
    if (index >= 0) {
      if (_cartItems[index]['quantity'] > 1) {
        _cartItems[index]['quantity']--;
        _cartItems[index]['subtotal'] = _cartItems[index]['quantity'] * _cartItems[index]['price'];
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

  Future<void> checkout() async {
    try {
      await http.post(Uri.parse('$_baseUrl/sales'), headers: _headers, body: json.encode({'items': _cartItems, 'total': cartTotal}));
      clearCart();
      await loadDashboard();
    } catch (e) {
      print('Error checkout: $e');
    }
  }

  Future<void> processVoiceScan(String text) async {
    print('🎤 [VOICE] Input: "$text"');
    _lastVoiceText = text;
    
    // ALWAYS reload to ensure fresh data
    print('📦 [VOICE] Force loading products...');
    await loadProducts();
    print('📦 [VOICE] Loaded ${_products.length} products');
    
    if (_products.isEmpty) {
      print('❌ [VOICE] No products after load!');
      notifyListeners();
      return;
    }
    
    final cleanText = text.toLowerCase().trim();
    print('🔍 [VOICE] Searching: "$cleanText"');
    print('📦 [VOICE] Available: ${_products.map((p) => p['name']).toList()}');
    
    for (var product in _products) {
      final productName = product['name'].toString().toLowerCase();
      
      if (cleanText.contains(productName) || productName.contains(cleanText)) {
        int quantity = 1;
        
        // Check numbers
        final numMatch = RegExp(r'(\d+)').firstMatch(cleanText);
        if (numMatch != null) {
          quantity = int.parse(numMatch.group(0)!);
        } 
        // Indonesian numbers
        else if (cleanText.contains('satu')) quantity = 1;
        else if (cleanText.contains('dua')) quantity = 2;
        else if (cleanText.contains('tiga')) quantity = 3;
        else if (cleanText.contains('empat')) quantity = 4;
        else if (cleanText.contains('lima')) quantity = 5;
        
        print('✅ [VOICE] MATCH: ${product['name']} x$quantity');
        addToCart(product, quantity);
        notifyListeners();
        return;
      }
    }
    
    print('❌ [VOICE] No match for "$cleanText"');
    notifyListeners();
  }

  Future<void> processVoiceCommand(String text) => processVoiceScan(text);
}
