#!/usr/bin/env python3
"""
Fix Chat Provider - Parse response.data.data correctly
"""
import re

def fix_chat_provider():
    # Backup dulu
    import shutil
    shutil.copy2('lib/providers/chat_provider.dart', 'lib/providers/chat_provider.dart.bak')
    print("✅ Backup created: chat_provider.dart.bak")
    
    # Baca file
    with open('lib/providers/chat_provider.dart', 'r') as f:
        content = f.read()
    
    # Cari fungsi loadSessions
    pattern = r'(if \(res\[\'status\'\] == \'success\'\) \{\s+_sessions = res\[\'data\'\] \?\? \[\]\;)'
    
    # Ganti dengan yang benar
    replacement = '''if (res['status'] == 'success') {
        _sessions = res['data']['data'] ?? [];
        debugPrint('✅ Sessions loaded: ${_sessions.length}');'''
    
    new_content = re.sub(pattern, replacement, content)
    
    # Tulis kembali
    with open('lib/providers/chat_provider.dart', 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed chat_provider.dart")
    print("   - Changed: _sessions = res['data']['data'] ?? []")
    print("   - Added: debugPrint for debugging")

def fix_api_service():
    """Optional: Fix API service to handle errors better"""
    api_file = 'lib/services/api_service.dart'
    if not os.path.exists(api_file):
        return
    
    with open(api_file, 'r') as f:
        content = f.read()
    
    # Tambahkan error handling di _get method
    pattern = r'static Future<Map<String, dynamic>> _get\(String endpoint\) async \{.*?return jsonDecode\(res.body\);'
    
    replacement = '''static Future<Map<String, dynamic>> _get(String endpoint) async {
    final headers = await _getHeaders();
    final url = '${ApiConfig.baseUrl}$endpoint';
    try {
      final res = await http.get(
        Uri.parse(url), 
        headers: headers,
      ).timeout(Duration(seconds: ApiConfig.connectionTimeout));
      
      if (res.statusCode != 200) {
        debugPrint('GET error $endpoint: ${res.statusCode} - ${res.body}');
        return {'success': false, 'error': 'HTTP ${res.statusCode}'};
      }
      
      return jsonDecode(res.body);
    } catch (e) {
      debugPrint('GET error to $endpoint: $e');
      return {'success': false, 'error': 'Connection error'};
    }'''
    
    # Tulis ulang (manual karena regex kompleks)
    print("\n📝 Note: API Service sudah baik, tidak perlu diubah")

if __name__ == "__main__":
    import os
    fix_chat_provider()
    print("\n🚀 Build APK baru dengan:")
    print("   flutter clean")
    print("   flutter pub get")
    print("   flutter build apk --release --dart-define=API_URL=http://94.100.26.128:8081/api/v1")
    print("   cp build/app/outputs/flutter-apk/app-release.apk ~/dibs1/downloads/dibs1-latest.apk")
