import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()
nvidia_api_key = os.getenv("NVIDIA_API_KEY")

print(f"✅ API Key: {nvidia_api_key[:20]}...")

# Read files
files = {}
for f in ["main.dart", "toko_provider.dart"]:
    with open(f"/tmp/code_review/{f}", "r") as file:
        files[f] = file.read()[:2000]  # First 2000 chars only

prompt = f"""Debug Flutter bug:

Tab Produk shows "empty" but API returns 6 products.

toko_provider.dart:
{files['toko_provider.dart']}
main.dart:
{files['main.dart']}
Why is _products empty? Give solution."""

try:
    print("🤖 Calling Nemotron...")
    
    # Use correct model string from settings
    response = requests.post(
        "https://integrate.api.nvidia.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {nvidia_api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": "nvidia/llama-3.1-nemotron-70b-instruct",  # Correct model
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1024,
            "temperature": 0.3
        },
        timeout=90
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    
    if 'choices' in result:
        print("\n" + "="*80)
        print("🤖 ANALYSIS:")
        print("="*80)
        print(result['choices'][0]['message']['content'])
        print("="*80)
    else:
        print("Response:", json.dumps(result, indent=2))
        
except Exception as e:
    print(f"Error: {e}")
