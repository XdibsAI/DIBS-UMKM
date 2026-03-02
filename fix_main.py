#!/usr/bin/env python3
"""
Fix main.py - Move signal handlers to correct position
"""
import re

def fix_main():
    with open('backend/main.py', 'r') as f:
        content = f.read()
    
    # Hapus signal handler yang ada di akhir file
    signal_pattern = r'# ===== GRACEFUL SHUTDOWN =====.*?loop\.add_signal_handler.*?\n'
    content = re.sub(signal_pattern, '', content, flags=re.DOTALL)
    
    # Tambahkan signal handler di dalam lifespan setelah yield
    shutdown_code = '''
    # ===== GRACEFUL SHUTDOWN =====
    import signal
    
    async def shutdown_handler(sig, frame):
        """Handle shutdown gracefully"""
        logger.info(f"Received signal {sig}, shutting down...")
        
        # Close database connections
        if db:
            await db.close()
        
        # Cancel reminder scheduler
        from reminders.scheduler import get_scheduler
        scheduler = get_scheduler()
        scheduler.stop()
    
    # Register signal handlers
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown_handler(s, None)))
'''
    
    # Cari posisi setelah yield
    content = content.replace('    yield', '    yield' + shutdown_code)
    
    with open('backend/main.py', 'w') as f:
        f.write(content)
    
    print("✅ main.py fixed!")

if __name__ == "__main__":
    fix_main()
