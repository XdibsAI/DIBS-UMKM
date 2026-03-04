import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:flutter/material.dart';

class TokoProvider extends ChangeNotifier {
  List<Map<String, dynamic>> _products = [];
  List<Map<String, dynamic>> _cartItems = [];
  bool _isLoading = false;
  String _lastVoiceText = "";

  List<Map<String, dynamic>> get products => _products;
  List<Map<String, dynamic>> get cartItems => _cartItems;
  String get lastVoiceText => _lastVoiceText;
  double get cartTotal => _cartItems.fold(0, (sum, item) => sum + (item['subtotal'] as num).toDouble());

  static const String apiUrl = 'http://94.100.26.128:8081/api/v1';

  // --- CEK KONEKSI & LOAD DATA ---
  Future<void> loadProducts() async {
    print("🔍 [Dibs-Log] Mencoba tarik data produk dari: $apiUrl/products");
    try {
      final response = await http.get(Uri.parse('$apiUrl/products'));
      print("📡 [Dibs-Log] Status Code API: ${response.statusCode}");
      if (response.statusCode == 200) {
        _products = (json.decode(response.body) as List).cast<Map<String, dynamic>>();
        print("📦 [Dibs-Log] Berhasil muat ${_products.length} produk dari database.");
      }
    } catch (e) {
      print("❌ [Dibs-Log] ERROR KONEKSI: $e");
    }
    notifyListeners();
  }

  // --- SIMPAN KE DATABASE ---
  Future<void> addProduct(Map<String, dynamic> data) async {
    print("🚀 [Dibs-Log] Mengirim produk baru ke database: ${data['name']}");
    try {
      final response = await http.post(
        Uri.parse('$apiUrl/products'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode(data),
      );
      print("📡 [Dibs-Log] Respon Server: ${response.statusCode}");
      if (response.statusCode == 200 || response.statusCode == 201) {
        print("✅ [Dibs-Log] Produk Tersimpan!");
        await loadProducts();
      }
    } catch (e) {
      print("❌ [Dibs-Log] GAGAL SIMPAN: $e");
    }
  }

  // --- VOICE LOGIC ---
  Future<void> processVoiceCommand(String command) async {
    print("🎙️ [Dibs-Log] Voice Diterima: '$command'");
    _lastVoiceText = command;
    
    if (_products.isEmpty) {
      print("⚠️ [Dibs-Log] Daftar produk kosong, menarik data dulu...");
      await loadProducts();
    }

    String cleanCommand = command.toLowerCase();
    bool found = false;

    for (var product in _products) {
      String pName = product['name'].toString().toLowerCase();
      if (cleanCommand.contains(pName)) {
        print("🎯 [Dibs-Log] MATCH! Menambah $pName ke keranjang.");
        addToCart(product, 1);
        found = true;
        break;
      }
    }

    if (!found) print("❓ [Dibs-Log] Produk tidak ditemukan untuk suara: '$command'");
    notifyListeners();
  }

  void addToCart(Map<String, dynamic> product, int qty) {
    _cartItems.add({
      'id': product['id'],
      'name': product['name'],
      'quantity': qty,
      'price': product['price'],
      'subtotal': qty * (double.tryParse(product['price'].toString()) ?? 0),
    });
    notifyListeners();
  }
  
  void clearCart() { _cartItems.clear(); notifyListeners(); }
}
