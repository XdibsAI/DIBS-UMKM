from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Optional
from auth.routes import get_current_user, TokenData
from config.logging import logger

router = APIRouter(prefix="/api/v1/toko", tags=["toko"])

db = None

def set_database(database):
    global db
    db = database

@router.get("/dashboard")
async def get_dashboard(current_user: TokenData = Depends(get_current_user)):
    try:
        import ast
        from datetime import datetime, timedelta, timezone
        from zoneinfo import ZoneInfo

        u_id = str(getattr(current_user, 'id', getattr(current_user, 'user_id', '0')))

        # Timezone fleksibel: ambil dari user jika ada, fallback Asia/Jakarta
        tz_name = getattr(current_user, 'timezone', None) or 'Asia/Jakarta'
        try:
            user_tz = ZoneInfo(tz_name)
        except Exception:
            tz_name = 'Asia/Jakarta'
            user_tz = ZoneInfo(tz_name)

        # Asumsi created_at di DB disimpan sebagai UTC naive ISO string
        now_utc = datetime.now(timezone.utc)
        now_local = now_utc.astimezone(user_tz)

        start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        end_local = start_local + timedelta(days=1)

        start_utc_str = start_local.astimezone(timezone.utc).replace(tzinfo=None).isoformat()
        end_utc_str = end_local.astimezone(timezone.utc).replace(tzinfo=None).isoformat()

        # Total Products
        res_products = await db.fetch_all(
            "SELECT COUNT(*) as total FROM toko_products WHERE user_id = ?",
            (u_id,)
        )
        total_products = res_products[0]['total'] if res_products else 0

        # Low Stock (sementara pakai threshold stock <= 10)
        res_low_stock = await db.fetch_all(
            "SELECT COUNT(*) as total FROM toko_products WHERE user_id = ? AND stock <= 10",
            (u_id,)
        )
        low_stock = res_low_stock[0]['total'] if res_low_stock else 0

        # Today Sales & Transactions berdasarkan timezone user
        res_today = await db.fetch_all(
            """
            SELECT
                COALESCE(SUM(total), 0) as total_sales,
                COUNT(*) as total_transactions
            FROM toko_sales
            WHERE user_id = ?
              AND created_at >= ?
              AND created_at < ?
            """,
            (u_id, start_utc_str, end_utc_str)
        )
        today_sales = res_today[0]['total_sales'] if res_today else 0
        today_transactions = res_today[0]['total_transactions'] if res_today else 0

        # Recent Sales
        sales_rows = await db.fetch_all(
            """
            SELECT id, total, items, created_at
            FROM toko_sales
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 5
            """,
            (u_id,)
        )

        recent_sales = []
        for row in sales_rows:
            sale = dict(row)
            items_raw = sale.get('items', '[]')
            parsed_items = []

            if isinstance(items_raw, str) and items_raw.strip():
                try:
                    parsed_items = ast.literal_eval(items_raw)
                except Exception:
                    parsed_items = []
            elif isinstance(items_raw, list):
                parsed_items = items_raw

            first_name = 'Produk'
            item_count = 0

            if isinstance(parsed_items, list) and parsed_items:
                first_item = parsed_items[0] or {}
                first_name = first_item.get('name') or 'Produk'
                item_count = len(parsed_items)

            if item_count > 1:
                product_name = f"{first_name} +{item_count - 1} item"
            else:
                product_name = first_name

            recent_sales.append({
                "id": sale.get("id"),
                "product_name": product_name,
                "total": sale.get("total", 0),
                "created_at": sale.get("created_at", ""),
                "items": parsed_items,
            })

        return {
            "status": "success",
            "data": {
                "today_sales": today_sales,
                "today_transactions": today_transactions,
                "total_products": total_products,
                "low_stock": low_stock,
                "recent_sales": recent_sales,
                "timezone": tz_name
            }
        }
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return {"status": "error", "message": str(e)}

@router.get("/products")
async def get_products(current_user: TokenData = Depends(get_current_user)):
    try:
        u_id = str(getattr(current_user, 'id', getattr(current_user, 'user_id', '0')))
        products = await db.fetch_all("SELECT * FROM toko_products WHERE user_id = ?", (u_id,))
        return {"status": "success", "data": [dict(p) for p in products]}
    except Exception as e:
        logger.error(f"Get products error: {e}")
        raise HTTPException(500, str(e))

@router.post("/products")
async def create_product(data: Dict, current_user: TokenData = Depends(get_current_user)):
    try:
        u_id = str(getattr(current_user, 'id', getattr(current_user, 'user_id', '0')))

        name = str(data.get('name', 'Produk Baru')).strip()
        price = float(data.get('price', 0.0))
        stock = int(data.get('stock', 0))
        category = str(data.get('category', 'Umum')).strip()
        description = str(data.get('description', '')).strip()
        barcode = str(data.get('barcode', '')).strip() or None

        if barcode:
            existing = await db.fetch_one(
                "SELECT id, name FROM toko_products WHERE user_id = ? AND barcode = ?",
                (u_id, barcode)
            )
            if existing:
                raise HTTPException(400, f"Barcode sudah dipakai oleh produk: {existing['name']}")

        query = "INSERT INTO toko_products (user_id, name, price, stock, category, description, barcode) VALUES (?, ?, ?, ?, ?, ?, ?)"
        values = (u_id, name, price, stock, category, description, barcode)

        await db.execute(query, values)
        return {"status": "success", "message": "Product created successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create product error: {e}")
        raise HTTPException(400, f"Error: {str(e)}")

@router.delete("/products/{product_id}")
async def delete_product(product_id: int, current_user: TokenData = Depends(get_current_user)):
    try:
        u_id = str(getattr(current_user, 'id', getattr(current_user, 'user_id', '0')))
        await db.execute("DELETE FROM toko_products WHERE id = ? AND user_id = ?", (product_id, u_id))
        return {"status": "success", "message": "Product deleted"}
    except Exception as e:
        raise HTTPException(500, str(e))


@router.put("/products/{product_id}")
async def update_product(product_id: int, data: Dict, current_user: TokenData = Depends(get_current_user)):
    try:
        u_id = str(getattr(current_user, 'id', getattr(current_user, 'user_id', '0')))

        existing = await db.fetch_one(
            "SELECT * FROM toko_products WHERE id = ? AND user_id = ?",
            (product_id, u_id)
        )
        if not existing:
            raise HTTPException(404, "Produk tidak ditemukan")

        name = str(data.get('name', existing['name'])).strip()
        price = float(data.get('price', existing['price']))
        stock = int(data.get('stock', existing['stock']))
        category = str(data.get('category', existing['category'] or 'Umum')).strip()
        description = str(data.get('description', existing['description'] or '')).strip()
        barcode = str(data.get('barcode', existing['barcode'] or '')).strip() or None

        if barcode:
            duplicate = await db.fetch_one(
                "SELECT id, name FROM toko_products WHERE user_id = ? AND barcode = ? AND id != ?",
                (u_id, barcode, product_id)
            )
            if duplicate:
                raise HTTPException(400, f"Barcode sudah dipakai oleh produk: {duplicate['name']}")

        await db.execute(
            """
            UPDATE toko_products
            SET name = ?, price = ?, stock = ?, category = ?, description = ?, barcode = ?
            WHERE id = ? AND user_id = ?
            """,
            (name, price, stock, category, description, barcode, product_id, u_id)
        )

        return {"status": "success", "message": "Product updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update product error: {e}")
        raise HTTPException(400, f"Error: {str(e)}")

@router.post("/sales")
async def create_sale(data: Dict, current_user: TokenData = Depends(get_current_user)):
    try:
        import uuid, json
        from datetime import datetime

        u_id = str(getattr(current_user, "id", getattr(current_user, "user_id", "0")))
        sale_id = str(uuid.uuid4())
        total = int(data.get("total", 0))
        items_raw = data.get("items", "[]")
        items_list = json.loads(items_raw) if isinstance(items_raw, str) else items_raw
        created_at = datetime.now().isoformat()

        if not items_list:
            raise HTTPException(400, "Keranjang kosong")

        # Validasi stok dulu sebelum simpan transaksi
        for item in items_list:
            p_id = item.get("id")
            qty = int(item.get("qty", item.get("quantity", 0)))

            if not p_id:
                raise HTTPException(400, "Produk pada transaksi tidak valid")

            if qty < 1:
                raise HTTPException(400, "Quantity produk minimal 1")

            product = await db.fetch_one(
                "SELECT id, name, stock FROM toko_products WHERE id = ? AND user_id = ?",
                (p_id, u_id)
            )

            if not product:
                raise HTTPException(404, f"Produk dengan id {p_id} tidak ditemukan")

            current_stock = int(product["stock"] or 0)
            if current_stock < qty:
                raise HTTPException(
                    400,
                    f"Stok tidak cukup untuk {product['name']}. Tersedia: {current_stock}, diminta: {qty}"
                )

        # Simpan transaksi setelah semua valid
        await db.execute(
            "INSERT INTO toko_sales (id, user_id, total, items, created_at) VALUES (?, ?, ?, ?, ?)",
            (sale_id, u_id, total, str(items_raw), created_at)
        )

        # Kurangi stok
        for item in items_list:
            p_id = item.get("id")
            qty = int(item.get("qty", item.get("quantity", 0)))

            await db.execute(
                "UPDATE toko_products SET stock = stock - ? WHERE id = ? AND user_id = ?",
                (qty, p_id, u_id)
            )

        return {"status": "success", "message": "Sale recorded & stock updated", "sale_id": sale_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sale Error: {e}")
        raise HTTPException(400, f"Gagal transaksi: {str(e)}")

@router.post("/sales/scan-barcode")
async def scan_barcode_for_sale(data: Dict, current_user: TokenData = Depends(get_current_user)):
    try:
        u_id = str(getattr(current_user, "id", getattr(current_user, "user_id", "0")))
        barcode = str(data.get("barcode", "")).strip()
        quantity = int(data.get("quantity", 1))

        if not barcode:
            raise HTTPException(400, "Barcode wajib diisi")

        if quantity < 1:
            raise HTTPException(400, "Quantity minimal 1")

        product = await db.fetch_one(
            "SELECT * FROM toko_products WHERE user_id = ? AND barcode = ?",
            (u_id, barcode)
        )

        if not product:
            raise HTTPException(404, "Produk dengan barcode tersebut tidak ditemukan")

        product_data = dict(product)
        stock = int(product_data.get("stock", 0))

        if stock < quantity:
            raise HTTPException(
                400,
                f"Stok tidak cukup. Tersedia: {stock}, diminta: {quantity}"
            )

        return {
            "status": "success",
            "matched": True,
            "message": f"Produk ditemukan: {product_data.get('name', 'Produk')}",
            "data": {
                "product": product_data,
                "quantity": quantity
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scan barcode sale error: {e}")
        raise HTTPException(400, f"Gagal scan barcode: {str(e)}")

@router.get("/payment-settings")
async def get_payment_settings(current_user: TokenData = Depends(get_current_user)):
    try:
        u_id = str(getattr(current_user, 'id', getattr(current_user, 'user_id', '0')))
        row = await db.fetch_one(
            "SELECT * FROM toko_payment_settings WHERE user_id = ?",
            (u_id,)
        )

        return {
            "status": "success",
            "data": dict(row) if row else {
                "user_id": u_id,
                "qris_image_url": None,
                "bank_name": "",
                "account_name": "",
                "account_number": ""
            }
        }
    except Exception as e:
        logger.error(f"Get payment settings error: {e}")
        raise HTTPException(500, str(e))


@router.post("/payment-settings")
async def save_payment_settings(data: Dict, current_user: TokenData = Depends(get_current_user)):
    try:
        from datetime import datetime

        u_id = str(getattr(current_user, 'id', getattr(current_user, 'user_id', '0')))
        qris_image_url = str(data.get('qris_image_url', '')).strip() or None
        bank_name = str(data.get('bank_name', '')).strip()
        account_name = str(data.get('account_name', '')).strip()
        account_number = str(data.get('account_number', '')).strip()
        updated_at = datetime.now().isoformat()

        existing = await db.fetch_one(
            "SELECT user_id FROM toko_payment_settings WHERE user_id = ?",
            (u_id,)
        )

        if existing:
            await db.execute(
                """
                UPDATE toko_payment_settings
                SET qris_image_url = ?, bank_name = ?, account_name = ?, account_number = ?, updated_at = ?
                WHERE user_id = ?
                """,
                (qris_image_url, bank_name, account_name, account_number, updated_at, u_id)
            )
        else:
            await db.execute(
                """
                INSERT INTO toko_payment_settings
                (user_id, qris_image_url, bank_name, account_name, account_number, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (u_id, qris_image_url, bank_name, account_name, account_number, updated_at)
            )

        return {"status": "success", "message": "Payment settings saved"}
    except Exception as e:
        logger.error(f"Save payment settings error: {e}")
        raise HTTPException(400, str(e))
