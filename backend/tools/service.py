import os
import sys
import asyncio
import shutil
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chat.core import ollama_ai

async def auto_service(file_path):
    if not os.path.exists(file_path):
        print("❌ File ora ketemu!")
        return

    # 1. Gawe Backup dhisik (Safety First!)
    backup_path = f"{file_path}.bak_{datetime.now().strftime('%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"📦 Backup digawe: {backup_path}")

    with open(file_path, 'r') as f:
        old_code = f.read()

    print(f"🔧 Dibs lagi nyervis file: {file_path}...")

    prompt = f"""
    Kowe iku Senior Flutter & Python Developer. 
    Tugasmu: DANDANI KODE IKI supaya ora error lan siap di-build.
    
    PERINTAH:
    - Langsung balekne kabeh isi file sing wis bener.
    - OJO menehi penjelasan neng awal utawa akhir.
    - OJO nganggo markdown block (```).
    - Cukup isi filene wae.
    
    FILE: {file_path}
    KODE ERROR:
    {old_code}
    """
    
    try:
        new_code = await ollama_ai.generate(prompt)
        
        # Resik-resik bilih AI isih ngeyel nganggo ```
        clean_code = new_code.replace("```dart", "").replace("```python", "").replace("```", "").strip()

        with open(file_path, 'w') as f:
            f.write(clean_code)
        
        print(f"✅ SERVICE RAMPUNG! File {file_path} wis diupdate.")
        print(f"💡 Yen ana masalah, kowe iso mbalekne nganggo file backup mau.")
    except Exception as e:
        print(f"❌ Gagal nyervis: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 service.py <path_file>")
    else:
        asyncio.run(auto_service(sys.argv[1]))
