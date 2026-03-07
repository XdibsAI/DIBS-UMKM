import asyncio
import sys
sys.path.insert(0, '.')
from chat.core import NemotronAI

async def main():
    nemotron = NemotronAI()
    prompt = "Flutter: why is _products list empty after API call? API returns data but UI shows empty."
    
    print("🤖 Testing Nemotron...")
    result = await nemotron.generate(prompt, "test", [], None)
    print(f"\n{result}\n")

asyncio.run(main())
