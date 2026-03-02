#!/usr/bin/env python3
"""
DIBS AI Auto-Healing System
Monitor logs, detect errors, suggest fixes, auto-heal
Baca API key dari .env
"""
import os
import time
import subprocess
import threading
from datetime import datetime
from openai import OpenAI
import re
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

class DIBSAutoHealer:
    def __init__(self):
        # Baca API key dari environment (yang sudah di-load dari .env)
        self.api_key = os.getenv("NVIDIA_API_KEY", "")
        if not self.api_key:
            print("⚠️ WARNING: NVIDIA_API_KEY tidak ditemukan di .env")
            print("📁 Mencari di:", env_path)
        
        # NVIDIA AI Client (Qwen Coder untuk analisis)
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=self.api_key
        )
        self.model = "qwen/qwen3-coder-480b-a35b-instruct"
        
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
        
        # Penyimpanan error history
        self.error_history = []
        self.fix_history = []
        
        print(f"🔑 API Key: {self.api_key[:10]}..." if self.api_key else "❌ No API Key")
        
    def check_service(self, name, port):
        """Cek apakah service berjalan"""
        try:
            result = subprocess.run(
                f"lsof -ti:{port}", 
                shell=True, 
                capture_output=True, 
                text=True
            )
            if result.stdout.strip():
                pid = result.stdout.strip().split('\n')[0]
                self.services[name] = {"port": port, "pid": pid, "status": "running"}
                return True
            else:
                self.services[name] = {"port": port, "pid": None, "status": "stopped"}
                return False
        except:
            self.services[name] = {"port": port, "pid": None, "status": "unknown"}
            return False
    
    def read_logs(self, lines=50):
        """Baca log terbaru dari semua file"""
        all_logs = []
        for log_file in self.log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        # Baca 50 baris terakhir
                        content = f.readlines()[-lines:]
                        all_logs.extend([f"[{os.path.basename(log_file)}] {line.strip()}" for line in content])
                except:
                    pass
        return "\n".join(all_logs)
    
    def detect_errors(self, logs):
        """Deteksi error pattern dari log"""
        error_patterns = [
            r"error",
            r"exception",
            r"traceback",
            r"fail",
            r"cannot",
            r"unable",
            r"permission denied",
            r"connection refused",
            r"timeout",
            r"no such table",
            r"invalid credentials",
            r"403 forbidden",
            r"401 unauthorized",
            r"500 internal"
        ]
        
        errors = []
        for line in logs.split('\n'):
            for pattern in error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    errors.append(line)
                    break
        return errors
    
    def analyze_with_ai(self, error_log):
        """Minta AI untuk analisis error dan saran fix"""
        if not error_log:
            return None
        
        if not self.api_key:
            return "⚠️ AI Analysis skipped: No API Key"
            
        prompt = f"""
        Anda adalah AI Senior Developer. Analisis error berikut dari aplikasi DIBS AI:
        
        ERROR LOG:
        {error_log}
        
        Status Services:
        - Backend: {self.services['backend']['status']}
        - Download: {self.services['download']['status']}
        - MCP: {self.services['mcp']['status']}
        
        Tugas Anda:
        1. Identifikasi penyebab error
        2. Berikan saran perbaikan (command yang bisa dijalankan)
        3. Berikan kode fix jika diperlukan
        
        Format respons:
        - PENYEBAB: [penjelasan singkat]
        - SOLUSI: [command atau langkah perbaikan]
        - KODE_FIX: [kode jika perlu]
        """
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
                stream=False
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Gagal analisis AI: {e}"
    
    def auto_fix(self, analysis):
        """Coba fix otomatis berdasarkan analisis AI"""
        if not analysis:
            return False
            
        # Parse command dari analisis
        if "SOLUSI:" in analysis:
            solusi_part = analysis.split("SOLUSI:")[1].split("\n")[0].strip()
            
            # Ekstrak command
            commands = re.findall(r'`([^`]+)`', solusi_part)
            
            for cmd in commands:
                print(f"🔧 Menjalankan: {cmd}")
                try:
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                    if result.returncode == 0:
                        print(f"✅ Berhasil: {cmd}")
                        self.fix_history.append({
                            "time": datetime.now().isoformat(),
                            "command": cmd,
                            "success": True
                        })
                    else:
                        print(f"❌ Gagal: {cmd} - {result.stderr[:100]}")
                except Exception as e:
                    print(f"❌ Error: {e}")
    
    def heal_loop(self):
        """Loop utama healing"""
        print("🚀 DIBS Auto-Healer started")
        print("📡 Monitoring logs and services...")
        print(f"📁 Log files: {', '.join(self.log_files)}")
        
        while True:
            # Cek semua service
            for service in self.services:
                self.check_service(service, self.services[service]["port"])
            
            # Baca logs
            logs = self.read_logs(50)
            
            # Deteksi errors
            errors = self.detect_errors(logs)
            
            if errors:
                error_text = "\n".join(errors[-5:])  # Ambil 5 error terakhir
                
                # Cek apakah error sudah pernah dianalisis
                if error_text not in self.error_history[-10:]:
                    print(f"\n🚨 Error terdeteksi: {datetime.now().isoformat()}")
                    print("-" * 50)
                    
                    # Analisis dengan AI
                    analysis = self.analyze_with_ai(error_text)
                    
                    if analysis:
                        print(analysis)
                        print("-" * 50)
                        
                        # Auto-fix
                        self.auto_fix(analysis)
                        
                        # Simpan history
                        self.error_history.append(error_text)
            
            # Tunggu 30 detik sebelum cek lagi
            time.sleep(30)
    
    def start(self):
        """Start healer di background"""
        thread = threading.Thread(target=self.heal_loop, daemon=True)
        thread.start()
        print("✅ Auto-Healer running in background")
        return thread

if __name__ == "__main__":
    healer = DIBSAutoHealer()
    healer.start()
    
    # Keep main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Auto-Healer stopped")
