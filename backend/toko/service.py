"""Toko Service - Business Logic untuk Manajemen Toko"""
import json
import re
import logging
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import random
import string

from .database import TokoDatabase
from .models import SaleCreate, ProductCreate, ProductUpdate
from chat.core import ollama_ai  # Tambahkan import Ollama

logger = logging.getLogger('DIBS1.TOKO')

class TokoService:
    def __init__(self, db: TokoDatabase):
        self.db = db
        self.product_cache = {}  # Cache untuk produk

    # ========== UTILITY FUNCTIONS ==========
    def _generate_invoice_number(self) -> str:
        """Generate nomor invoice unik"""
        date_part = datetime.now().strftime("%Y%m%d")
        random_part = ''.join(random.choices(string.digits, k=4))
        return f"INV-{date_part}-{random_part}"

    def _calculate_profit(self, items: List[Dict], products: Dict[int, float]) -> float:
        """Hitung total keuntungan dari penjualan"""
        total_profit = 0
        for item in items:
            product_id = item.get('product_id')
            cost_price = products.get(product_id, 0)
            profit = (item['price'] - cost_price) * item['qty']
            total_profit += profit
        return total_profit

    # ========== PRODUCT MANAGEMENT ==========
    async def get_products(self, user_id: str, category: str = None) -> List[Dict]:
        """Get semua produk user"""
        rows = await self.db.get_products(user_id, category)
        return [dict(row) for row in rows] if rows else []

    async def get_product(self, user_id: str, product_id: int) -> Optional[Dict]:
        """Get produk by ID"""
        row = await self.db.get_product(user_id, product_id)
        return dict(row) if row else None

    async def create_product(self, user_id: str, data: ProductCreate) -> int:
        """Create produk baru"""
        product_id = await self.db.create_product(user_id, data.dict())
        
        # Update cache
        product = await self.get_product(user_id, product_id)
        if product:
            self.product_cache[f"{user_id}:{product_id}"] = product

        logger.info(f"✅ Product created: {data.name} (ID: {product_id})")
        return product_id

    async def update_product(self, user_id: str, product_id: int, data: ProductUpdate) -> bool:
        """Update produk"""
        # Filter out None values
        update_data = {k: v for k, v in data.dict().items() if v is not None}

        if not update_data:
            return False

        rows_affected = await self.db.update_product(user_id, product_id, update_data)

        if rows_affected > 0:
            # Update cache
            product = await self.get_product(user_id, product_id)
            if product:
                self.product_cache[f"{user_id}:{product_id}"] = product

            logger.info(f"✅ Product updated: ID {product_id}")
            return True

        return False

    async def delete_product(self, user_id: str, product_id: int) -> bool:
        """Soft delete produk"""
        rows_affected = await self.db.delete_product(user_id, product_id)

        if rows_affected > 0:
            # Remove from cache
            cache_key = f"{user_id}:{product_id}"
            if cache_key in self.product_cache:
                del self.product_cache[cache_key]

            logger.info(f"✅ Product deleted: ID {product_id}")
            return True

        return False

    # ========== SALES MANAGEMENT ==========
    async def create_sale(self, user_id: str, data: SaleCreate) -> Dict[str, Any]:
        """Create transaksi penjualan baru"""
        # Hitung subtotal dan profit
        subtotal = 0
        items_data = []
        product_prices = {}  # Untuk hitung profit

        for item in data.items:
            # Get product details
            product = await self.get_product(user_id, item.product_id)
            if not product:
                raise ValueError(f"Product ID {item.product_id} not found")

            # Check stock
            if product['stock'] < item.qty:
                raise ValueError(f"Insufficient stock for {product['name']}. Available: {product['stock']}")

            item_dict = item.dict()
            items_data.append(item_dict)
            subtotal += item.subtotal

            # Store cost price for profit calculation
            product_prices[item.product_id] = product.get('cost_price', 0)

        # Calculate totals
        discount = data.discount
        tax = data.tax
        total = subtotal - discount + tax
        profit = self._calculate_profit(items_data, product_prices)

        # Create sale record
        sale_data = {
            'invoice_number': self._generate_invoice_number(),
            'items': json.dumps(items_data, default=str),
            'subtotal': subtotal,
            'discount': discount,
            'tax': tax,
            'total': total,
            'profit': profit,
            'payment_method': data.payment_method,
            'customer_name': data.customer_name,
            'customer_phone': data.customer_phone,
            'notes': data.notes,
            'status': 'completed'
        }

        sale_id = await self.db.create_sale(user_id, sale_data)

        logger.info(f"✅ Sale created: {sale_data['invoice_number']} - Total: Rp {total:,.0f}")

        return {
            'id': sale_id,
            'invoice_number': sale_data['invoice_number'],
            'items': items_data,
            'subtotal': subtotal,
            'discount': discount,
            'tax': tax,
            'total': total,
            'profit': profit,
            'payment_method': data.payment_method
        }

    async def get_sales(self, user_id: str, limit: int = 50) -> List[Dict]:
        """Get riwayat penjualan"""
        rows = await self.db.get_sales(user_id, limit)
        sales = []

        for row in rows:
            sale = dict(row)
            # Parse items JSON
            if sale['items']:
                sale['items'] = json.loads(sale['items'])
            sales.append(sale)

        return sales

    async def get_daily_summary(self, user_id: str, target_date: date = None) -> Dict:
        """Get ringkasan harian"""
        if target_date is None:
            target_date = date.today()

        date_str = target_date.strftime("%Y-%m-%d")
        summary = await self.db.get_daily_summary(user_id, date_str)

        return {
            'date': date_str,
            'transaction_count': summary['transaction_count'],
            'total_sales': summary['total_sales'],
            'total_profit': summary['total_profit'],
            'average_transaction': summary['total_sales'] / summary['transaction_count']
                                   if summary['transaction_count'] > 0 else 0
        }

    # ========== INVENTORY MANAGEMENT ==========
    async def get_low_stock_products(self, user_id: str) -> List[Dict]:
        """Get produk dengan stok rendah"""
        rows = await self.db.get_low_stock_products(user_id)
        return [dict(row) for row in rows] if rows else []

    async def adjust_stock(self, user_id: str, product_id: int,
                           change: int, reason: str) -> Optional[int]:
        """Adjust stok manual"""
        new_stock = await self.db.adjust_stock(user_id, product_id, change, reason)

        if new_stock is not None:
            logger.info(f"✅ Stock adjusted: Product {product_id} -> {new_stock} ({reason})")

            # Update cache
            product = await self.get_product(user_id, product_id)
            if product:
                self.product_cache[f"{user_id}:{product_id}"] = product

        return new_stock

    # ========== VOICE SCAN DENGAN AI ==========
    async def scan_voice_text(self, user_id: str, text: str) -> Dict[str, Any]:
        """Parse voice/text input menjadi transaksi menggunakan AI"""
        
        # Coba pakai AI dulu
        try:
            # Prompt khusus untuk ekstraksi dengan AI
            prompt = f"""
            Dari teks berikut: "{text}"
            
            Ekstrak daftar belanja dalam format JSON:
            [
                {{
                    "name": "nama barang persis",
                    "qty": jumlah (angka),
                    "price": harga per unit (angka, tanpa Rp)
                }}
            ]
            
            Contoh: 
            - "beli rokok 1 20000" -> [{{"name": "rokok", "qty": 1, "price": 20000}}]
            - "vpants size M 1" -> [{{"name": "vpants size M", "qty": 1, "price": 0}}]
            
            Jika harga tidak disebutkan, gunakan price: 0.
            Hanya output JSON, tanpa teks lain.
            """
            
            response = await ollama_ai.generate(prompt)
            logger.debug(f"AI response: {response}")
            
            # Bersihkan response (ambil JSON saja)
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                items = json.loads(json_match.group())
                
                # Validasi format
                total = 0
                found_items = []
                not_found = []
                
                # Ambil semua produk user untuk pencarian
                products = await self.get_products(user_id)
                
                for item in items:
                    if 'name' not in item:
                        continue
                        
                    item_name = item['name'].lower()
                    qty = item.get('qty', 1)
                    price = item.get('price', 0)
                    
                    # Cari produk di database dengan berbagai metode
                    found_product = None
                    
                    # 1. Exact match
                    for p in products:
                        if item_name == p['name'].lower():
                            found_product = p
                            break
                    
                    # 2. Partial match dengan prioritas panjang nama
                    if not found_product:
                        # Urutkan berdasarkan panjang nama (descending) agar yang lebih spesifik didahulukan
                        sorted_products = sorted(products, key=lambda x: len(x['name']), reverse=True)
                        for p in sorted_products:
                            if item_name in p['name'].lower() or p['name'].lower() in item_name:
                                found_product = p
                                break
                    
                    if found_product:
                        # Gunakan harga dari database jika price 0
                        final_price = price if price > 0 else found_product['price']
                        subtotal = qty * final_price
                        
                        found_items.append({
                            'product_id': found_product['id'],
                            'name': found_product['name'],
                            'qty': qty,
                            'price': final_price,
                            'subtotal': subtotal
                        })
                        total += subtotal
                    else:
                        not_found.append(item['name'])
                
                # Buat preview
                preview = "📋 **RINCIAN BELANJA**\n"
                preview += "=" * 30 + "\n"
                
                for item in found_items:
                    preview += f"• {item['name']}: {item['qty']} x Rp {item['price']:,.0f} = Rp {item['subtotal']:,.0f}\n"
                
                preview += "=" * 30 + "\n"
                preview += f"💰 **TOTAL: Rp {total:,.0f}**\n"
                
                if not_found:
                    preview += f"\n⚠️ Produk tidak ditemukan: {', '.join(not_found)}\n"
                
                return {
                    'items': found_items,
                    'total': total,
                    'preview': preview,
                    'not_found': not_found
                }
                
        except Exception as e:
            logger.error(f"AI parsing error: {e}")
            # Fallback ke regex jika AI gagal
            return await self._scan_with_regex(user_id, text)
    
    async def _scan_with_regex(self, user_id: str, text: str) -> Dict[str, Any]:
        """Fallback: parse dengan regex"""
        pattern = r'([a-zA-Z\s]+?)\s*(\d+)?\s*(?:rb|ribu|k)?\s*(\d+)?'

        items = []
        total = 0
        not_found = []

        # Split by comma, 'dan', or '&'
        parts = re.split(r'[,|dan|&]', text.lower())

        for part in parts:
            match = re.search(r'([a-zA-Z\s]+?)\s*(\d+)?\s*(?:rb|ribu|k)?\s*(\d+)?', part.strip())
            if match:
                name = match.group(1).strip()
                qty = int(match.group(2)) if match.group(2) else 1
                price_input = match.group(3)

                # Cari produk di database
                products = await self.get_products(user_id)
                found_product = None

                # Urutkan berdasarkan panjang nama (descending)
                sorted_products = sorted(products, key=lambda x: len(x['name']), reverse=True)
                
                for p in sorted_products:
                    # Cocokkan nama persis atau mengandung kata kunci
                    if name.lower() in p["name"].lower() or p["name"].lower() in name.lower():
                        found_product = p
                        break

                if found_product:
                    # Gunakan harga dari database
                    price = found_product['price']
                    subtotal = qty * price

                    items.append({
                        'product_id': found_product['id'],
                        'name': found_product['name'],
                        'qty': qty,
                        'price': price,
                        'subtotal': subtotal
                    })
                    total += subtotal
                else:
                    # Produk tidak ditemukan
                    not_found.append(name)

        # Buat preview
        preview = "📋 **RINCIAN BELANJA**\n"
        preview += "=" * 30 + "\n"

        for item in items:
            preview += f"• {item['name']}: {item['qty']} x Rp {item['price']:,.0f} = Rp {item['subtotal']:,.0f}\n"

        preview += "=" * 30 + "\n"
        preview += f"💰 **TOTAL: Rp {total:,.0f}**\n"

        if not_found:
            preview += f"\n⚠️ Produk tidak ditemukan: {', '.join(not_found)}\n"

        return {
            'items': items,
            'total': total,
            'preview': preview,
            'not_found': not_found
        }

    # ========== DASHBOARD SUMMARY ==========
    async def get_dashboard_summary(self, user_id: str) -> Dict:
        """Get summary untuk dashboard"""
        # Total produk
        products = await self.get_products(user_id)
        active_products = [p for p in products if p.get('is_active', 1) == 1]

        # Low stock
        low_stock = await self.get_low_stock_products(user_id)

        # Today's sales
        today_summary = await self.get_daily_summary(user_id)

        # Total stock value
        total_stock_value = sum(p['stock'] * p['price'] for p in products if p.get('is_active', 1))
        total_investment = sum(p['stock'] * p.get('cost_price', 0) for p in products if p.get('is_active', 1))

        return {
            'products': {
                'total': len(products),
                'active': len(active_products),
                'low_stock': len(low_stock)
            },
            'inventory': {
                'total_value': total_stock_value,
                'total_investment': total_investment,
                'potential_profit': total_stock_value - total_investment
            },
            'sales_today': today_summary,
            'alerts': {
                'low_stock': [dict(p) for p in low_stock[:5]]  # Top 5 low stock
            }
        }
