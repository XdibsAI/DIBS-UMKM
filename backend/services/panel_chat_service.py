import asyncio
import json
import os
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional

from services.simple_panel_observer import SimplePanelObserver


class PanelChatService:
    def __init__(self, db_manager):
        self.db = db_manager
        self.nvidia_api_key = os.getenv("NVIDIA_API_KEY", "").strip()
        self.nvidia_endpoint = os.getenv(
            "NVIDIA_API_BASE",
            "https://integrate.api.nvidia.com/v1/chat/completions",
        ).strip()

        self.nemo_model = os.getenv(
            "NVIDIA_PANEL_MODEL_NEMO",
            "nvidia/nemotron-3-nano-30b-a3b",
        ).strip()

        self.kimi_model = os.getenv(
            "NVIDIA_PANEL_MODEL_KIMI",
            "nvidia/nemotron-3-nano-30b-a3b",
        ).strip()

        self.ngelantur_url = os.getenv(
            "NGELANTUR_URL",
            "http://127.0.0.1:5000/summary",
        ).strip()

        self.observer = SimplePanelObserver()

    async def ensure_tables(self):
        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS panel_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            title TEXT,
            topic TEXT,
            status TEXT DEFAULT 'open',
            trigger_text TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS panel_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            speaker TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)

        await self.db.execute("""
        CREATE TABLE IF NOT EXISTS panel_memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            user_id TEXT NOT NULL,
            topic TEXT,
            raw_summary TEXT,
            key_points_json TEXT DEFAULT '[]',
            action_items_json TEXT DEFAULT '[]',
            created_at TEXT NOT NULL
        )
        """)

    def _trigger_open_panel(self, message: str) -> bool:
        text = (message or "").strip().lower()
        triggers = [
            "dibs ngobrol bareng yuk",
            "dibs diskusi bareng model",
            "dibs ajak model ngobrol",
            "dibs panel diskusi",
        ]
        return any(t in text for t in triggers)

    async def create_session(self, user_id: str, trigger_text: str) -> Dict[str, Any]:
        await self.ensure_tables()
        now = datetime.now().isoformat()

        await self.db.execute(
            """
            INSERT INTO panel_sessions
            (user_id, title, topic, status, trigger_text, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, "Panel Discussion", "", "open", trigger_text, now, now),
        )

        row = await self.db.fetch_one("SELECT * FROM panel_sessions ORDER BY id DESC LIMIT 1")
        return dict(row)

    async def get_open_session(self, user_id: str) -> Optional[Dict[str, Any]]:
        await self.ensure_tables()
        row = await self.db.fetch_one(
            """
            SELECT *
            FROM panel_sessions
            WHERE user_id = ? AND status = 'open'
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,),
        )
        return dict(row) if row else None

    async def append_message(self, session_id: int, user_id: str, speaker: str, role: str, content: str):
        await self.ensure_tables()
        now = datetime.now().isoformat()

        await self.db.execute(
            """
            INSERT INTO panel_messages
            (session_id, user_id, speaker, role, content, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (session_id, user_id, speaker, role, content, now),
        )

        await self.db.execute(
            """
            UPDATE panel_sessions
            SET updated_at = ?
            WHERE id = ? AND user_id = ?
            """,
            (now, session_id, user_id),
        )

    async def get_recent_messages(self, session_id: int, limit: int = 12) -> List[Dict[str, Any]]:
        await self.ensure_tables()
        rows = await self.db.fetch_all(
            """
            SELECT *
            FROM panel_messages
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (session_id, max(1, min(limit, 50))),
        )
        data = [dict(r) for r in rows]
        data.reverse()
        return data

    async def save_memory(self, session_id: int, user_id: str, topic: str, raw_summary: str, key_points: List[str], action_items: List[str]):
        await self.ensure_tables()
        await self.db.execute(
            """
            INSERT INTO panel_memories
            (session_id, user_id, topic, raw_summary, key_points_json, action_items_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                user_id,
                topic,
                raw_summary,
                json.dumps(key_points, ensure_ascii=False),
                json.dumps(action_items, ensure_ascii=False),
                datetime.now().isoformat(),
            ),
        )

    async def _post_json(self, url: str, headers: Dict[str, str], payload: Dict[str, Any], timeout: int = 120) -> Dict[str, Any]:
        def _do():
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        return await asyncio.to_thread(_do)

    async def call_nvidia_model(self, model: str, system_prompt: str, user_prompt: str) -> str:
        if not self.nvidia_api_key:
            return f"[{model}] NVIDIA_API_KEY belum di-set."

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.4,
            "top_p": 0.9,
            "max_tokens": 500,
        }

        headers = {
            "Authorization": f"Bearer {self.nvidia_api_key}",
            "Content-Type": "application/json",
        }

        try:
            data = await self._post_json(self.nvidia_endpoint, headers, payload, timeout=180)
            choices = data.get("choices") or []
            if not choices:
                return f"[{model}] tidak mengembalikan jawaban."
            msg = choices[0].get("message") or {}
            return (msg.get("content") or "").strip() or f"[{model}] jawaban kosong."
        except Exception as e:
            return f"[{model}] error: {e}"

    async def call_ngelantur_summary(self, topic: str, transcript: str) -> Dict[str, Any]:
        payload = {
            "topic": topic,
            "transcript": transcript,
            "max_tokens": 180,
            "temperature": 0.3,
        }
        headers = {"Content-Type": "application/json"}

        try:
            data = await self._post_json(self.ngelantur_url, headers, payload, timeout=120)
            answer = (data.get("answer") or "").strip()
            if not answer:
                return {"raw_summary": "Ngelantur tidak mengembalikan ringkasan.", "key_points": [], "action_items": []}
            return {"raw_summary": answer, "key_points": [], "action_items": []}
        except Exception as e:
            return {"raw_summary": f"Ngelantur error: {e}", "key_points": [], "action_items": []}

    def _build_transcript(self, messages: List[Dict[str, Any]]) -> str:
        return "\n".join([f"{m.get('speaker')}: {m.get('content')}" for m in messages])

    async def handle_message(self, user_id: str, message: str) -> Dict[str, Any]:
        await self.ensure_tables()

        if self._trigger_open_panel(message):
            existing = await self.get_open_session(user_id)
            if existing:
                return {
                    "mode": "panel",
                    "session_id": existing["id"],
                    "message": "Panel sudah aktif.\n- DIBS Moderator\n- DIBS Nemo\n- DIBS Kimi\n- DIBS Observer Internal\n\nTopik apa yang mau dibahas?",
                    "opened": False,
                }

            session = await self.create_session(user_id, message)
            opening = "Panel aktif.\n- DIBS Moderator\n- DIBS Nemo\n- DIBS Kimi\n- DIBS Observer Internal\n\nTopik apa yang mau dibahas?"
            await self.append_message(session["id"], user_id, "moderator", "assistant", opening)
            return {
                "mode": "panel",
                "session_id": session["id"],
                "message": opening,
                "opened": True,
            }

        session = await self.get_open_session(user_id)
        if not session:
            return {"mode": "normal", "message": "Panel belum aktif. Trigger dulu dengan: dibs ngobrol bareng yuk"}

        session_id = session["id"]
        topic = (message or "").strip()

        await self.db.execute(
            "UPDATE panel_sessions SET topic = ?, updated_at = ? WHERE id = ? AND user_id = ?",
            (topic, datetime.now().isoformat(), session_id, user_id),
        )

        await self.append_message(session_id, user_id, "user", "user", topic)

        nemo_system = """Kamu DIBS Nemo.
Peranmu panelis teknis.
Fokus ke:
- akar masalah
- resiko teknis
- solusi paling stabil
Jawab singkat, konkret, maksimal 5 poin."""
        kimi_system = """Kamu DIBS Kimi.
Peranmu panelis strategi.
Fokus ke:
- alternatif pendekatan
- efisiensi
- peluang improvement
Jawab singkat, konkret, maksimal 5 poin."""

        nemo_task = f"Topik diskusi: {topic}\nBerikan pandangan teknis yang fokus dan tidak berulang."
        kimi_task = f"Topik diskusi: {topic}\nBerikan pandangan strategi/alternatif yang berbeda dari panel teknis."

        nemo_reply, kimi_reply = await asyncio.gather(
            self.call_nvidia_model(self.nemo_model, nemo_system, nemo_task),
            self.call_nvidia_model(self.kimi_model, kimi_system, kimi_task),
        )

        if not kimi_reply or "error:" in kimi_reply.lower():
            kimi_reply = "Kimi sedang lambat/timeout. Fokuskan ronde ini ke langkah paling cepat dan efisien dari hasil teknis yang sudah ada."

        moderator_summary = (
            "DIBS Moderator:\n"
            "Saya rangkum hasil panel:\n"
            "- Nemo fokus ke sisi teknis dan stabilitas.\n"
            "- Kimi fokus ke opsi strategi dan efisiensi.\n"
            "Ambil irisan yang paling realistis untuk dikerjakan dulu."
        )

        await self.append_message(session_id, user_id, "nemo", "assistant", nemo_reply)
        await self.append_message(session_id, user_id, "kimi", "assistant", kimi_reply)
        await self.append_message(session_id, user_id, "moderator", "assistant", moderator_summary)

        recent = await self.get_recent_messages(session_id, limit=20)
        transcript = self._build_transcript(recent)

        observer_memory = self.observer.observe(
            topic=topic,
            nemo_reply=nemo_reply,
            kimi_reply=kimi_reply,
            moderator_summary=moderator_summary,
        )

        ngelantur_memory = await self.call_ngelantur_summary(topic=topic, transcript=transcript)

        raw_summary = ngelantur_memory.get("raw_summary") or observer_memory["raw_summary"]
        if raw_summary.lower().startswith("ngelantur error:"):
            raw_summary = observer_memory["raw_summary"]

        final_memory = {
            "raw_summary": raw_summary,
            "key_points": observer_memory["key_points"],
            "action_items": observer_memory["action_items"],
        }

        await self.save_memory(
            session_id=session_id,
            user_id=user_id,
            topic=topic,
            raw_summary=final_memory["raw_summary"],
            key_points=final_memory["key_points"],
            action_items=final_memory["action_items"],
        )

        return {
            "mode": "panel",
            "session_id": session_id,
            "topic": topic,
            "moderator": moderator_summary,
            "panel": {"nemo": nemo_reply, "kimi": kimi_reply},
            "observer": final_memory,
        }
