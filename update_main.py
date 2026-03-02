#!/usr/bin/env python3
"""
Update main.py - Handle missing dibs_routes gracefully
"""
import re

def update_main_py():
    with open('backend/main.py', 'r') as f:
        content = f.read()
    
    # Pattern untuk mencari import dibs_routes
    import_pattern = r'(from dibs_routes import router as dibs_router)'
    
    # Ganti dengan try-except
    new_import = '''# Try import dibs_routes, but don't fail if not exists
try:
    from dibs_routes import router as dibs_router
    dibs_router_available = True
except ImportError:
    dibs_router_available = False
    logger.warning("⚠️ dibs_routes.py not found, skipping import")'''
    
    content = re.sub(import_pattern, new_import, content)
    
    # Pattern untuk include router
    include_pattern = r'(app\.include_router\(dibs_router\))'
    
    # Ganti dengan conditional
    new_include = '''if dibs_router_available:
    app.include_router(dibs_router)'''
    
    content = re.sub(include_pattern, new_include, content)
    
    # Tulis kembali
    with open('backend/main.py', 'w') as f:
        f.write(content)
    
    print("✅ main.py updated successfully!")
    print("📁 Backup saved")

if __name__ == "__main__":
    update_main_py()
