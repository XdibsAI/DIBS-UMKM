import re
from typing import List, Dict, Optional


def normalize_text(text: str) -> str:
    text = (text or "").lower().strip()

    replacements = {
        "kilogram": "kg",
        "kilo": "kg",
        "gram": "gr",
        " g ": " gr ",
        "liter": "liter",
        "ltr": "liter",
        " l ": " liter ",
        "pcs": "pcs",
        "pc": "pcs",
    }

    text = f" {text} "
    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r'(\d)\s*gr\b', r'\1 gr', text)
    text = re.sub(r'(\d)\s*kg\b', r'\1 kg', text)
    text = re.sub(r'(\d)\s*liter\b', r'\1 liter', text)
    text = re.sub(r'(\d)\s*ml\b', r'\1 ml', text)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def tokenize(text: str) -> List[str]:
    return [t for t in normalize_text(text).split() if len(t) >= 2]


def _size_patterns(size_value: Optional[float], size_unit: Optional[str]) -> List[str]:
    if size_value is None or not size_unit:
        return []

    if float(size_value).is_integer():
        value_text = str(int(size_value))
    else:
        value_text = str(size_value).replace(".0", "")

    unit = size_unit.lower().strip()
    patterns = [
        f"{value_text} {unit}",
        f"{value_text}{unit}",
    ]

    if unit == "liter":
        patterns.extend([f"{value_text} l", f"{value_text}l", f"{value_text} liter"])
    elif unit == "gr":
        patterns.extend([f"{value_text} g", f"{value_text}g", f"{value_text} gr"])
    elif unit == "kg":
        patterns.extend([f"{value_text} kilo", f"{value_text} kilogram", f"{value_text}kg"])
    elif unit == "pcs":
        patterns.extend([f"{value_text} pc", f"{value_text}pcs"])

    return list(dict.fromkeys(normalize_text(p) for p in patterns))


def score_product_match(
    product_name: str,
    product_normalized_name: str,
    product_barcode: str,
    product_query: str,
    size_value: Optional[float],
    size_unit: Optional[str],
) -> int:
    name_norm = normalize_text(product_name)
    normalized_name = normalize_text(product_normalized_name or product_name)
    barcode_norm = normalize_text(product_barcode)
    query_norm = normalize_text(product_query)
    query_tokens = tokenize(product_query)

    score = 0

    if not query_norm:
        score += 1

    if query_norm and query_norm == normalized_name:
        score += 140
    elif query_norm and query_norm == name_norm:
        score += 120

    if query_norm and query_norm in normalized_name:
        score += 80
    elif query_norm and query_norm in name_norm:
        score += 60

    matched_tokens = 0
    for token in query_tokens:
        if token in normalized_name:
            matched_tokens += 1
            score += 15
        elif token in name_norm:
            matched_tokens += 1
            score += 12
        elif token in barcode_norm:
            matched_tokens += 1
            score += 20

    if query_tokens and matched_tokens == len(query_tokens):
        score += 30
    elif query_tokens and matched_tokens >= max(1, len(query_tokens) - 1):
        score += 10

    size_patterns = _size_patterns(size_value, size_unit)
    if size_patterns:
        if any(p in normalized_name for p in size_patterns):
            score += 45
        elif any(p in name_norm for p in size_patterns):
            score += 30
        else:
            score -= 15

    return score


async def search_inventory_products(
    db,
    user_id: str,
    product_query: str,
    size_value: Optional[float] = None,
    size_unit: Optional[str] = None,
    limit: int = 8,
) -> List[Dict]:
    query_norm = normalize_text(product_query)
    query_tokens = tokenize(product_query)

    rows = []
    if query_tokens:
        sql = """
        SELECT id, name, normalized_name, stock, price, barcode
        FROM toko_products
        WHERE user_id = ?
          AND (
        """
        conditions = []
        params = [user_id]

        for token in query_tokens[:5]:
            conditions.append("LOWER(COALESCE(normalized_name, name)) LIKE ?")
            params.append(f"%{token}%")

        sql += " OR ".join(conditions)
        sql += """
          )
        ORDER BY name ASC
        LIMIT 200
        """
        rows = await db.fetch_all(sql, tuple(params))

    if not rows:
        rows = await db.fetch_all(
            """
            SELECT id, name, normalized_name, stock, price, barcode
            FROM toko_products
            WHERE user_id = ?
            ORDER BY name ASC
            LIMIT 700
            """,
            (user_id,),
        )

    ranked = []
    for row in rows:
        item = dict(row)
        score = score_product_match(
            item.get("name", ""),
            item.get("normalized_name", ""),
            item.get("barcode", ""),
            query_norm,
            size_value,
            size_unit,
        )
        if score > 0:
            item["match_score"] = score
            ranked.append(item)

    ranked.sort(
        key=lambda x: (
            -x["match_score"],
            x.get("stock", 0) == 0,
            x.get("name", ""),
        )
    )
    return ranked[:limit]


async def get_low_stock_products_local(db, user_id: str, threshold: int = 5, limit: int = 10) -> List[Dict]:
    rows = await db.fetch_all(
        """
        SELECT id, name, normalized_name, stock, price, barcode
        FROM toko_products
        WHERE user_id = ? AND stock <= ?
        ORDER BY stock ASC, name ASC
        LIMIT ?
        """,
        (user_id, threshold, limit),
    )
    return [dict(r) for r in rows]


def format_rupiah(value) -> str:
    try:
        n = int(value or 0)
    except:
        n = 0
    return f"Rp {n:,}".replace(",", ".")


def build_stock_response(product_query: str, products: List[Dict]) -> str:
    if not products:
        return f"Stok untuk '{product_query}' tidak ditemukan."

    if len(products) == 1 or (products and products[0].get("match_score", 0) >= 120 and (
        len(products) == 1 or products[0].get("match_score", 0) - products[1].get("match_score", 0) >= 25
    )):
        item = products[0]
        return f"Stok {item.get('name', 'produk')} tersisa {item.get('stock', 0)} pcs."

    lines = [f"Saya menemukan {len(products)} varian untuk '{product_query}':", ""]
    for item in products:
        lines.append(f"- {item.get('name', 'Produk')}: stok {item.get('stock', 0)} pcs")
    return "\n".join(lines)


def build_price_response(product_query: str, products: List[Dict]) -> str:
    if not products:
        return f"Harga untuk '{product_query}' tidak ditemukan."

    if len(products) == 1 or (products and products[0].get("match_score", 0) >= 120 and (
        len(products) == 1 or products[0].get("match_score", 0) - products[1].get("match_score", 0) >= 25
    )):
        item = products[0]
        return f"Harga {item.get('name', 'produk')} adalah {format_rupiah(item.get('price', 0))}."

    lines = [f"Harga produk untuk '{product_query}':", ""]
    for item in products:
        lines.append(f"- {item.get('name', 'Produk')}: {format_rupiah(item.get('price', 0))}")
    return "\n".join(lines)


def build_low_stock_response(products: List[Dict]) -> str:
    if not products:
        return "Saat ini tidak ada produk yang stoknya menipis."

    lines = ["Produk yang stoknya menipis:", ""]
    for item in products:
        lines.append(f"- {item.get('name', 'Produk')}: stok {item.get('stock', 0)} pcs")
    return "\n".join(lines)
