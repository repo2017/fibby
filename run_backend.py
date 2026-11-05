import subprocess
import time
import os
import sys
import threading
import re
import requests

print("==================================================")
print("     Fibby Studio All-In-One Unified Server       ")
print("==================================================")

# 1. Start Fooocus
print("[1/3] Launching Fooocus AI Engine (Port 7865)...")
fooocus_proc = subprocess.Popen([
    r"C:\ai\Fooocus_win64_2-5-0\Fooocus_win64_2-5-0\python_embeded\python.exe",
    "-s",
    r"C:\ai\Fooocus_win64_2-5-0\Fooocus_win64_2-5-0\Fooocus\entry_with_update.py"
], cwd=r"C:\ai\Fooocus_win64_2-5-0\Fooocus_win64_2-5-0")

time.sleep(5)

# 2. Start Cloudflare Tunnel and capture URL dynamically & auto-report to Render
print("[2/3] Launching Cloudflare Tunnel & Auto-Reporting URL...")
tunnel_proc = subprocess.Popen(
    [r"C:\ai\focusclient\cloudflared.exe", "tunnel", "--url", "http://127.0.0.1:8000"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

tunnel_url = None

def monitor_tunnel():
    global tunnel_url
    for line in tunnel_proc.stdout:
        print(f"[Tunnel] {line}", end="")
        match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
        if match and not tunnel_url:
            tunnel_url = match.group(0)
            api_url = f"{tunnel_url}/api/inpaint"
            os.environ["PUBLIC_WORKER_URL"] = tunnel_url
            with open("active_tunnel_url.txt", "w") as f:
                f.write(api_url)

            print(f"\n==================================================")
            print(f"  ACTIVE CLOUDFLARE URL: {tunnel_url}")
            print(f"  Auto-reporting to Render Cloud Controller...")
            print(f"==================================================\n")

            # Auto-report to Render cloud controller
            try:
                resp = requests.post("https://fibby.onrender.com/api/update-worker-url", json={
                    "secret": "fibby_secret_123",
                    "url": api_url
                }, timeout=15)
                print(f"[Auto-Report] Render response: {resp.status_code} {resp.text}")
            except Exception as ex:
                print(f"[Auto-Report Error]: {ex}")

t = threading.Thread(target=monitor_tunnel, daemon=True)
t.start()

# Wait up to 15 seconds for tunnel URL
print("Waiting for Cloudflare tunnel URL assignment...")
for _ in range(15):
    if tunnel_url:
        break
    time.sleep(1)

if not tunnel_url:
    print("Warning: Cloudflare URL took longer than expected, defaulting to localhost...")
    os.environ["PUBLIC_WORKER_URL"] = "http://127.0.0.1:8000"

# 3. Start Fibby FastAPI Server
print("[3/3] Launching Fibby FastAPI Server (Port 8000)...")
os.chdir(r"C:\ai\focusclient")

import uvicorn
from server import app

try:
    uvicorn.run(app, host="127.0.0.1", port=8000)
finally:
    print("Shutting down background services...")
    fooocus_proc.terminate()
    tunnel_proc.terminate()
