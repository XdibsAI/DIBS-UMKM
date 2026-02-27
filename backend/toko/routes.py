"""Toko & Kasir Routes"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
import logging
import re
from typing import List, Dict

from auth.utils import get_current_user, TokenData

router = APIRouter(prefix="/api/v1/toko", tags=["Toko"])
logger = logging.getLogger('DIBS1')

# Database will be injected
db = None

def set_database(database):
    global db
    db = database

# ============ DASHBOARD ============

@router.get("/dashboard")
async def get_dashboard(current_user: TokenData = Depends(get_current_user)):
    """Get toko dashboard summary"""
    try:
        today = datetime.now().date()
        
        # Today's sales
        today_sales = await db.fetch_all(
            "SELECT * FROM toko_sales WHERE user_id = ? AND DATE(created_at) = ?",
            (current_user.user_id, today.isoformat())
        )
        
        total_today = sum(sale['total'] for sale in today_sales)
        
        # Total products
        products = await db.fetch_all(
            "SELECT * FROM toko_products WHERE user_id = ?",
            (current_user.user_id,)
        )
        
        # Low stock products
        low_stock = [p for p in products if p['stock'] < 10]
        
        return {
            "status": "success",
            "data": {
                "today_sales": total_today,
                "today_transactions": len(today_sales),
                "total_products": len(products),
                "low_stock": len(low_stock),
            }
        }
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        raise HTTPException(500, str(e))

# ============ PRODUCTS ============

@router.get("/products")
async def get_products(
    category: str = None,
    current_user: TokenData = Depends(get_current_user)
):
    """Get all products"""
    try:
        if category:
            products = await db.fetch_all(
                "SELECT * FROM toko_products WHERE user_id = ? AND category = ? ORDER BY name",
                (current_user.user_id, category)
            )
        else:
            products = await db.fetch_all(
                "SELECT * FROM toko_products WHERE user_id = ? ORDER BY name",
                (current_user.user_id,)
            )
        
        return {
            "status": "success",
            "data": [dict(p) for p in products]
        }
    except Exception as e:
        logger.error(f"Get products error: {e}")
        raise HTTPException(500, str(e))

@router.post("/products")
async def create_product(
    data: Dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Create new product"""
    try:
        import uuid
        product_id = str(uuid.uuid4())
        
        await db.execute(
            """INSERT INTO toko_products 
               (id, user_id, name, price, stock, category, created_at) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                product_id,
                current_user.user_id,
                data.get('name'),
                data.get('price', 0),
                data.get('stock', 0),
                data.get('category', 'general'),
                datetime.now().isoformat()
            )
        )
        
        logger.info(f"✅ Product created: {data.get('name')}")
        return {"status": "success", "data": {"id": product_id}}
        
    except Exception as e:
        logger.error(f"Create product error: {e}")
        raise HTTPException(500, str(e))

@router.put("/products/{product_id}")
async def update_product(
    product_id: str,
    data: Dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Update product"""
    try:
        await db.execute(
            """UPDATE toko_products 
               SET name = ?, price = ?, stock = ?, category = ?
               WHERE id = ? AND user_id = ?""",
            (
                data.get('name'),
                data.get('price'),
                data.get('stock'),
                data.get('category', 'general'),
                product_id,
                current_user.user_id
            )
        )
        
        logger.info(f"✅ Product updated: {product_id}")
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Update product error: {e}")
        raise HTTPException(500, str(e))

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """Delete product"""
    try:
        await db.execute(
            "DELETE FROM toko_products WHERE id = ? AND user_id = ?",
            (product_id, current_user.user_id)
        )
        
        logger.info(f"🗑️ Product deleted: {product_id}")
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Delete product error: {e}")
        raise HTTPException(500, str(e))

# ============ VOICE SCAN ============

@router.post("/scan-voice")
async def scan_voice(
    data: Dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Parse voice/text input for kasir"""
    try:
        text = data.get('text', '').lower()
        
        # Simple parser - detect products & quantities
        # Format: "beli mie goreng 2, teh botol 1"
        
        items = []
        not_found = []
        
        # Split by comma
        parts = text.split(',')
        
        for part in parts:
            # Extract quantity (angka or kata)
            quantity = 1
            
            # Check for numbers
            numbers = re.findall(r'\d+', part)
            if numbers:
                quantity = int(numbers[-1])  # Last number is quantity
            else:
                # Check for Indonesian number words
                if 'satu' in part or 'siji' in part:
                    quantity = 1
                elif 'dua' in part or 'loro' in part:
                    quantity = 2
                elif 'tiga' in part or 'telu' in part:
                    quantity = 3
                elif 'empat' in part or 'papat' in part:
                    quantity = 4
                elif 'lima' in part or 'limo' in part:
                    quantity = 5
            
            # Remove quantity from text to get product name
            product_text = re.sub(r'\d+', '', part)
            product_text = re.sub(r'(satu|dua|tiga|empat|lima|siji|loro|telu|papat|limo)', '', product_text)
            product_text = re.sub(r'(beli|tuku|ambil)', '', product_text)
            product_text = product_text.strip()
            
            if not product_text:
                continue
            
            # Search product in database
            products = await db.fetch_all(
                "SELECT * FROM toko_products WHERE user_id = ? AND LOWER(name) LIKE ?",
                (current_user.user_id, f'%{product_text}%')
            )
            
            if products:
                product = dict(products[0])
                items.append({
                    'id': product['id'],
                    'name': product['name'],
                    'price': product['price'],
                    'quantity': quantity,
                    'subtotal': product['price'] * quantity
                })
            else:
                not_found.append(product_text)
        
        preview = f"Terdeteksi: {len(items)} produk"
        if not_found:
            preview += f", {len(not_found)} tidak ditemukan"
        
        return {
            "status": "success",
            "data": {
                "items": items,
                "not_found": not_found,
                "preview": preview
            }
        }
        
    except Exception as e:
        logger.error(f"Voice scan error: {e}")
        raise HTTPException(500, str(e))

# ============ SALES ============

@router.get("/sales")
async def get_sales(
    limit: int = 10,
    current_user: TokenData = Depends(get_current_user)
):
    """Get recent sales"""
    try:
        sales = await db.fetch_all(
            """SELECT * FROM toko_sales 
               WHERE user_id = ? 
               ORDER BY created_at DESC 
               LIMIT ?""",
            (current_user.user_id, limit)
        )
        
        return {
            "status": "success",
            "data": [dict(s) for s in sales]
        }
    except Exception as e:
        logger.error(f"Get sales error: {e}")
        raise HTTPException(500, str(e))

@router.post("/sales")
async def create_sale(
    data: Dict,
    current_user: TokenData = Depends(get_current_user)
):
    """Create new sale transaction"""
    try:
        import uuid
        sale_id = str(uuid.uuid4())
        
        items = data.get('items', [])
        total = data.get('total', 0)
        
        # Save sale
        await db.execute(
            """INSERT INTO toko_sales 
               (id, user_id, items, total, created_at) 
               VALUES (?, ?, ?, ?, ?)""",
            (
                sale_id,
                current_user.user_id,
                str(items),  # JSON string
                total,
                datetime.now().isoformat()
            )
        )
        
        # Update stock
        for item in items:
            await db.execute(
                "UPDATE toko_products SET stock = stock - ? WHERE id = ?",
                (item['quantity'], item['id'])
            )
        
        logger.info(f"✅ Sale created: Rp {total}")
        return {
            "status": "success",
            "data": {
                "transaction_id": sale_id,
                "total": total
            }
        }
        
    except Exception as e:
        logger.error(f"Create sale error: {e}")
        raise HTTPException(500, str(e))
