#!/usr/bin/env python3
"""
DIBS Auto - Analisa langsung dandani
Cara: dibs-auto <file>
Contoh: dibs-auto main.dart
"""

import os
import sys
import asyncio
import shutil
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chat.core import ollama_ai

# Mapping file
FILE_MAP = {
    "main.dart": "/home/dibs/dibs1/frontend/lib/main.dart",
    "core.py": "/home/dibs/dibs1/backend/chat/core.py",
    "pubspec.yaml": "/home/dibs/dibs1/frontend/pubspec.yaml",
    "chat_screen.dart": "/home/dibs/dibs1/frontend/lib/screens/chat/chat_screen.dart",
    "api_service.dart": "/home/dibs/dibs1/frontend/lib/services/api_service.dart",
    "login_screen.dart": "/home/dibs/dibs1/frontend/lib/screens/auth/login_screen.dart",
}


def cari_file(nama):
    """Golek file sing luwih pinter (Anti-Kaku)"""
    base_dir = "/home/dibs/dibs1"
    
    # 1. Cek neng FILE_MAP
    if nama in FILE_MAP:
        return FILE_MAP[nama]
    
    # 2. Cek path absolut utawa langsung
    if os.path.exists(nama):
        return os.path.abspath(nama)
    
    # 3. Cek path relatif seko project root (misal: frontend/lib/...)
    p_root = os.path.join(base_dir, nama)
    if os.path.exists(p_root):
        return p_root
    
    # 4. Search otomatis yen mung ngetik jeneng filene tok
    clean_name = os.path.basename(nama)
    for root, dirs, files in os.walk(base_dir):
        if any(x in root for x in ['venv', '.git', '__pycache__', 'build']):
            continue
        if clean_name in files:
            return os.path.join(root, clean_name)
    
    return None


async def remed_file(file_path, ulang=0):
    """Remed file - ANALISA → DANDANI → CEK MANEH"""
    
    # CEK FILE
    if not os.path.exists(file_path):
        print(f"❌ File ora ketemu: {file_path}")
        return False
    
    # BACA FILE
    with open(file_path, 'r') as f:
        kode_asli = f.read()
    
    print(f"\n📂 FILE: {os.path.basename(file_path)}")
    print(f"📍 Lokasi: {file_path}")
    print(f"📊 Ukuran: {len(kode_asli)} karakter, {len(kode_asli.splitlines())} baris")
    print("=" * 60)
    
    # ===== LANGKAH 1: ANALISA =====
    print("🔍 LAGI ANALISA...")
    
    prompt_analisa = f"""
    Tugas: Analisa kode iki, sebutna 3 MASALAH UTAMA sing kudu didandani.
    
    FILE: {os.path.basename(file_path)}
    
    KODE:
    {kode_asli[:4000]}
    
    TULISKAN FORMAT BENER:
    [MASALAH1] - [baris kira-kira]
    [MASALAH2] - [baris kira-kira]
    [MASALAH3] - [baris kira-kira]
    
    Contoh:
    Typo variable glowController - baris 156
    Async tanpa error handling - baris 45
    Import kurang - baris 3
    """
    
    try:
        hasil_analisa = await ollama_ai.generate(prompt_analisa)
        print("\n📋 HASIL ANALISA:")
        print(hasil_analisa)
        print("=" * 60)
        
        # CEK APA MASIH ONO MASALAH?
        if "ora ono masalah" in hasil_analisa.lower() or "bersih" in hasil_analisa.lower() or "apik" in hasil_analisa.lower():
            print("✅ FILE WIS BERSIH! Ora perlu dandani.")
            return True
        
        # ===== LANGKAH 2: KONFIRMASI =====
        if ulang == 0:
            jawab = input("\n🔧 Dandani masalah-masalah iki? (y/n): ").lower()
            if jawab != 'y':
                print("⏭️  Skip dandani.")
                return True
        
        # ===== LANGKAH 3: DANDANI =====
        print("\n🔧 LAGI NDANDANI...")
        
        # BACKUP DISEK
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"
        shutil.copy2(file_path, backup_path)
        print(f"💾 Backup: {os.path.basename(backup_path)}")
        
        # PROMPT DANDANI
        prompt_dandani = f"""
        Tugas: Dandani kode iki sesuai masalah sing wis dianalisa.
        
        FILE: {os.path.basename(file_path)}
        
        MASALAH:
        {hasil_analisa}
        
        KODE ASLI:
        {kode_asli}
        
        ATURAN PENTING:
        1. Balikke KABEH kode sing wis didandani (OJO ONO PENJELASAN BAHASA MANUSIA NENG NJERO KODE)
        2. PASTIKKE OUTPUT IKI KODE PROGRAM SING BISA DI-RUN (DART/PYTHON)
        3. OJO NERJEMAHKE KODE DADI KALIMAT
        2. OJO nganggo backticks (```)
        3. Tandai owahan nganggo "// FIXED:" utawa "# FIXED:"
        4. Dandani masalah sing disebut tok
        5. OJO ngrusak kode liyane
        """
        
        hasil_dandani = await ollama_ai.generate(prompt_dandani)
        kode_anyar = hasil_dandani.replace("```dart", "").replace("```python", "").replace("```yaml", "").replace("```", "").strip()
        
        # TULIS FILE
        with open(file_path, 'w') as f:
            f.write(kode_anyar)
        
        # TAMPILKE RINGKESAN
        garis_asli = len(kode_asli.splitlines())
        garis_anyar = len(kode_anyar.splitlines())
        
        print("\n✅ SUKSES DIDANDANI!")
        print("=" * 60)
        print(f"📊 Ringkesan:")
        print(f"   - Garis: {garis_asli} → {garis_anyar}")
        print(f"   - Backup: {os.path.basename(backup_path)}")
        
        # TEMUKAN BAGIAN SING DIOWAHI
        asli_lines = kode_asli.splitlines()
        anyar_lines = kode_anyar.splitlines()
        
        print("\n📝 Bagian sing diowahi:")
        owahan = 0
        for i, (asli, anyar) in enumerate(zip(asli_lines, anyar_lines)):
            if asli != anyar:
                owahan += 1
                print(f"\n  Baris {i+1}:")
                print(f"  - {asli[:60]}{'...' if len(asli) > 60 else ''}")
                print(f"  + {anyar[:60]}{'...' if len(anyar) > 60 else ''}")
                if owahan >= 3:  # Cukup 3 owahan
                    print("  ... lan liyane")
                    break
        
        print("=" * 60)
        
        # ===== LANGKAH 4: CEK MANEH (LOOP) =====
        print("\n🔍 CEK MANEH YOK ISIH ONO MASALAH ORA...")
        
        # TUNGGU BENTAR
        await asyncio.sleep(2)
        
        # CEK MANEH (REKURSIF MAKSIMAL 3x)
        if ulang < 3:
            print(f"➡️  Remed putaran {ulang+2}/4")
            # PANGGIL MANEH DIRI SENDIRI
            return await remed_file(file_path, ulang+1)
        else:
            print("\n✅ REMED SELESAI! (wis 4x remed)")
            return True
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def main():
    if len(sys.argv) < 2:
        print("""
╔═══════════════════════════════════════════════╗
║    DIBS AUTO v2 - REMED SAMPAI BERSIH        ║
╚═══════════════════════════════════════════════╝

CARANE:
  remed <file>

CONTOH:
  remed main.dart
  remed core.py
  remed pubspec.yaml

PROSES:
  1️⃣ Analisa file → nemokake masalah
  2️⃣ Dandani otomatis
  3️⃣ CEK MANEH → yen isih ono masalah
  4️⃣ DANDANI MANEH → sampe 4x putaran
  5️⃣ Backup saben putaran

FILE SUPPORT:
  • main.dart • core.py • pubspec.yaml
  • chat_screen.dart • api_service.dart • login_screen.dart
""")
        return
    
    # Golek file
    file_input = sys.argv[1]
    file_path = cari_file(file_input)
    
    if not file_path:
        print(f"❌ File '{file_input}' ora ketemu.")
        print("   Coba: main.dart, core.py, pubspec.yaml")
        return
    
    print("\n" + "🚀" * 30)
    print("🚀 DIBS AUTO - REMED BERANTAI")
    print("🚀" * 30)
    
    await remed_file(file_path, 0)
    
    print("\n" + "✅" * 30)
    print("✅ PROSES REMED SELESAI!")
    print("✅" * 30)

if __name__ == "__main__":
    asyncio.run(main())
