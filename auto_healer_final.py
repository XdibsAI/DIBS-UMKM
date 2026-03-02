#!/usr/bin/env python3
"""
DIBS AI Auto-Healing System - With Ollama Fallback
"""
import os
import time
import subprocess
import threading
from datetime import datetime
import re
import json
import requests

class DIBSAutoHealer:
    def __init__(self):
        # Baca API key dari .env
        self.api_key = self.get_api_key()
        self.use_nvidia = bool(self.api_key)
        
        print(f"🔑 NVIDIA API: {'AVAILABLE' if self.use_nvidia else 'NOT FOUND'}")
        print(f"🔄 Fallback ke Ollama jika NVIDIA error")
        
        # File yang dimonitor
        self.log_files = [
            "/home/dibs/dibs1/backend/backend.log",
            "/home/dibs/dibs1/downloads/http.log",
            "/home/dibs/dibs1/mcp-server/mcp.log"
        ]
        
        # Status service
        self.services = {
            "backend": {"port": 8081, "pid": None, "status": "unknown"},
            "download": {"port": 9091, "pid": None, "status": "unknown"},
            "mcp": {"port": 8765, "pid": None, "status": "unknown"}
        }
        
        self.error_history = []
        
    def get_api_key(self):
        try:
            with open('/home/dibs/dibs1/.env', 'r') as f:
                for line in f:
                    if 'NVIDIA_API_KEY' in line and '=' in line:
                        return line.split('=')[1].strip().strip('"').strip("'")
        except:
            pass
        return None
    
    def check_service(self, name, port):
        try:
            result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                pid = result.stdout.strip().split('\n')[0]
                self.services[name] = {"port": port, "pid": pid, "status": "running"}
                return True
            else:
                self.services[name] = {"port": port, "pid": None, "status": "stopped"}
                return False
        except:
            return False
    
    def read_logs(self, lines=30):
        all_logs = []
        for log_file in self.log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        content = f.readlines()[-lines:]
                        all_logs.extend([f"[{os.path.basename(log_file)}] {line.strip()}" for line in content])
                except:
                    pass
        return "\n".join(all_logs)
    
    def detect_errors(self, logs):
        error_patterns = [r"error", r"exception", r"traceback", r"fail", r"cannot", r"unable"]
        errors = []
        for line in logs.split('\n'):
            for pattern in error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    errors.append(line)
                    break
        return errors
    
    def analyze_with_ollama(self, error_log):
        """Analisis pake Ollama lokal (fallback)"""
        try:
            prompt = f"Analisis error ini dan beri solusi singkat (max 2 kalimat):\n{error_log}"
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 200}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('response', 'Tidak ada respons')
        except:
            pass
        return None
    
    def analyze_with_nvidia(self, error_log):
        """Analisis pake NVIDIA (primary)"""
        if not self.api_key:
            return None
            
        try:
            from openai import OpenAI
            client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=self.api_key
            )
            
            prompt = f"Analisis error ini dan beri solusi singkat (max 2 kalimat):\n{error_log}"
            
            completion = client.chat.completions.create(
                model="qwen/qwen3-coder-480b-a35b-instruct",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"⚠️ NVIDIA error: {e}, fallback ke Ollama")
            return None
    
    def heal_loop(self):
        print("🚀 DIBS Auto-Healer started")
        print("📡 Monitoring logs and services...")
        
        while True:
            # Cek services
            for service in self.services:
                self.check_service(service, self.services[service]["port"])
            
            # Baca logs
            logs = self.read_logs(20)
            errors = self.detect_errors(logs)
            
            if errors:
                error_text = "\n".join(errors[:3])
                
                if error_text not in self.error_history[-10:]:
                    print(f"\n🚨 {datetime.now().strftime('%H:%M:%S')} - Error detected")
                    
                    # Coba NVIDIA dulu
                    analysis = self.analyze_with_nvidia(error_text)
                    
                    # Fallback ke Ollama kalau NVIDIA gagal
                    if not analysis:
                        analysis = self.analyze_with_ollama(error_text)
                    
                    if analysis:
                        print(f"💡 {analysis}")
                    else:
                        print("⚠️ No analysis available")
                    
                    self.error_history.append(error_text)
            
            time.sleep(15)
    
    def start(self):
        thread = threading.Thread(target=self.heal_loop, daemon=True)
        thread.start()
        print("✅ Auto-Healer running")
        return thread

if __name__ == "__main__":
    healer = DIBSAutoHealer()
    healer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Auto-Healer stopped")
