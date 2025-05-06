# build_scripts/deploy.py

import os
import shutil
from pathlib import Path
import subprocess

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
ZIP_FILE = DIST_DIR / "shadow_echo_release.zip"
DEPLOY_TARGET = Path("/var/www/shadow_echo/")  # Thay đổi tùy hệ thống của bạn

def deploy_to_localhost():
    if not ZIP_FILE.exists():
        print("❌ Zip package not found. Please run package.py first.")
        return

    if DEPLOY_TARGET.exists():
        print("🧹 Cleaning up old deployment...")
        shutil.rmtree(DEPLOY_TARGET)
    
    DEPLOY_TARGET.mkdir(parents=True, exist_ok=True)

    print("🚚 Extracting package to deployment directory...")
    shutil.unpack_archive(str(ZIP_FILE), str(DEPLOY_TARGET), 'zip')

    print("✅ Deployment complete.")
    print(f"📁 Deployed to: {DEPLOY_TARGET}")

def restart_service(service_name="shadow-echo"):
    print(f"🔁 Restarting service: {service_name}...")
    try:
        subprocess.run(["systemctl", "restart", service_name], check=True)
        print("✅ Service restarted successfully.")
    except subprocess.CalledProcessError:
        print("⚠️ Failed to restart service. Please check manually.")

if __name__ == "__main__":
    deploy_to_localhost()
    restart_service()