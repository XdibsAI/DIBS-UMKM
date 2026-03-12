import json
from datetime import datetime
from typing import Any, Dict, Optional, List


class ChatbotService:
    def __init__(self, db_manager):
        self.db = db_manager

    async def ensure_tables(self):
        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS chat_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            channel TEXT NOT NULL DEFAULT 'chat',
            external_id TEXT NOT NULL,
            display_name TEXT,
            phone TEXT,
            customer_id INTEGER,
            status TEXT DEFAULT 'known',
            profile_json TEXT DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id, channel, external_id)
        )
        """)

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS chatbot_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            contact_id INTEGER NOT NULL,
            session_key TEXT,
            current_intent TEXT,
            context_json TEXT DEFAULT '{}',
            started_at TEXT NOT NULL,
            last_message_at TEXT NOT NULL,
            status TEXT DEFAULT 'open'
        )
        """)

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS chatbot_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            session_id INTEGER NOT NULL,
            contact_id INTEGER NOT NULL,
            sender_role TEXT NOT NULL,
            message_text TEXT NOT NULL,
            message_type TEXT DEFAULT 'text',
            metadata_json TEXT DEFAULT '{}',
            created_at TEXT NOT NULL
        )
        """)

    def _loads(self, value: Any) -> Dict[str, Any]:
        try:
            if isinstance(value, dict):
                return value
            return json.loads(value or "{}")
        except Exception:
            return {}

    def _contact_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": row.get("id"),
            "user_id": row.get("user_id"),
            "channel": row.get("channel"),
            "external_id": row.get("external_id"),
            "display_name": row.get("display_name") or "",
            "phone": row.get("phone") or "",
            "customer_id": row.get("customer_id"),
            "status": row.get("status") or "known",
            "profile": self._loads(row.get("profile_json")),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }

    def _session_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": row.get("id"),
            "user_id": row.get("user_id"),
            "contact_id": row.get("contact_id"),
            "session_key": row.get("session_key") or "",
            "current_intent": row.get("current_intent") or "",
            "context": self._loads(row.get("context_json")),
            "started_at": row.get("started_at"),
            "last_message_at": row.get("last_message_at"),
            "status": row.get("status") or "open",
        }

    async def identify_contact(
        self,
        user_id: str,
        external_id: str,
        channel: str = "chat",
        display_name: str = "",
        phone: str = "",
    ) -> Dict[str, Any]:
        await self.ensure_tables()
        now = datetime.now().isoformat()

        row = await self.db.fetch_one(
            """
            SELECT *
            FROM chat_contacts
            WHERE user_id = ? AND channel = ? AND external_id = ?
            LIMIT 1
            """,
            (user_id, channel, external_id),
        )

        if row:
            await self.db.execute(
                """
                UPDATE chat_contacts
                SET display_name = COALESCE(NULLIF(?, ''), display_name),
                    phone = COALESCE(NULLIF(?, ''), phone),
                    updated_at = ?
                WHERE id = ?
                """,
                (display_name, phone, now, dict(row)["id"]),
            )
            row2 = await self.db.fetch_one("SELECT * FROM chat_contacts WHERE id = ?", (dict(row)["id"],))
            return self._contact_row(dict(row2))

        await self.db.execute(
            """
            INSERT INTO chat_contacts
            (user_id, channel, external_id, display_name, phone, status, profile_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                channel,
                external_id,
                display_name,
                phone,
                "known",
                "{}",
                now,
                now,
            ),
        )

        created = await self.db.fetch_one("SELECT * FROM chat_contacts ORDER BY id DESC LIMIT 1")
        return self._contact_row(dict(created))

    async def get_or_create_open_session(
        self,
        user_id: str,
        contact_id: int,
    ) -> Dict[str, Any]:
        await self.ensure_tables()
        now = datetime.now().isoformat()

        row = await self.db.fetch_one(
            """
            SELECT *
            FROM chatbot_sessions
            WHERE user_id = ? AND contact_id = ? AND status = 'open'
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id, contact_id),
        )

        if row:
            await self.db.execute(
                """
                UPDATE chatbot_sessions
                SET last_message_at = ?
                WHERE id = ?
                """,
                (now, dict(row)["id"]),
            )
            row2 = await self.db.fetch_one("SELECT * FROM chatbot_sessions WHERE id = ?", (dict(row)["id"],))
            return self._session_row(dict(row2))

        await self.db.execute(
            """
            INSERT INTO chatbot_sessions
            (user_id, contact_id, session_key, current_intent, context_json, started_at, last_message_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                contact_id,
                f"{user_id}:{contact_id}:{int(datetime.now().timestamp())}",
                "",
                "{}",
                now,
                now,
                "open",
            ),
        )

        created = await self.db.fetch_one("SELECT * FROM chatbot_sessions ORDER BY id DESC LIMIT 1")
        return self._session_row(dict(created))

    async def append_message(
        self,
        user_id: str,
        session_id: int,
        contact_id: int,
        sender_role: str,
        message_text: str,
        message_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        await self.ensure_tables()
        now = datetime.now().isoformat()

        await self.db.execute(
            """
            INSERT INTO chatbot_messages
            (user_id, session_id, contact_id, sender_role, message_text, message_type, metadata_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                session_id,
                contact_id,
                sender_role,
                message_text,
                message_type,
                json.dumps(metadata or {}, ensure_ascii=False),
                now,
            ),
        )

        await self.db.execute(
            """
            UPDATE chatbot_sessions
            SET last_message_at = ?
            WHERE id = ?
            """,
            (now, session_id),
        )

        row = await self.db.fetch_one("SELECT * FROM chatbot_messages ORDER BY id DESC LIMIT 1")
        return dict(row)

    async def get_recent_messages(
        self,
        user_id: str,
        contact_id: int,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        await self.ensure_tables()
        rows = await self.db.fetch_all(
            """
            SELECT *
            FROM chatbot_messages
            WHERE user_id = ? AND contact_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, contact_id, max(1, min(limit, 100))),
        )
        return [dict(r) for r in rows]

    async def get_contact_context(
        self,
        user_id: str,
        contact_id: int,
    ) -> Dict[str, Any]:
        await self.ensure_tables()

        contact_row = await self.db.fetch_one(
            "SELECT * FROM chat_contacts WHERE id = ? AND user_id = ?",
            (contact_id, user_id),
        )
        if not contact_row:
            raise ValueError("contact tidak ditemukan")

        contact = self._contact_row(dict(contact_row))
        customer = None
        tasks = []
        drafts = []

        if contact.get("customer_id"):
            customer = await self.db.fetch_one(
                "SELECT * FROM customers WHERE id = ? AND user_id = ?",
                (contact["customer_id"], user_id),
            )
            if customer:
                customer = dict(customer)

            task_rows = await self.db.fetch_all(
                """
                SELECT *
                FROM customer_tasks
                WHERE customer_id = ? AND user_id = ? AND status = 'pending'
                ORDER BY due_date ASC, id DESC
                LIMIT 10
                """,
                (contact["customer_id"], user_id),
            )
            tasks = [dict(r) for r in task_rows]

        draft_rows = await self.db.fetch_all(
            """
            SELECT *
            FROM customer_drafts
            WHERE user_id = ? AND status = 'pending'
            ORDER BY id DESC
            LIMIT 5
            """,
            (user_id,),
        )
        drafts = [dict(r) for r in draft_rows]

        recent_messages = await self.get_recent_messages(user_id=user_id, contact_id=contact_id, limit=10)

        return {
            "contact": contact,
            "customer": customer,
            "pending_tasks": tasks,
            "pending_drafts": drafts,
            "recent_messages": recent_messages,
        }
