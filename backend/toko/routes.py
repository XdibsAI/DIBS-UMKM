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
        u_id = str(getattr(current_user, 'id', getattr(current_user, 'user_id', '0')))
        
        # Total Products
        res = await db.fetch_all("SELECT COUNT(*) as total FROM toko_products WHERE user_id = ?", (u_id,))
        total_products = res[0]['total'] if res else 0
        
        # Today Sales (Placeholder logic)
        res_sales = await db.fetch_all("SELECT SUM(total) as total FROM toko_sales WHERE user_id = ? AND date(created_at) = date('now')", (u_id,))
        today_sales = res_sales[0]['total'] if res_sales and res_sales[0]['total'] else 0
        
        return {
            "status": "success",
            "data": {
                "today_sales": today_sales,
                "today_transactions": 0,
                "total_products": total_products,
                "low_stock": 0
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
        
        # Explicit Casting to prevent Database Mismatch
        name = str(data.get('name', 'Produk Baru'))
        price = float(data.get('price', 0.0))
        stock = int(data.get('stock', 0))
        category = str(data.get('category', 'Umum'))
        description = str(data.get('description', ''))

        
        # DEBUG TIPE DATA
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

        # 1. Simpan Penjualan
        await db.execute("INSERT INTO toko_sales (id, user_id, total, items, created_at) VALUES (?, ?, ?, ?, ?)", 
                         (sale_id, u_id, total, str(items_raw), created_at))

        # 2. Update Stok (Looping items)
        for item in items_list:
            p_id = item.get("id")
            qty = int(item.get("qty", 0))
            if p_id:
                await db.execute("UPDATE toko_products SET stock = stock - ? WHERE id = ? AND user_id = ?", (qty, p_id, u_id))

        return {"status": "success", "message": "Sale recorded & stock updated", "sale_id": sale_id}
    except Exception as e:
        logger.error(f"Sale Error: {e}")
        raise HTTPException(400, f"Gagal transaksi: {str(e)}")
