import csv
import io
import sqlite3
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse

from auth.utils import get_current_user, TokenData
from inventory_ai.query import normalize_text

router = APIRouter(prefix="/api/v1/inventory-ai", tags=["Inventory AI Import Export"])

DB_PATH = Path("/home/dibs/dibs1/data/dibs.db")


def build_aliases(name: str) -> str:
    base = normalize_text(name)
    no_size = base
    no_size = no_size.replace(" gram", " gr")
    no_size = no_size.replace(" kilogram", " kg")
    no_size = no_size.replace(" liter", " liter")

    aliases = set()
    if base:
        aliases.add(base)
    if no_size and no_size != base:
        aliases.add(no_size)

    variations = [
        no_size.replace("mie", "mi"),
        no_size.replace("mi", "mie"),
        no_size.replace("sedaap", "sedap"),
        no_size.replace("sedap", "sedaap"),
        no_size.replace("keripik", "kripik"),
        no_size.replace("kripik", "keripik"),
        no_size.replace("liter", "l"),
        no_size.replace("gr", "gram"),
        no_size.replace("kg", "kilo"),
    ]

    for item in variations:
        item = normalize_text(item)
        if item and len(item) >= 3:
            aliases.add(item)

    parts = no_size.split()
    if len(parts) >= 2:
        aliases.add(" ".join(parts[:2]))
        aliases.add(" ".join(parts[-2:]))

    return ",".join(sorted(x for x in aliases if x))


def ensure_columns(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(toko_products)")
    cols = [row[1] for row in cur.fetchall()]

    if "normalized_name" not in cols:
        cur.execute("ALTER TABLE toko_products ADD COLUMN normalized_name TEXT")
    if "aliases" not in cols:
        cur.execute("ALTER TABLE toko_products ADD COLUMN aliases TEXT")
    conn.commit()


@router.get("/products/export")
async def export_products(current_user: TokenData = Depends(get_current_user)):
    user_id = str(getattr(current_user, "user_id", getattr(current_user, "id", "")))

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    ensure_columns(conn)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, stock, price, barcode, normalized_name, aliases
        FROM toko_products
        WHERE user_id = ?
        ORDER BY name ASC
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["name", "stock", "price", "barcode", "normalized_name", "aliases"])

    for row in rows:
        writer.writerow([
            row["name"] or "",
            row["stock"] or 0,
            row["price"] or 0,
            row["barcode"] or "",
            row["normalized_name"] or "",
            row["aliases"] or "",
        ])

    output.seek(0)
    filename = "toko_products_export.csv"

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.post("/products/import")
async def import_products(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
):
    user_id = str(getattr(current_user, "user_id", getattr(current_user, "id", "")))

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "File harus CSV")

    content = await file.read()
    try:
        decoded = content.decode("utf-8-sig")
    except Exception:
        raise HTTPException(400, "CSV harus UTF-8")

    reader = csv.DictReader(io.StringIO(decoded))
    required_cols = {"name", "stock", "price"}
    if not reader.fieldnames or not required_cols.issubset(set(reader.fieldnames)):
        raise HTTPException(400, "CSV minimal harus punya kolom: name, stock, price")

    conn = sqlite3.connect(DB_PATH)
    ensure_columns(conn)
    cur = conn.cursor()

    inserted = 0
    updated = 0
    skipped = 0

    for row in reader:
        name = (row.get("name") or "").strip()
        if not name:
            skipped += 1
            continue

        try:
            stock = int(float((row.get("stock") or "0").strip()))
        except Exception:
            stock = 0

        try:
            price = int(float((row.get("price") or "0").strip()))
        except Exception:
            price = 0

        barcode = (row.get("barcode") or "").strip()
        normalized_name = normalize_text(row.get("normalized_name") or name)
        aliases = (row.get("aliases") or "").strip()
        if not aliases:
            aliases = build_aliases(name)

        # barcode prioritas, fallback by exact name per user
        existing = None
        if barcode:
            cur.execute(
                "SELECT id FROM toko_products WHERE user_id = ? AND barcode = ?",
                (user_id, barcode),
            )
            existing = cur.fetchone()

        if not existing:
            cur.execute(
                "SELECT id FROM toko_products WHERE user_id = ? AND LOWER(name) = LOWER(?)",
                (user_id, name),
            )
            existing = cur.fetchone()

        if existing:
            cur.execute("""
                UPDATE toko_products
                SET name = ?, stock = ?, price = ?, barcode = ?, normalized_name = ?, aliases = ?
                WHERE id = ?
            """, (
                name, stock, price, barcode, normalized_name, aliases, existing[0]
            ))
            updated += 1
        else:
            cur.execute("""
                INSERT INTO toko_products
                (user_id, name, stock, price, barcode, normalized_name, aliases)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, name, stock, price, barcode, normalized_name, aliases
            ))
            inserted += 1

    conn.commit()
    conn.close()

    return {
        "status": "success",
        "data": {
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
            "total_processed": inserted + updated + skipped,
        }
    }
