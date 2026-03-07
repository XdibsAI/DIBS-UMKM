import asyncio
import sys
sys.path.insert(0, '.')
from chat.kimi_ai import KimiAI
from dotenv import load_dotenv
import os

async def main():
    load_dotenv()
    api_key = os.getenv("NVIDIA_API_KEY")
    kimi = KimiAI(api_key)
    
    # Read code
    with open('/tmp/code_review/toko_provider.dart', 'r') as f:
        provider = f.read()[:2500]
    
    prompt = f"""Analisa Flutter bug:

Tab Produk empty tapi API return 6 products. Dashboard works.

toko_provider.dart:
{provider}
Why _products empty? Give solution."""

    print("🤖 Kimi analyzing...")
    result = await kimi.generate(prompt)
    
    print("\n" + "="*80)
    print(result)
    print("="*80)

asyncio.run(main())
