# build_scripts/package.py

import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
ZIP_NAME = "shadow_echo_release.zip"

def package_build():
    if not BUILD_DIR.exists():
        print("❌ Build directory not found. Please run build.py first.")
        return

    DIST_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = DIST_DIR / ZIP_NAME

    print(f"📦 Packaging build into {zip_path}...")
    shutil.make_archive(str(zip_path.with_suffix("")), 'zip', BUILD_DIR)
    print("✅ Packaging complete.")

if __name__ == "__main__":
    package_build()
