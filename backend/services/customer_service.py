import json
from datetime import datetime
from typing import Any, Dict, List, Optional


class CustomerService:
    def __init__(self, db_manager):
        self.db = db_manager

    async def ensure_table(self):
        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                name TEXT,
                phone TEXT,
                store_name TEXT,
                address TEXT,
                customer_type TEXT,
                notes TEXT,
                extra_json TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )

        await self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS customer_drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT,
                payload_json TEXT,
                summary_text TEXT,
                status TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )

    def _normalize_extra(self, extra: Optional[Dict[str, Any]]) -> str:
        return json.dumps(extra or {}, ensure_ascii=False)

    def _parse_extra(self, extra_raw: Any) -> Dict[str, Any]:
        try:
            if isinstance(extra_raw, dict):
                return extra_raw
            return json.loads(extra_raw or "{}")
        except Exception:
            return {}

    def _row_to_customer(self, row: Dict[str, Any]) -> Dict[str, Any]:
        extra = self._parse_extra(row.get("extra_json"))
        return {
            "id": row.get("id"),
            "user_id": row.get("user_id"),
            "name": row.get("name") or "",
            "phone": row.get("phone") or "",
            "store_name": row.get("store_name") or "",
            "address": row.get("address") or "",
            "customer_type": row.get("customer_type") or "",
            "notes": row.get("notes") or "",
            "extra": extra,
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }

    def _row_to_draft(self, row: Dict[str, Any]) -> Dict[str, Any]:
        payload = self._parse_extra(row.get("payload_json"))
        return {
            "id": row.get("id"),
            "user_id": row.get("user_id"),
            "action": row.get("action") or "",
            "payload": payload,
            "summary_text": row.get("summary_text") or "",
            "status": row.get("status") or "pending",
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }

    def _draft_summary(self, data: Dict[str, Any]) -> str:
        extra = data.get("extra") or {}
        lines = ["Data yang akan disimpan:"]

        def add(label: str, value: Any):
            value = "" if value is None else str(value).strip()
            if value:
                lines.append(f"- {label}: {value}")

        add("Nama", data.get("name"))
        add("No HP", data.get("phone"))
        add("Nama toko", data.get("store_name"))
        add("Alamat", data.get("address"))
        add("Tipe", data.get("customer_type"))
        add("Catatan", data.get("notes"))

        for key, label in [
            ("next_visit_date", "Kunjungan berikutnya"),
            ("consignment_qty", "Jumlah barang titip"),
            ("today_sales", "Penjualan hari ini"),
            ("owner_name", "Nama owner"),
        ]:
            add(label, extra.get(key))

        lines.append("")
        lines.append("Lanjut simpan? Balas: ya / tidak / ubah")
        return "\n".join(lines)

    async def create_customer(
        self,
        user_id: str,
        name: str,
        phone: str = "",
        store_name: str = "",
        address: str = "",
        customer_type: str = "",
        notes: str = "",
        extra: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        await self.ensure_table()

        now = datetime.now().isoformat()
        extra_json = self._normalize_extra(extra)

        await self.db.execute(
            """
            INSERT INTO customers
            (user_id, name, phone, store_name, address, customer_type, notes, extra_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                name.strip(),
                phone.strip(),
                store_name.strip(),
                address.strip(),
                customer_type.strip(),
                notes.strip(),
                extra_json,
                now,
                now,
            ),
        )

        row = await self.db.fetch_one("SELECT * FROM customers ORDER BY id DESC LIMIT 1")
        return self._row_to_customer(dict(row))

    async def prepare_customer_create(
        self,
        user_id: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        await self.ensure_table()

        payload = {
            "name": str(data.get("name") or "").strip(),
            "phone": str(data.get("phone") or "").strip(),
            "store_name": str(data.get("store_name") or "").strip(),
            "address": str(data.get("address") or "").strip(),
            "customer_type": str(data.get("customer_type") or "").strip(),
            "notes": str(data.get("notes") or "").strip(),
            "extra": data.get("extra") or {},
        }

        if not payload["name"]:
            raise ValueError("name wajib diisi")

        now = datetime.now().isoformat()
        summary = self._draft_summary(payload)

        await self.db.execute(
            """
            INSERT INTO customer_drafts
            (user_id, action, payload_json, summary_text, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                "create_customer",
                json.dumps(payload, ensure_ascii=False),
                summary,
                "pending",
                now,
                now,
            ),
        )

        row = await self.db.fetch_one("SELECT * FROM customer_drafts ORDER BY id DESC LIMIT 1")
        return self._row_to_draft(dict(row))

    async def get_latest_pending_draft(self, user_id: str) -> Optional[Dict[str, Any]]:
        await self.ensure_table()
        row = await self.db.fetch_one(
            """
            SELECT *
            FROM customer_drafts
            WHERE user_id = ? AND status = 'pending'
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
        )
        return self._row_to_draft(dict(row)) if row else None

    async def confirm_draft(self, draft_id: int, user_id: str) -> Dict[str, Any]:
        await self.ensure_table()

        row = await self.db.fetch_one(
            """
            SELECT *
            FROM customer_drafts
            WHERE id = ? AND user_id = ? AND status = 'pending'
            """,
            (draft_id, user_id),
        )
        if not row:
            raise ValueError("draft tidak ditemukan atau sudah diproses")

        draft = dict(row)
        payload = self._parse_extra(draft.get("payload_json"))

        created = await self.create_customer(
            user_id=user_id,
            name=str(payload.get("name") or ""),
            phone=str(payload.get("phone") or ""),
            store_name=str(payload.get("store_name") or ""),
            address=str(payload.get("address") or ""),
            customer_type=str(payload.get("customer_type") or ""),
            notes=str(payload.get("notes") or ""),
            extra=payload.get("extra") or {},
        )

        await self.db.execute(
            """
            UPDATE customer_drafts
            SET status = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
            """,
            ("confirmed", datetime.now().isoformat(), draft_id, user_id),
        )

        return {
            "draft_id": draft_id,
            "saved": created,
        }

    async def cancel_draft(self, draft_id: int, user_id: str) -> Dict[str, Any]:
        await self.ensure_table()

        row = await self.db.fetch_one(
            """
            SELECT *
            FROM customer_drafts
            WHERE id = ? AND user_id = ? AND status = 'pending'
            """,
            (draft_id, user_id),
        )
        if not row:
            raise ValueError("draft tidak ditemukan atau sudah diproses")

        await self.db.execute(
            """
            UPDATE customer_drafts
            SET status = ?, updated_at = ?
            WHERE id = ? AND user_id = ?
            """,
            ("cancelled", datetime.now().isoformat(), draft_id, user_id),
        )

        return {
            "draft_id": draft_id,
            "status": "cancelled",
        }

    async def update_customer(
        self,
        customer_id: int,
        user_id: str,
        data: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        await self.ensure_table()

        current = await self.db.fetch_one(
            "SELECT * FROM customers WHERE id = ? AND user_id = ?",
            (customer_id, user_id),
        )
        if not current:
            return None

        current = dict(current)
        allowed_core = {"name", "phone", "store_name", "address", "customer_type", "notes"}

        updates = []
        params: List[Any] = []

        for key in allowed_core:
            if key in data:
                updates.append(f"{key} = ?")
                params.append(str(data[key]).strip())

        if "extra" in data:
            updates.append("extra_json = ?")
            params.append(self._normalize_extra(data.get("extra")))

        if not updates:
            return self._row_to_customer(current)

        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.extend([customer_id, user_id])

        await self.db.execute(
            f"""
            UPDATE customers
            SET {", ".join(updates)}
            WHERE id = ? AND user_id = ?
            """,
            tuple(params),
        )

        row = await self.db.fetch_one(
            "SELECT * FROM customers WHERE id = ? AND user_id = ?",
            (customer_id, user_id),
        )
        return self._row_to_customer(dict(row)) if row else None

    async def get_customer(self, customer_id: int, user_id: str) -> Optional[Dict[str, Any]]:
        await self.ensure_table()
        row = await self.db.fetch_one(
            "SELECT * FROM customers WHERE id = ? AND user_id = ?",
            (customer_id, user_id),
        )
        return self._row_to_customer(dict(row)) if row else None

    async def list_customers(
        self,
        user_id: str,
        q: str = "",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        await self.ensure_table()

        limit = max(1, min(int(limit or 50), 200))
        q = (q or "").strip()

        if q:
            rows = await self.db.fetch_all(
                """
                SELECT *
                FROM customers
                WHERE user_id = ?
                  AND (
                    LOWER(name) LIKE LOWER(?)
                    OR LOWER(phone) LIKE LOWER(?)
                    OR LOWER(store_name) LIKE LOWER(?)
                    OR LOWER(address) LIKE LOWER(?)
                    OR LOWER(notes) LIKE LOWER(?)
                  )
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%", limit),
            )
        else:
            rows = await self.db.fetch_all(
                """
                SELECT *
                FROM customers
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            )

        return [self._row_to_customer(dict(r)) for r in rows]
