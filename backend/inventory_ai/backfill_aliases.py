import re
import sqlite3
from pathlib import Path

DB_PATH = Path("/home/dibs/dibs1/data/dibs.db")


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


def remove_size_tokens(text: str) -> str:
    text = normalize_text(text)
    text = re.sub(r'\b\d+(?:[\.,]\d+)?\s*(kg|gr|liter|ml|pcs)\b', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def build_aliases(name: str) -> str:
    base = normalize_text(name)
    no_size = remove_size_tokens(name)

    aliases = set()

    if base:
        aliases.add(base)

    if no_size and no_size != base:
        aliases.add(no_size)

    # typo ringan / variasi umum
    variations = [
        no_size.replace("mie", "mi"),
        no_size.replace("mi", "mie"),
        no_size.replace("sedaap", "sedap"),
        no_size.replace("sedap", "sedaap"),
        no_size.replace("liter", "l"),
        no_size.replace("gr", "gram"),
        no_size.replace("kg", "kilo"),
    ]

    for item in variations:
        item = normalize_text(item)
        if item and len(item) >= 3:
            aliases.add(item)

    # token subset sederhana
    parts = no_size.split()
    if len(parts) >= 2:
        aliases.add(" ".join(parts[:2]))
        aliases.add(" ".join(parts[-2:]))

    aliases = [a for a in aliases if a]
    aliases.sort()
    return ",".join(aliases)


def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT id, name FROM toko_products")
    rows = cur.fetchall()

    updated = 0
    for product_id, name in rows:
        aliases = build_aliases(name or "")
        cur.execute(
            "UPDATE toko_products SET aliases = ? WHERE id = ?",
            (aliases, product_id),
        )
        updated += 1

    conn.commit()
    conn.close()
    print(f"UPDATED_ALIASES={updated}")


if __name__ == "__main__":
    main()
