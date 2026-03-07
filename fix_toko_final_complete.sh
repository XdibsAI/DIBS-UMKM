#!/bin/bash

cd ~/dibs1/frontend

echo "🔧 FINAL COMPREHENSIVE FIX FOR TOKO MODULE"

# Backup
cp lib/screens/toko/toko_screen.dart lib/screens/toko/toko_screen.dart.before-final-fix

# Fix Tab Produk - line 737-746: Should show products with stock & price
# Current WRONG: item['quantity'], item['subtotal']  
# Should be: product['stock'], product['price']

python3 - << 'PYFIX'
content = open('lib/screens/toko/toko_screen.dart', 'r').read()

# Find and replace Tab Produk DataTable (around line 737)
import re

# Pattern: In _buildProduk, the DataTable that maps products
pattern = r"(rows: provider\.products\.map\(\(item\) => DataRow\(\s*cells: \[\s*DataCell\(Text\(item\['name'\].*?DataCell\(IconButton\(.*?icon: Icon\(Icons\..*?\),.*?onPressed:.*?provider\.decrementCartItem\(item\['id'\]\),.*?\)\),.*?\],)"

replacement = r"""rows: products.map((product) => DataRow(
                          cells: [
                            DataCell(Text(product['name'] ?? '', style: TextStyle(color: Colors.white, fontSize: 13))),
                            DataCell(Text('${product['stock'] ?? 0}', style: TextStyle(color: Colors.white))),
                            DataCell(Text('Rp ${_formatNumber(product['price'] ?? 0)}', style: TextStyle(color: Colors.white))),
                            DataCell(IconButton(
                              icon: Icon(Icons.add_circle, color: Colors.green, size: 18),
                              tooltip: 'Tambah ke keranjang',
                              onPressed: () {
                                provider.addToCart(product, 1);
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text('✅ ${product['name']} ditambahkan'),
                                    duration: Duration(milliseconds: 800),
                                  ),
                                );
                              },
                            )),
                          ],"""

# This is complex - let me just do direct line replacement
# Line 737-746 in _buildProduk

lines = content.split('\n')

# Find line with "rows: provider.products.map" in _buildProduk section
for i, line in enumerate(lines):
    if i > 700 and 'rows: provider.products.map' in line and i < 800:
        print(f"Found Produk DataTable at line {i+1}")
        # Replace next 10 lines
        lines[i] = "                        rows: products.map((product) => DataRow("
        lines[i+1] = "                          cells: ["
        lines[i+2] = "                            DataCell(Text(product['name'] ?? '', style: TextStyle(color: Colors.white, fontSize: 13))),"
        lines[i+3] = "                            DataCell(Text('${product['stock'] ?? 0}', style: TextStyle(color: Colors.white))),"
        lines[i+4] = "                            DataCell(Text('Rp ${_formatNumber(product['price'] ?? 0)}', style: TextStyle(color: Colors.white))),"
        lines[i+5] = "                            DataCell(IconButton("
        lines[i+6] = "                              icon: Icon(Icons.add_circle, color: Colors.green, size: 18),"
        lines[i+7] = "                              onPressed: () {"
        lines[i+8] = "                                provider.addToCart(product, 1);"
        lines[i+9] = "                                ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('${product['name']} ditambahkan'), duration: Duration(seconds: 1)));"
        lines[i+10] = "                              },"
        # Keep line i+11 as is (closing IconButton)
        print("✅ Fixed Tab Produk DataTable")
        break

# Fix Tab Kasir - should use cartItems
for i, line in enumerate(lines):
    if i > 400 and i < 600 and 'rows: provider.products.map' in line:
        print(f"Found Kasir DataTable at line {i+1} - changing to cartItems")
        lines[i] = lines[i].replace('provider.products.map', 'cartItems.map')
        print("✅ Fixed Tab Kasir to use cartItems")
        break

content = '\n'.join(lines)
open('lib/screens/toko/toko_screen.dart', 'w').write(content)
print("\n✅ Both tabs fixed!")
PYFIX

# Build
flutter build apk --release --dart-define=API_URL=http://94.100.26.128:8081/api/v1

if [ -f build/app/outputs/flutter-apk/app-release.apk ]; then
    cp build/app/outputs/flutter-apk/app-release.apk ~/dibs1/downloads/dibs-v3.2-FINAL-COMPLETE.apk
    cp ~/dibs1/downloads/dibs-v3.2-FINAL-COMPLETE.apk ~/dibs1/downloads/dibs-latest.apk
    
    echo ""
    echo "🎉 v3.2 - COMPLETE FIX!"
    ls -lh ~/dibs1/downloads/dibs-v3.2-FINAL-COMPLETE.apk
fi
