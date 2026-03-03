#!/usr/bin/env python3
"""
Fix processVoiceScan function manually
"""
import re

def fix_voice_scan():
    # Baca file
    with open('lib/providers/toko_provider.dart', 'r') as f:
        content = f.read()
    
    # Cari fungsi processVoiceScan yang lama
    old_func = r'(Future<void> processVoiceScan\(String text\) async \{\s+try \{\s+final response = await ApiService\.scanVoice\(text, autoSave: false\);\s+if \(response\[\'status\'\] == \'success\'\) \{\s+final items = response\[\'data\'\]\[\'items\'\] as List\?;\s+if \(items != null\) \{\s+for \(var item in items\) \{\s+// Find product by name\s+final product = _products\.firstWhere\(\s+\(p\) => p\[\'name\'\]\.toString\(\)\.toLowerCase\(\)\.contains\(\s+item\[\'name\'\]\.toString\(\)\.toLowerCase\(\)\s+\),\s+orElse: \(\) => \{\},\s+\);\s+if \(product\.isNotEmpty\) \{\s+addToCart\(product, item\[\'quantity\'\] \?\? 1\);\s+\}\s+\}\s+\}\s+\}\s+\} catch \(e\) \{\s+_error = e\.toString\(\);\s+debugPrint\(\'❌ Voice scan error: \$e\'\);\s+\}\s+\})'
    
    # Fungsi baru dengan _lastVoiceText
    new_func = '''Future<void> processVoiceScan(String text) async {
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
    
    # Ganti fungsi lama dengan baru
    new_content = re.sub(old_func, new_func, content, flags=re.DOTALL)
    
    # Tulis kembali
    with open('lib/providers/toko_provider.dart', 'w') as f:
        f.write(new_content)
    
    print("✅ processVoiceScan updated successfully!")

def verify():
    print("\n🔍 VERIFIKASI:")
    with open('lib/providers/toko_provider.dart', 'r') as f:
        content = f.read()
    
    if '_lastVoiceText = text' in content:
        print("✅ _lastVoiceText = text found")
    else:
        print("❌ _lastVoiceText = text not found")
    
    if 'notifyListeners()' in content and 'processVoiceScan' in content:
        print("✅ notifyListeners found in processVoiceScan")
    else:
        print("❌ notifyListeners not found")

if __name__ == "__main__":
    fix_voice_scan()
    verify()
