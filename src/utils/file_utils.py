# src/utils/file_utils.py

import os
import json

def load_json(file_path):
    """Tải file JSON từ đường dẫn."""
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(file_path, data):
    """Lưu dữ liệu JSON vào file."""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
