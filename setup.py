import os
import sys
import time
import webbrowser
import subprocess
from pathlib import Path
from threading import Thread

ROOT = Path(__file__).resolve().parent
REQS = ROOT / "requirements.txt"
CREATE = ROOT / "scripts" / "createDB.py"
POPULATE = ROOT / "scripts" / "main.py"

HOST = os.getenv("API_HOST", "127.0.0.1")
PORT = os.getenv("API_PORT", "8000")

def step(title):
    print(f"\n=== {title} ===")

def run_or_fail(cmd, cwd=None):
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    print(f"[+] Running: {' '.join(cmd)} (cwd={cwd or os.getcwd()})")
    res = subprocess.run(cmd, cwd=cwd, env=env, text=True)
    if res.returncode != 0:
        raise SystemExit(f"[!] Command failed ({res.returncode}): {' '.join(cmd)}")

def uvicorn_stream():
    env = os.environ.copy()
    env.setdefault("PYTHONIOENCODING", "utf-8")
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", HOST, "--port", PORT, "--reload"]
    print(f"[+] Starting API at http://{HOST}:{PORT}")
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env=env)
    def pipe():
        for line in iter(proc.stdout.readline, ""):
            print(line, end="")
    t = Thread(target=pipe, daemon=True)
    t.start()
    # Probe readiness
    for _ in range(40):
        try:
            import urllib.request
            with urllib.request.urlopen(f"http://{HOST}:{PORT}/", timeout=0.5) as r:
                if r.status == 200:
                    print("[+] API is up.")
                    return proc
        except Exception:
            time.sleep(0.25)
    print("[!] API did not respond yet; continuing.")
    return proc

def main():
    # Sanity checks
    for p, desc in [
        (REQS, "requirements.txt"),
        (CREATE, "scripts/createDB.py"),
        (POPULATE, "scripts/main.py"),
    ]:
        if not p.exists():
            raise SystemExit(f"[!] Missing {desc}: {p}")

    # 1) Install dependencies
    step("Step 1: Install Python dependencies")
    run_or_fail([sys.executable, "-m", "pip", "install", "-r", str(REQS)])

    # 2) Create/refresh schema
    step("Step 2: Create/refresh database schema")
    run_or_fail([sys.executable, str(CREATE)])

    # 3) Insert sample data
    step("Step 3: Insert sample data")
    run_or_fail([sys.executable, str(POPULATE)])

    # 4) Start API and open GUI
    step("Step 4: Start API server")
    proc = uvicorn_stream()

    print("\nAll set. Use Ctrl+C to stop the API.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[+] Stopping API...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    main()
