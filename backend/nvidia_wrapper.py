#!/usr/bin/env python3
"""NVIDIA Nemotron wrapper using OpenAI SDK"""
import os
import json
import sys
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NVIDIAClient:
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY")
        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY not found in environment")
        
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=self.api_key
        )
        self.model = "nvidia/nemotron-3-nano-30b-a3b"
    
    def chat(self, prompt: str, temperature: float = 1.0, max_tokens: int = 16384, stream: bool = False):
        """Chat dengan NVIDIA Nemotron"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                top_p=1,
                max_tokens=max_tokens,
                extra_body={
                    "reasoning_budget": 16384,
                    "chat_template_kwargs": {"enable_thinking": False}  # Matikan thinking biar cepat
                },
                stream=stream
            )
            
            if stream:
                return completion
            else:
                return completion.choices[0].message.content
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def chat_stream_collect(self, prompt: str) -> str:
        """Collect stream response into string"""
        stream = self.chat(prompt, stream=True)
        response = []
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                response.append(chunk.choices[0].delta.content)
        return ''.join(response)

# Singleton instance
_nvidia_client = None

def get_nvidia_client():
    global _nvidia_client
    if _nvidia_client is None:
        try:
            _nvidia_client = NVIDIAClient()
        except Exception as e:
            print(f"Error initializing NVIDIA client: {e}", file=sys.stderr)
            return None
    return _nvidia_client

def ask_nvidia(prompt: str) -> str:
    """Ask NVIDIA Nemotron (simplified)"""
    client = get_nvidia_client()
    if not client:
        return "Error: NVIDIA client not available (check API key)"
    
    try:
        return client.chat_stream_collect(prompt)
    except Exception as e:
        return f"Error: {str(e)}"

# For direct testing
if __name__ == "__main__":
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Halo, apa kabar?"
    result = ask_nvidia(prompt)
    print(result)
