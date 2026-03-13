import subprocess
import sys
import os

REQUIREMENTS_FILE = "requirements.txt"

def install():
    if not os.path.exists(REQUIREMENTS_FILE):
        print(f"Error: '{REQUIREMENTS_FILE}' file not found.")
        sys.exit(1)

    print(f"Installing dependencies from '{REQUIREMENTS_FILE}'...\n")

    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", REQUIREMENTS_FILE],
        check=False
    )

    if result.returncode == 0:
        print("\nInstallation completed successfully.")
    else:
        print("\nInstallation failed. See messages above.")
        sys.exit(result.returncode)

if __name__ == "__main__":
    install()