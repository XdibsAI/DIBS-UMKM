import re
from inventory_ai.models import InventoryIntentResult


INVENTORY_KEYWORDS = [
    "cek",
    "stok",
    "stock",
    "berapa",
    "harga",
    "ada nggak",
    "ada gak",
    "masih ada",
    "sisa",
    "barang",
    "produk",
    "tersisa",
    "habis",
    "hampir habis",
    "stok menipis",
]

STOCK_KEYWORDS = [
    "stok",
    "stock",
    "sisa",
    "tersisa",
    "masih ada",
    "habis",
]

PRICE_KEYWORDS = [
    "harga",
    "berapa harga",
    "harganya",
]

FIND_KEYWORDS = [
    "ada nggak",
    "ada gak",
    "ada",
    "cari",
    "produk",
    "barang",
]

LOW_STOCK_KEYWORDS = [
    "hampir habis",
    "stok menipis",
    "low stock",
    "stok tipis",
]

# PENTING: unit panjang dulu, baru pendek
SIZE_PATTERN = re.compile(
    r'(\d+(?:[\.,]\d+)?)\s*(kilogram|kilo|kg|gram|gr|g|liter|ltr|ml|pcs|pc|l)\b',
    re.IGNORECASE,
)


def normalize_unit(unit: str) -> str:
    u = unit.lower().strip()
    mapping = {
        "g": "gr",
        "gram": "gr",
        "gr": "gr",
        "kg": "kg",
        "kilo": "kg",
        "kilogram": "kg",
        "l": "liter",
        "ltr": "liter",
        "liter": "liter",
        "ml": "ml",
        "pcs": "pcs",
        "pc": "pcs",
    }
    return mapping.get(u, u)


def cleanup_product_query(text: str) -> str:
    q = text.lower().strip()

    removable_phrases = [
        "hampir habis",
        "stok menipis",
        "berapa harga",
        "ada nggak",
        "ada gak",
        "masih ada",
    ]

    for phrase in removable_phrases:
        q = re.sub(r'\b' + re.escape(phrase) + r'\b', ' ', q)

    q = SIZE_PATTERN.sub(" ", q)

    removable_words = [
        "dibs",
        "cek",
        "stok",
        "stock",
        "berapa",
        "harga",
        "barang",
        "produk",
        "tersisa",
        "sisa",
        "habis",
        "masih",
        "ada",
        "yang",
        "apa",
        "tolong",
        "dong",
        "ya",
        "nih",
        "mohon",
    ]

    for word in removable_words:
        q = re.sub(r'\b' + re.escape(word) + r'\b', ' ', q)

    q = re.sub(r'[^a-z0-9\s]', ' ', q)
    q = re.sub(r'\s+', ' ', q).strip()
    return q


def detect_inventory_intent(text: str) -> InventoryIntentResult:
    raw = (text or "").strip()
    lower = raw.lower()

    found_keywords = [kw for kw in INVENTORY_KEYWORDS if kw in lower]
    if not found_keywords:
        return InventoryIntentResult(
            matched=False,
            raw_text=raw,
            keywords=[],
        )

    intent = "find_product"

    if any(kw in lower for kw in LOW_STOCK_KEYWORDS):
        intent = "low_stock"
    elif any(kw in lower for kw in PRICE_KEYWORDS):
        intent = "check_price"
    elif any(kw in lower for kw in STOCK_KEYWORDS):
        intent = "check_stock"
    elif any(kw in lower for kw in FIND_KEYWORDS):
        intent = "find_product"

    size_value = None
    size_unit = None

    m = SIZE_PATTERN.search(lower)
    if m:
        raw_value = m.group(1).replace(",", ".")
        try:
            size_value = float(raw_value)
        except:
            size_value = None
        size_unit = normalize_unit(m.group(2))

    product_query = cleanup_product_query(raw)

    return InventoryIntentResult(
        matched=True,
        intent=intent,
        product_query=product_query,
        size_value=size_value,
        size_unit=size_unit,
        keywords=found_keywords,
        raw_text=raw,
    )
