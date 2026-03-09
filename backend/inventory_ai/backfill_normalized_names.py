import re
import sqlite3
from pathlib import Path

DB_PATH = Path("/home/dibs/dibs1/data/dibs.db")


def normalize_text(text: str) -> str:
    text = (text or "").lower().strip()

    replacements = {
        "kilogram": "kg",
        "kilo": "kg",
        " gram ": " gr ",
        "gram": "gr",
        " g ": " gr ",
        " grm ": " gr ",
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


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM toko_products")
    rows = cur.fetchall()

    updated = 0
    for product_id, name in rows:
        normalized_name = normalize_text(name or "")
        cur.execute(
            "UPDATE toko_products SET normalized_name = ? WHERE id = ?",
            (normalized_name, product_id),
        )
        updated += 1

    conn.commit()
    conn.close()
    print(f"UPDATED_NORMALIZED_NAME={updated}")


if __name__ == "__main__":
    main()
