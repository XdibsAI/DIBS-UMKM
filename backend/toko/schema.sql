-- Database Toko untuk DIBS - Terpisah dari database user

-- Tabel produk
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL DEFAULT 0,
    cost_price REAL DEFAULT 0,
    stock INTEGER DEFAULT 0,
    category TEXT,
    barcode TEXT,
    sku TEXT,
    min_stock INTEGER DEFAULT 0,
    image_url TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, barcode),
    UNIQUE(user_id, sku)
);

-- Tabel transaksi penjualan
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    invoice_number TEXT UNIQUE,
    items TEXT NOT NULL,
    subtotal REAL NOT NULL,
    discount REAL DEFAULT 0,
    tax REAL DEFAULT 0,
    total REAL NOT NULL,
    profit REAL DEFAULT 0,
    payment_method TEXT DEFAULT 'cash',
    customer_name TEXT,
    customer_phone TEXT,
    notes TEXT,
    status TEXT DEFAULT 'completed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel pembelian stok
CREATE TABLE IF NOT EXISTS purchases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    supplier_name TEXT,
    items TEXT NOT NULL,
    subtotal REAL NOT NULL,
    total REAL NOT NULL,
    payment_status TEXT DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabel log inventaris
CREATE TABLE IF NOT EXISTS inventory_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    product_id INTEGER NOT NULL,
    change INTEGER NOT NULL,
    previous_stock INTEGER NOT NULL,
    new_stock INTEGER NOT NULL,
    reference_type TEXT,
    reference_id INTEGER,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Tabel kategori
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    parent_id INTEGER DEFAULT NULL,
    UNIQUE(user_id, name)
);

-- Tabel supplier
CREATE TABLE IF NOT EXISTS suppliers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    contact_person TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index untuk performa
CREATE INDEX idx_products_user_id ON products(user_id);
CREATE INDEX idx_products_barcode ON products(barcode);
CREATE INDEX idx_sales_user_id ON sales(user_id);
CREATE INDEX idx_sales_created_at ON sales(created_at);
CREATE INDEX idx_inventory_log_product ON inventory_log(product_id);
CREATE INDEX idx_inventory_log_created_at ON inventory_log(created_at);

-- Trigger untuk update timestamp
CREATE TRIGGER IF NOT EXISTS update_products_timestamp 
AFTER UPDATE ON products
BEGIN
    UPDATE products SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Trigger untuk log sale
CREATE TRIGGER IF NOT EXISTS log_sale_inventory
AFTER INSERT ON sales
BEGIN
    INSERT INTO inventory_log (user_id, product_id, change, previous_stock, new_stock, reference_type, reference_id, reason)
    SELECT 
        NEW.user_id,
        json_extract(value, '$.product_id'),
        -json_extract(value, '$.qty'),
        (SELECT stock FROM products WHERE id = json_extract(value, '$.product_id')),
        (SELECT stock - json_extract(value, '$.qty') FROM products WHERE id = json_extract(value, '$.product_id')),
        'sale',
        NEW.id,
        'Penjualan'
    FROM json_each(NEW.items);
    
    UPDATE products SET stock = stock - json_extract(value, '$.qty')
    FROM json_each(NEW.items)
    WHERE products.id = json_extract(value, '$.product_id');
END;

-- Trigger untuk log purchase
CREATE TRIGGER IF NOT EXISTS log_purchase_inventory
AFTER INSERT ON purchases
BEGIN
    INSERT INTO inventory_log (user_id, product_id, change, previous_stock, new_stock, reference_type, reference_id, reason)
    SELECT 
        NEW.user_id,
        json_extract(value, '$.product_id'),
        json_extract(value, '$.qty'),
        (SELECT stock FROM products WHERE id = json_extract(value, '$.product_id')),
        (SELECT stock + json_extract(value, '$.qty') FROM products WHERE id = json_extract(value, '$.product_id')),
        'purchase',
        NEW.id,
        'Pembelian stok'
    FROM json_each(NEW.items);
    
    UPDATE products SET stock = stock + json_extract(value, '$.qty')
    FROM json_each(NEW.items)
    WHERE products.id = json_extract(value, '$.product_id');
END;
