import json
from datetime import datetime, timedelta

def _start_end(period: str):
    now = datetime.now()
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "week":
        start = now - timedelta(days=7)
    elif period == "month":
        start = now - timedelta(days=30)
    else:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start, now

async def get_low_stock_products(db, user_id: str, threshold: int = 5):
    rows = await db.fetch_all(
        """
        SELECT id, name, stock, price, barcode
        FROM toko_products
        WHERE user_id = ? AND stock <= ?
        ORDER BY stock ASC, name ASC
        """,
        (user_id, threshold)
    )
    return [dict(r) for r in rows]

async def get_sales_rows(db, user_id: str, period: str = "today"):
    start, end = _start_end(period)
    rows = await db.fetch_all(
        """
        SELECT id, total, items, payment_method, created_at
        FROM toko_sales
        WHERE user_id = ? AND created_at BETWEEN ? AND ?
        ORDER BY created_at DESC
        """,
        (user_id, start.isoformat(), end.isoformat())
    )
    return [dict(r) for r in rows], start, end

def parse_sale_items(raw):
    try:
        if isinstance(raw, list):
            return raw
        if isinstance(raw, str) and raw.strip():
            return json.loads(raw)
    except:
        pass
    return []

def aggregate_top_products(sales_rows, limit: int = 5):
    bucket = {}
    for sale in sales_rows:
        for item in parse_sale_items(sale.get("items")):
            name = (item.get("name") or "Produk").strip()
            qty = item.get("qty", item.get("quantity", 0)) or 0
            try:
                qty = int(qty)
            except:
                qty = 0
            bucket[name] = bucket.get(name, 0) + qty

    ranked = sorted(bucket.items(), key=lambda x: x[1], reverse=True)
    return [{"name": name, "qty": qty} for name, qty in ranked[:limit]]

def summarize_payment_methods(sales_rows):
    result = {}
    for sale in sales_rows:
        pm = (sale.get("payment_method") or "cash").strip() or "cash"
        result[pm] = result.get(pm, 0) + 1
    return result

def total_sales(sales_rows):
    total = 0
    for sale in sales_rows:
        try:
            total += int(sale.get("total", 0) or 0)
        except:
            pass
    return total
