#!/usr/bin/env python3
"""
Update Toko Provider - Tambah variable untuk mode inklusif
"""
import re

def update_toko_provider():
    # Backup dulu
    import shutil
    shutil.copy2('lib/providers/toko_provider.dart', 'lib/providers/toko_provider.dart.bak')
    print("✅ Backup created: toko_provider.dart.bak")
    
    # Baca file
    with open('lib/providers/toko_provider.dart', 'r') as f:
        content = f.read()
    
    # 1. TAMBAH VARIABLE DI BAGIAN ATAS (setelah deklarasi variable lain)
    var_pattern = r'(  Map<String, dynamic> _dashboard = {\n.*?  bool _isLoading = false;\n  String\? _error;)'
    
    new_vars = '''  Map<String, dynamic> _dashboard = {
    'today_sales': 0,
    'today_transactions': 0,
    'total_products': 0,
    'low_stock': 0,
  };

  bool _isLoading = false;
  String? _error;
  
  // Untuk mode inklusif
  String _lastVoiceText = '';
  bool _isInclusiveMode = false;'''
    
    content = re.sub(var_pattern, new_vars, content, flags=re.DOTALL)
    
    # 2. TAMBAH GETTERS
    getter_pattern = r'(  bool get isLoading => _isLoading;\n  String\? get error => _error;)'
    
    new_getters = '''  bool get isLoading => _isLoading;
  String? get error => _error;
  
  // Inclusive mode getters
  String get lastVoiceText => _lastVoiceText;
  bool get isInclusiveMode => _isInclusiveMode;'''
    
    content = re.sub(getter_pattern, new_getters, content)
    
    # 3. TAMBAH SETTER
    setter_pattern = r'(  int get cartTotal \{\n    return _cartItems\.fold\(0, \(sum, item\) => sum \+ \(item\[\'subtotal\'\] as int\? \?\? 0\)\);\n  \})'
    
    new_setter = '''  int get cartTotal {
    return _cartItems.fold(0, (sum, item) => sum + (item['subtotal'] as int? ?? 0));
  }
  
  // Inclusive mode methods
  void setInclusiveMode(bool value) {
    _isInclusiveMode = value;
    notifyListeners();
  }'''
    
    content = re.sub(setter_pattern, new_setter, content)
    
    # 4. UPDATE FUNCTION processVoiceScan
    voice_pattern = r'(  Future<void> processVoiceScan\(String text\) async \{\n    try \{\n      final response = await ApiService\.scanVoice\(text, autoSave: false\);\n\n      if \(response\[\'status\'\] == \'success\'\) \{\n        final items = response\[\'data\'\]\[\'items\'\] as List\?;\n\n        if \(items != null\) \{\n          for \(var item in items\) \{\n            // Find product by name\n            final product = _products\.firstWhere\(\n              \(p\) => p\[\'name\'\]\.toString\(\)\.toLowerCase\(\)\.contains\(\n                item\[\'name\'\]\.toString\(\)\.toLowerCase\(\)\n              \),\n              orElse: \(\) => \{\},\n            \);\n\n            if \(product\.isNotEmpty\) \{\n              addToCart\(product, item\[\'quantity\'\] \?\? 1\);\n            \}\n          \}\n        \}\n      \}\n\n    \} catch \(e\) \{\n      _error = e\.toString\(\);\n      debugPrint\(\'❌ Voice scan error: \$e\'\);\n    \}\n  \})'
    
    new_voice = '''  Future<void> processVoiceScan(String text) async {
    _lastVoiceText = text;
    notifyListeners();
    
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
        
        debugPrint('✅ Voice scan berhasil: $text');
      }

    } catch (e) {
      _error = e.toString();
      debugPrint('❌ Voice scan error: $e');
    }
  }'''
    
    content = re.sub(voice_pattern, new_voice, content, flags=re.DOTALL)
    
    # Tulis kembali
    with open('lib/providers/toko_provider.dart', 'w') as f:
        f.write(content)
    
    print("✅ toko_provider.dart updated!")
    print("   - Added _lastVoiceText & _isInclusiveMode variables")
    print("   - Added getters & setters for inclusive mode")
    print("   - Updated processVoiceScan to save lastVoiceText")

def check_result():
    """Verifikasi hasil update"""
    print("\n" + "="*50)
    print("🔍 VERIFIKASI HASIL UPDATE")
    print("="*50)
    
    with open('lib/providers/toko_provider.dart', 'r') as f:
        content = f.read()
    
    # Cek variable baru
    if '_lastVoiceText' in content:
        print("✅ _lastVoiceText added")
    else:
        print("❌ _lastVoiceText not found")
    
    if '_isInclusiveMode' in content:
        print("✅ _isInclusiveMode added")
    else:
        print("❌ _isInclusiveMode not found")
    
    # Cek getter
    if 'String get lastVoiceText' in content:
        print("✅ lastVoiceText getter added")
    else:
        print("❌ lastVoiceText getter not found")
    
    # Cek setter
    if 'void setInclusiveMode' in content:
        print("✅ setInclusiveMode added")
    else:
        print("❌ setInclusiveMode not found")
    
    # Cek update processVoiceScan
    if '_lastVoiceText = text' in content:
        print("✅ processVoiceScan updated with _lastVoiceText")
    else:
        print("❌ processVoiceScan not updated properly")

if __name__ == "__main__":
    update_toko_provider()
    check_result()
    print("\n🚀 NEXT STEP: Buat InclusiveCheckoutScreen widget")
