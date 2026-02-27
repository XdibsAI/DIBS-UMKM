import os
import base64
from pathlib import Path

def get_image_data(file_path: str):
    """Mengonversi file gambar ke base64 agar bisa dibaca model AI"""
    if not os.path.exists(file_path):
        return None
    
    with open(file_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def list_uploaded_files(directory="uploads"):
    """List semua file yang diupload user"""
    path = Path(directory)
    if not path.exists():
        return []
    return [f.name for f in path.iterdir() if f.is_file()]
