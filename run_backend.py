import subprocess
import time
import os
import sys
import threading
import re
import requests
import urllib.request

os.chdir(r"C:\ai\focusclient")
sys.path.insert(0, r"C:\ai\focusclient")

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

time.sleep(6)

# 2. Start FastAPI Server FIRST so port 8000 is listening before tunnel opens
print("[2/3] Launching Fibby FastAPI Server (Port 8000)...")

def run_server():
    import uvicorn
    from server import app
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="warning")

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# Wait until port 8000 is ready
print("Waiting for FastAPI server to bind to port 8000...")
for _ in range(15):
    try:
        r = urllib.request.urlopen("http://127.0.0.1:8000", timeout=2)
        if r.getcode() == 200:
            print("FastAPI server is live on port 8000!")
            break
    except:
        time.sleep(1)

# 3. Start Cloudflare Tunnel AFTER server is running and capture URL dynamically
print("[3/3] Launching Cloudflare Tunnel & Auto-Reporting URL...")
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

# Keep main thread alive
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down background services...")
    fooocus_proc.terminate()
    tunnel_proc.terminate()
