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

        name = str(data.get('name', 'Produk Baru'))
        price = float(data.get('price', 0.0))
        stock = int(data.get('stock', 0))
        category = str(data.get('category', 'Umum'))
        description = str(data.get('description', ''))

        print(f"DEBUG: u_id={type(u_id)} value={u_id}")
        print(f"DEBUG: name={type(name)} value={name}")
        print(f"DEBUG: price={type(price)} value={price}")
        print(f"DEBUG: stock={type(stock)} value={stock}")

        query = "INSERT INTO toko_products (user_id, name, price, stock, category, description) VALUES (?, ?, ?, ?, ?, ?)"
        values = (u_id, name, price, stock, category, description)

        await db.execute(query, values)
        return {"status": "success", "message": "Product created successfully"}
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

        await db.execute(
            "INSERT INTO toko_sales (id, user_id, total, items, created_at) VALUES (?, ?, ?, ?, ?)",
            (sale_id, u_id, total, str(items_raw), created_at)
        )

        for item in items_list:
            p_id = item.get("id")
            qty = int(item.get("qty", item.get("quantity", 0)))
            if p_id:
                await db.execute(
                    "UPDATE toko_products SET stock = stock - ? WHERE id = ? AND user_id = ?",
                    (qty, p_id, u_id)
                )

        return {"status": "success", "message": "Sale recorded & stock updated", "sale_id": sale_id}
    except Exception as e:
        logger.error(f"Sale Error: {e}")
        raise HTTPException(400, f"Gagal transaksi: {str(e)}")
