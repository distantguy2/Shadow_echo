# build_scripts/build.py

import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = PROJECT_ROOT / "build"

def clean_build():
    if BUILD_DIR.exists():
        print("🧹 Cleaning previous build...")
        shutil.rmtree(BUILD_DIR)
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    print("✅ Clean build directory created.")

def copy_source():
    print("📁 Copying source files...")
    folders_to_copy = ["src", "config", "assets", "data", "docs"]
    for folder in folders_to_copy:
        src_path = PROJECT_ROOT / folder
        dst_path = BUILD_DIR / folder
        if src_path.exists():
            shutil.copytree(src_path, dst_path)
    print("✅ Source files copied.")

def copy_core_files():
    print("📦 Copying core files...")
    core_files = ["main.py", "requirements.txt", "README.md"]
    for file in core_files:
        src = PROJECT_ROOT / file
        if src.exists():
            shutil.copy(src, BUILD_DIR / file)
    print("✅ Core files copied.")

def build_game_package():
    clean_build()
    copy_source()
    copy_core_files()
    print(f"🎮 Build completed at: {BUILD_DIR}")

if __name__ == "__main__":
    build_game_package()
