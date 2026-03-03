#!/usr/bin/env python3
"""
Update main.dart - Tambah route untuk InclusiveCheckoutScreen
"""
import re

def update_main():
    with open('lib/main.dart', 'r') as f:
        content = f.read()
    
    # 1. TAMBAH IMPORT di bagian atas
    import_pattern = r"(import 'screens/toko/toko_screen.dart';)"
    new_import = "import 'screens/toko/toko_screen.dart';\nimport 'widgets/toko/inclusive_checkout.dart';"
    content = content.replace(import_pattern, new_import)
    
    # 2. TAMBAH ROUTE di bagian routes
    routes_pattern = r"(routes: \{[^\}]*\})"
    
    new_routes = '''routes: {
        '/': (context) => const AppStartup(),
        '/home': (context) => HomeScreen(),
        '/login': (context) => LoginScreen(),
        '/register': (context) => RegisterScreen(),
        '/inclusive-checkout': (context) => const InclusiveCheckoutScreen(),
      }'''
    
    content = re.sub(routes_pattern, new_routes, content, flags=re.DOTALL)
    
    with open('lib/main.dart', 'w') as f:
        f.write(content)
    
    print("✅ main.dart updated!")
    print("   - Added import for inclusive_checkout.dart")
    print("   - Added route '/inclusive-checkout'")

def verify():
    print("\n🔍 VERIFIKASI:")
    with open('lib/main.dart', 'r') as f:
        content = f.read()
    
    if 'inclusive_checkout.dart' in content:
        print("✅ Import added")
    else:
        print("❌ Import missing")
    
    if "'/inclusive-checkout'" in content:
        print("✅ Route added")
    else:
        print("❌ Route missing")

if __name__ == "__main__":
    update_main()
    verify()
