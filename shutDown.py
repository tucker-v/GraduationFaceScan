import os
import sys
import subprocess
from pathlib import Path

SCRIPT = Path("scripts") / "dropDB.py"

def main():
    if not SCRIPT.exists():
        print(f"[!] Missing script: {SCRIPT.resolve()}")
        sys.exit(1)

    print("WARNING: This will DROP the database configured in db_config.json.")
    confirm = input("Type 'DROP' to continue: ").strip()
    if confirm != "DROP":
        print("[i] Aborted.")
        return

    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")

    print(f"[+] Running: {sys.executable} {SCRIPT}")
    proc = subprocess.run([sys.executable, str(SCRIPT)], env=env, text=True)

    if proc.returncode == 0:
        print("[+] Database dropped successfully.")
    else:
        print(f"[!] dropDB.py failed with code {proc.returncode}")
        sys.exit(proc.returncode)

if __name__ == "__main__":
    main()
