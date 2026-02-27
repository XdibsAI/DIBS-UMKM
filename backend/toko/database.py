"""Database Manager untuk Toko - Koneksi terpisah dari database user"""
import aiosqlite
import logging
from pathlib import Path

logger = logging.getLogger('DIBS1.TOKO')

class TokoDatabase:
    def __init__(self, db_path: str = "toko.db"):
        self.db_path = db_path
        self.db = None

    async def connect(self):
        """Connect ke database toko"""
        self.db = await aiosqlite.connect(self.db_path)
        self.db.row_factory = aiosqlite.Row
        logger.info(f"✅ Database Toko connected: {self.db_path}")
        return self.db

    async def close(self):
        """Close database connection"""
        if self.db:
            await self.db.close()
            logger.info("👋 Database Toko closed")

    async def init_db(self):
        """Inisialisasi tabel dari schema.sql (CREATE IF NOT EXISTS)"""
        if not self.db:
            await self.connect()
        
        # Baca file schema.sql
        schema_path = Path(__file__).parent / "schema.sql"
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema = f.read()
            
            # Execute schema - pakai executescript untuk multiple statements
            try:
                await self.db.executescript(schema)
                await self.db.commit()
                logger.info("✅ Database Toko schema initialized")
            except aiosqlite.OperationalError as e:
                if "already exists" in str(e):
                    logger.info("ℹ️ Database schema already exists, skipping...")
                else:
                    raise e
        else:
            logger.error(f"❌ Schema file not found: {schema_path}")

    async def execute(self, query: str, params: tuple = ()):
        """Execute query dengan parameter"""
        async with self.db.execute(query, params) as cursor:
            await self.db.commit()
            return cursor

    async def fetch_one(self, query: str, params: tuple = ()):
        """Fetch satu row"""
        async with self.db.execute(query, params) as cursor:
            return await cursor.fetchone()

    async def fetch_all(self, query: str, params: tuple = ()):
        """Fetch semua rows"""
        async with self.db.execute(query, params) as cursor:
            return await cursor.fetchall()

    async def execute_many(self, query: str, params_list: list):
        """Execute many queries (for batch insert)"""
        async with self.db.executemany(query, params_list) as cursor:
            await self.db.commit()
            return cursor

    async def get_products(self, user_id: int, category: str = None, active_only: bool = True):
        """Get semua produk milik user"""
        query = "SELECT * FROM products WHERE user_id = ?"
        params = [user_id]
        
        if active_only:
            query += " AND is_active = 1"
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY name"
        
        return await self.fetch_all(query, tuple(params))

    async def get_product(self, user_id: int, product_id: int):
        """Get produk by ID"""
        return await self.fetch_one(
            "SELECT * FROM products WHERE user_id = ? AND id = ?",
            (user_id, product_id)
        )

    async def get_product_by_barcode(self, user_id: int, barcode: str):
        """Get produk by barcode"""
        return await self.fetch_one(
            "SELECT * FROM products WHERE user_id = ? AND barcode = ?",
            (user_id, barcode)
        )

    async def create_product(self, user_id: int, data: dict):
        """Create produk baru"""
        query = """
            INSERT INTO products (
                user_id, name, description, price, cost_price, stock,
                category, barcode, sku, min_stock, image_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            user_id,
            data.get('name'),
            data.get('description'),
            data.get('price', 0),
            data.get('cost_price', 0),
            data.get('stock', 0),
            data.get('category'),
            data.get('barcode'),
            data.get('sku'),
            data.get('min_stock', 0),
            data.get('image_url')
        )
        
        cursor = await self.execute(query, params)
        return cursor.lastrowid

    async def update_product(self, user_id: int, product_id: int, data: dict):
        """Update produk"""
        fields = []
        values = []
        
        for key, value in data.items():
            if key in ['name', 'description', 'price', 'cost_price', 'stock',
                      'category', 'barcode', 'sku', 'min_stock', 'image_url', 'is_active']:
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return 0
        
        values.append(user_id)
        values.append(product_id)
        
        query = f"UPDATE products SET {', '.join(fields)} WHERE user_id = ? AND id = ?"
        cursor = await self.execute(query, tuple(values))
        return cursor.rowcount

    async def delete_product(self, user_id: int, product_id: int):
        """Soft delete produk (set is_active = 0)"""
        cursor = await self.execute(
            "UPDATE products SET is_active = 0 WHERE user_id = ? AND id = ?",
            (user_id, product_id)
        )
        return cursor.rowcount

    async def create_sale(self, user_id: int, data: dict):
        """Create transaksi penjualan"""
        query = """
            INSERT INTO sales (
                user_id, invoice_number, items, subtotal, discount, tax,
                total, profit, payment_method, customer_name, customer_phone,
                notes, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            user_id,
            data.get('invoice_number'),
            data.get('items'),  # JSON string
            data.get('subtotal', 0),
            data.get('discount', 0),
            data.get('tax', 0),
            data.get('total', 0),
            data.get('profit', 0),
            data.get('payment_method', 'cash'),
            data.get('customer_name'),
            data.get('customer_phone'),
            data.get('notes'),
            data.get('status', 'completed')
        )
        
        cursor = await self.execute(query, params)
        return cursor.lastrowid

    async def get_sales(self, user_id: int, limit: int = 50):
        """Get riwayat penjualan"""
        return await self.fetch_all(
            """SELECT * FROM sales 
               WHERE user_id = ? 
               ORDER BY created_at DESC 
               LIMIT ?""",
            (user_id, limit)
        )

    async def get_daily_summary(self, user_id: int, date: str):
        """Get ringkasan penjualan harian"""
        cursor = await self.fetch_one("""
            SELECT 
                COUNT(*) as transaction_count,
                SUM(total) as total_sales,
                SUM(profit) as total_profit
            FROM sales 
            WHERE user_id = ? AND DATE(created_at) = ?
        """, (user_id, date))
        
        return dict(cursor) if cursor else {
            'transaction_count': 0,
            'total_sales': 0,
            'total_profit': 0
        }

    async def get_low_stock_products(self, user_id: int):
        """Get produk dengan stok di bawah minimal"""
        return await self.fetch_all(
            """SELECT * FROM products 
               WHERE user_id = ? AND is_active = 1 
               AND stock <= min_stock AND min_stock > 0
               ORDER BY stock ASC""",
            (user_id,)
        )

    async def adjust_stock(self, user_id: int, product_id: int, 
                          change: int, reason: str, reference_type: str = None, 
                          reference_id: int = None):
        """Adjust stok manual"""
        # Get current stock
        product = await self.get_product(user_id, product_id)
        if not product:
            return None
        
        current_stock = product['stock']
        new_stock = current_stock + change
        
        # Update product stock
        await self.execute(
            "UPDATE products SET stock = ? WHERE id = ?",
            (new_stock, product_id)
        )
        
        # Log the change
        await self.execute("""
            INSERT INTO inventory_log 
            (user_id, product_id, change, previous_stock, new_stock, 
             reference_type, reference_id, reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, product_id, change, current_stock, new_stock,
            reference_type, reference_id, reason
        ))
        
        return new_stock
