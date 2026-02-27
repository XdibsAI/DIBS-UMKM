import 'package:flutter/material.dart';
import '../services/api_service.dart';

class TokoProvider extends ChangeNotifier {
  // Data
  List<Map<String, dynamic>> _products = [];
  List<Map<String, dynamic>> _cartItems = [];
  List<Map<String, dynamic>> _recentSales = [];
  Map<String, dynamic> _dashboard = {
    'today_sales': 0,
    'today_transactions': 0,
    'total_products': 0,
    'low_stock': 0,
  };
  
  bool _isLoading = false;
  String? _error;

  // Getters
  List<Map<String, dynamic>> get products => _products;
  List<Map<String, dynamic>> get cartItems => _cartItems;
  List<Map<String, dynamic>> get recentSales => _recentSales;
  Map<String, dynamic> get dashboard => _dashboard;
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  int get cartTotal {
    return _cartItems.fold(0, (sum, item) => sum + (item['subtotal'] as int? ?? 0));
  }

  // Load Dashboard
  Future<void> loadDashboard() async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await ApiService.getTokoDashboard();
      
      if (response['status'] == 'success') {
        _dashboard = response['data'] ?? _dashboard;
      }
      
      // Load recent sales
      final salesResponse = await ApiService.getTokoSales(limit: 5);
      if (salesResponse['status'] == 'success') {
        _recentSales = List<Map<String, dynamic>>.from(salesResponse['data'] ?? []);
      }
      
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Load dashboard error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Load Products
  Future<void> loadProducts({String? category}) async {
    _isLoading = true;
    notifyListeners();

    try {
      final response = await ApiService.getTokoProducts(category: category);
      
      if (response['status'] == 'success') {
        _products = List<Map<String, dynamic>>.from(response['data'] ?? []);
      }
      
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Load products error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Search Products
  void searchProducts(String query) {
    if (query.isEmpty) {
      loadProducts();
      return;
    }
    
    _products = _products.where((p) {
      final name = (p['name'] ?? '').toString().toLowerCase();
      return name.contains(query.toLowerCase());
    }).toList();
    
    notifyListeners();
  }

  // Add Product
  Future<void> addProduct(Map<String, dynamic> data) async {
    try {
      final response = await ApiService.createTokoProduct(data);
      
      if (response['status'] == 'success') {
        await loadProducts();
      }
      
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Add product error: $e');
    }
  }

  // Update Product
  Future<void> updateProduct(int productId, Map<String, dynamic> data) async {
    try {
      final response = await ApiService.updateTokoProduct(productId.toString(), data);
      
      if (response['status'] == 'success') {
        await loadProducts();
      }
      
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Update product error: $e');
    }
  }

  // Delete Product
  Future<void> deleteProduct(int productId) async {
    try {
      final response = await ApiService.deleteTokoProduct(productId.toString());
      
      if (response['status'] == 'success') {
        _products.removeWhere((p) => p['id'] == productId);
        notifyListeners();
      }
      
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Delete product error: $e');
    }
  }

  // Cart Operations
  void addToCart(Map<String, dynamic> product, int quantity) {
    final existingIndex = _cartItems.indexWhere((item) => item['id'] == product['id']);
    
    if (existingIndex >= 0) {
      _cartItems[existingIndex]['quantity'] += quantity;
      _cartItems[existingIndex]['subtotal'] = 
          _cartItems[existingIndex]['quantity'] * _cartItems[existingIndex]['price'];
    } else {
      _cartItems.add({
        'id': product['id'],
        'name': product['name'],
        'price': product['price'],
        'quantity': quantity,
        'subtotal': product['price'] * quantity,
      });
    }
    
    notifyListeners();
  }

  void incrementCartItem(int productId) {
    final index = _cartItems.indexWhere((item) => item['id'] == productId);
    if (index >= 0) {
      _cartItems[index]['quantity']++;
      _cartItems[index]['subtotal'] = 
          _cartItems[index]['quantity'] * _cartItems[index]['price'];
      notifyListeners();
    }
  }

  void decrementCartItem(int productId) {
    final index = _cartItems.indexWhere((item) => item['id'] == productId);
    if (index >= 0) {
      if (_cartItems[index]['quantity'] > 1) {
        _cartItems[index]['quantity']--;
        _cartItems[index]['subtotal'] = 
            _cartItems[index]['quantity'] * _cartItems[index]['price'];
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

  // Voice Scan Processing
  Future<void> processVoiceScan(String text) async {
    try {
      final response = await ApiService.scanVoice(text, autoSave: false);
      
      if (response['status'] == 'success') {
        final items = response['data']['items'] as List?;
        
        if (items != null) {
          for (var item in items) {
            // Find product by name
            final product = _products.firstWhere(
              (p) => p['name'].toString().toLowerCase().contains(
                item['name'].toString().toLowerCase()
              ),
              orElse: () => {},
            );
            
            if (product.isNotEmpty) {
              addToCart(product, item['quantity'] ?? 1);
            }
          }
        }
      }
      
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Voice scan error: $e');
    }
  }

  // Checkout
  Future<bool> checkout() async {
    try {
      final saleData = {
        'items': _cartItems,
        'total': cartTotal,
        'created_at': DateTime.now().toIso8601String(),
      };
      
      final response = await ApiService.createTokoSale(saleData);
      
      if (response['status'] == 'success') {
        clearCart();
        await loadDashboard();
        return true;
      }
      
      return false;
    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Checkout error: $e');
      return false;
    }
  }
}
