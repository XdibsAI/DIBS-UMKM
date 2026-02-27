import os
import httpx
import sqlite3
import base64
from dotenv import load_dotenv

load_dotenv()

class DibsBridge:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.serper_key = os.getenv("SERPER_API_KEY")
        self.ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat") # Gunakan /chat untuk Vision
        self.db_path = os.path.join(os.path.dirname(__file__), "dibs1.db")

    async def web_search(self, query: str):
        if not self.serper_key: return {"error": "Serper Key Missing"}
        headers = {"X-API-KEY": self.serper_key, "Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            try:
                res = await client.post("https://google.serper.dev/search", 
                                        headers=headers, 
                                        json={"q": query, "gl": "id"}, timeout=15.0)
                return res.json()
            except Exception as e: return {"error": str(e)}

    def store_knowledge(self, content: str, category: str = "user_suggested"):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO knowledge (content, category) VALUES (?, ?)", (content, category))
            conn.commit()
            conn.close()
            return "✅ Dibs sudah simpan ini ke memori."
        except Exception as e: return f"❌ Gagal simpan: {str(e)}"

    def recall_knowledge(self, query: str):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT content FROM knowledge WHERE content LIKE ? ORDER BY timestamp DESC LIMIT 1", (f'%{query}%',))
            row = cursor.fetchone()
            conn.close()
            return row[0] if row else "Dibs tidak menemukan catatan terkait itu."
        except Exception as e: return f"Error recall: {str(e)}"

    async def analyze_image(self, filename: str, prompt: str = "Deskripsikan gambar ini"):
        # Cari file di uploads atau test_images
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "uploads", filename),
            os.path.join(os.path.dirname(__file__), "test_images", filename)
        ]
        
        file_path = next((p for p in possible_paths if os.path.exists(p)), None)
            
        if not file_path:
            return f"❌ File {filename} tidak ditemukan."

        try:
            with open(file_path, "rb") as img_file:
                img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

            async with httpx.AsyncClient() as client:
                payload = {
                    "model": "llama3.2-vision",
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt,
                            "images": [img_base64]
                        }
                    ],
                    "stream": False
                }
                # Perhatikan: endpoint chat untuk vision
                res = await client.post("http://localhost:11434/api/chat", json=payload, timeout=120.0)
                result = res.json()
                return result.get("message", {}).get("content", "Gagal mendapatkan deskripsi.")
        except Exception as e:
            return f"Error analyzing image: {str(e)}"

dibs_engine = DibsBridge()
