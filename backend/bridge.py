import os
import httpx
import sqlite3
from dotenv import load_dotenv

load_dotenv()

class DibsBridge:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.serper_key = os.getenv("SERPER_API_KEY")
        self.openclaw_key = os.getenv("OPENCLAW_API_KEY")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        # Mengacu pada dibs1.db yang terlihat di tree
        self.db_path = os.path.join(os.path.dirname(__file__), "dibs1.db")
        self.mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8000")

    async def web_search(self, query: str):
        """Serper.dev Powerup"""
        if not self.serper_key: return {"error": "Serper Key Missing"}
        headers = {"X-API-KEY": self.serper_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            try:
                res = await client.post("https://google.serper.dev/search", 
                                        headers=headers, 
                                        json={"q": query, "gl": "id"}, timeout=10.0)
                return res.json()
            except Exception as e: return {"error": str(e)}

    def store_knowledge(self, content: str, category: str = "user_suggested"):
        """Simpan teks sesuai instruksi [2026-01-06]"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO knowledge (content, category) VALUES (?, ?)", (content, category))
            conn.commit()
            conn.close()
            return "✅ Dibs sudah simpan ini ke memori."
        except Exception as e:
            return f"❌ Gagal simpan: {str(e)}"

    def recall_knowledge(self, query: str):
        """Munculkan teks sesuai instruksi [2026-01-06]"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM knowledge WHERE content LIKE ? ORDER BY timestamp DESC LIMIT 1", (f'%{query}%',))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else "Dibs tidak menemukan catatan terkait itu."
        except Exception as e:
            return f"Error recall: {str(e)}"

dibs_engine = DibsBridge()
