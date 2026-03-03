#!/usr/bin/env python3
"""
Cek semua fungsi di screens/projects
"""
import os
import re

def extract_functions(content):
    """Ekstrak fungsi dari file dart"""
    patterns = [
        r'(Future<.*?>|void|String|int|bool|dynamic)\s+(\w+)\s*\([^)]*\)\s*{',
        r'@override\s+\w+\s+(\w+)\s*\(',
        r'initState\s*\(',
        r'build\s*\(',
        r'dispose\s*\('
    ]
    
    functions = []
    for pattern in patterns:
        matches = re.findall(pattern, content)
        functions.extend(matches)
    return functions

def check_projects_screen():
    projects_dir = "lib/screens/projects"
    
    if not os.path.exists(projects_dir):
        print(f"❌ Folder {projects_dir} tidak ditemukan")
        return
    
    print("="*60)
    print("📁 FUNGSI DI SCREENS/PROJECTS")
    print("="*60)
    
    for root, dirs, files in os.walk(projects_dir):
        for file in files:
            if file.endswith('.dart'):
                filepath = os.path.join(root, file)
                relpath = os.path.relpath(filepath)
                
                with open(filepath, 'r') as f:
                    content = f.read()
                
                functions = extract_functions(content)
                
                if functions:
                    print(f"\n📄 {relpath}")
                    print("-" * 40)
                    for func in functions:
                        if isinstance(func, tuple):
                            print(f"  🔹 {func[0]} {func[1]}")
                        else:
                            print(f"  🔹 {func}")

if __name__ == "__main__":
    check_projects_screen()
