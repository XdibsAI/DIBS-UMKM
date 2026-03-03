#!/usr/bin/env python3
"""
Debug menu toko blank putih - cek error di log dan struktur widget
"""
import subprocess
import re

def check_flutter_log():
    """Cek log Flutter untuk error"""
    print("🔍 CEK ERROR DI FLUTTER LOG")
    print("="*50)
    
    # Simulasi run dengan debug mode (tidak benar2 dijalankan)
    print("📱 Untuk melihat error realtime, jalankan:")
    print("   flutter run --dart-define=API_URL=http://94.100.26.128:8081/api/v1")
    print("\n   Lalu buka menu Toko, lihat console untuk error\n")

def check_toko_screen_structure():
    """Cek struktur toko_screen.dart"""
    print("\n🔍 CEK STRUKTUR TOKO_SCREEN.DART")
    print("="*50)
    
    with open('lib/screens/toko/toko_screen.dart', 'r') as f:
        content = f.read()
    
    # Cek apakah build method lengkap
    if 'return Scaffold' in content:
        print("✅ Scaffold ditemukan")
    else:
        print("❌ Scaffold tidak ditemukan")
    
    if 'appBar: AppBar' in content:
        print("✅ AppBar ditemukan")
    else:
        print("❌ AppBar tidak ditemukan")
    
    if 'bottom: const TabBar' in content:
        print("✅ TabBar di AppBar.bottom ditemukan")
    else:
        print("❌ TabBar tidak ditemukan")
    
    if 'TabBarView' in content:
        print("✅ TabBarView ditemukan")
    else:
        print("❌ TabBarView tidak ditemukan")
    
    # Cek fungsi-fungsi tab
    tabs = ['_buildDashboard', '_buildKasir', '_buildProduk']
    for tab in tabs:
        if tab in content:
            print(f"✅ {tab} ditemukan")
        else:
            print(f"❌ {tab} TIDAK ditemukan - INI MASALAH!")

def check_toko_provider():
    """Cek apakah provider terdaftar"""
    print("\n🔍 CEK TOKO PROVIDER")
    print("="*50)
    
    with open('lib/main.dart', 'r') as f:
        main_content = f.read()
    
    if 'ChangeNotifierProvider(create: (_) => TokoProvider()' in main_content:
        print("✅ TokoProvider terdaftar di main.dart")
    else:
        print("❌ TokoProvider TIDAK terdaftar di main.dart")

def check_common_errors():
    """Cek error umum"""
    print("\n🔍 CEK ERROR UMUM")
    print("="*50)
    
    # Cek apakah ada parameter yang salah
    with open('lib/screens/toko/toko_screen.dart', 'r') as f:
        content = f.read()
    
    if 'Scaffold(' in content and 'body:' in content:
        print("✅ Struktur Scaffold OK")
    else:
        print("❌ Struktur Scaffold bermasalah")
    
    # Rekomendasi
    print("\n💡 REKOMENDASI:")
    print("1. Jalankan dengan debug mode:")
    print("   flutter run --dart-define=API_URL=http://94.100.26.128:8081/api/v1")
    print("\n2. Lihat error di console, biasanya ada NullPointer atau Provider error")
    print("\n3. Coba clear cache dan rebuild ulang:")
    print("   flutter clean")
    print("   flutter pub cache repair")
    print("   flutter pub get")
    print("   flutter build apk --release --dart-define=API_URL=http://94.100.26.128:8081/api/v1")

if __name__ == "__main__":
    check_flutter_log()
    check_toko_screen_structure()
    check_toko_provider()
    check_common_errors()
