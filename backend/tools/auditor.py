import os
import sys
import asyncio

# Nambahake path supaya bisa import core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from chat.core import ollama_ai

async def audit_code(target_file):
    print(f"🔍 Dibs lagi ngecek file: {target_file}...")
    
    if not os.path.exists(target_file):
        print("❌ Waduh Jon, file-e ora ketemu!")
        return

    try:
        with open(target_file, 'r') as f:
            code = f.read()

        prompt = f"""
        ANALISA KODE IKI:
        File: {target_file}
        
        Tugasmu:
        1. Goleki error syntax, import sing kurang, utawa typo.
        2. Goleki bug logic.
        3. Menehi solusi kode sing bener lan ringkes.
        
        KODE:
        {code}
        """
        
        response = await ollama_ai.generate(prompt)
        print("\n=== 🤖 ANALISA DIBS ===")
        print(response)
        print("=======================\n")
    except Exception as e:
        print(f"❌ Error pas moco file utawa audit: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 auditor.py <path_file>")
    else:
        file_to_check = sys.argv[1]
        asyncio.run(audit_code(file_to_check))
