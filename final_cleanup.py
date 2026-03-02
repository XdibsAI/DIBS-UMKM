#!/usr/bin/env python3
"""
Final Cleanup Script untuk DIBS AI
Menghapus file-file yang tidak diperlukan
"""
import os
import shutil
import glob
from pathlib import Path

def cleanup():
    print("🧹 Membersihkan file backup...")
    patterns = ['*.bak', '*.bak.*', '*.pyc']
    for pattern in patterns:
        for f in glob.glob(f"**/{pattern}", recursive=True):
            try:
                os.remove(f)
                print(f"  ✅ Hapus: {f}")
            except:
                pass

    print("\n🧹 Membersihkan __pycache__...")
    for pycache in glob.glob("**/__pycache__", recursive=True):
        try:
            shutil.rmtree(pycache)
            print(f"  ✅ Hapus: {pycache}")
        except:
            pass

    print("\n🧹 Membersihkan file log...")
    log_files = [
        'backend/*.log',
        'downloads/*.log',
        'mcp-server/*.log',
        'frontend/*.log'
    ]
    for pattern in log_files:
        for f in glob.glob(pattern):
            try:
                os.remove(f)
                print(f"  ✅ Hapus: {f}")
            except:
                pass

    print("\n🧹 Membersihkan database lama...")
    old_dbs = [
        'dibs1.db', 'dibs1.db-shm', 'dibs1.db-wal',
        'backend/dibs.db', 'backend/dibs1.db', 'backend/toko.db'
    ]
    for db in old_dbs:
        if os.path.exists(db):
            os.remove(db)
            print(f"  ✅ Hapus: {db}")

    print("\n🧹 Membersihkan file python lama...")
    old_files = [
        'backend/bridge.py',
        'backend/dibs_routes.py',
        'backend/language_intelligence.py',
        'backend/video_generator.py',
        'backend/vision_helper.py',
        'backend/chat/language_detector.py',
        'lib/'
    ]
    for f in old_files:
        if os.path.exists(f):
            if os.path.isdir(f):
                shutil.rmtree(f)
                print(f"  ✅ Hapus folder: {f}")
            else:
                os.remove(f)
                print(f"  ✅ Hapus: {f}")

    print("\n🧹 Archive backup folders...")
    if os.path.exists('backups'):
        tar_cmd = "tar -czf backups/final-backup-$(date +%Y%m%d).tar.gz backups/ 2>/dev/null"
        os.system(tar_cmd)
        shutil.rmtree('backups')
        print("  ✅ Backup di-archive dan dihapus")

    print("\n✨ Cleanup selesai!")
    print("\n📊 Statistik akhir:")
    os.system("du -sh ~/dibs1 | cut -f1")
    os.system("find . -type f | wc -l | xargs echo '  Total files:'")

if __name__ == "__main__":
    print("="*50)
    print("🧹 FINAL CLEANUP DIBS AI")
    print("="*50)
    cleanup()
