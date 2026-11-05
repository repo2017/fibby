import subprocess
import time
import os

print("==================================================")
print("       Starting Fibby Studio Full Stack           ")
print("==================================================")

# 1. Start Fooocus
print("[1/3] Starting Fooocus AI Engine (Port 7865)...")
fooocus_proc = subprocess.Popen([
    r"C:\ai\Fooocus_win64_2-5-0\Fooocus_win64_2-5-0\python_embeded\python.exe",
    "-s",
    r"C:\ai\Fooocus_win64_2-5-0\Fooocus_win64_2-5-0\Fooocus\entry_with_update.py"
], cwd=r"C:\ai\Fooocus_win64_2-5-0\Fooocus_win64_2-5-0")

time.sleep(5)

# 2. Start Permanent Tunnel (fibby-worker)
print("[2/3] Starting Permanent Tunnel (https://fibby-worker.loca.lt)...")
tunnel_proc = subprocess.Popen([
    "npx", "-y", "localtunnel", "--port", "8000", "--subdomain", "fibby-worker"
], shell=True)

time.sleep(3)

# 3. Start Fibby Server
print("[3/3] Starting Fibby Backend Server (Port 8000)...")
env = os.environ.copy()
env["PUBLIC_WORKER_URL"] = "https://fibby-worker.loca.lt"
server_proc = subprocess.Popen([
    "python", "server.py"
], cwd=r"C:\ai\focusclient", env=env)

print("\n==================================================")
print("  All Services Started Successfully!              ")
print("  Permanent Tunnel: https://fibby-worker.loca.lt  ")
print("==================================================\n")

try:
    server_proc.wait()
except KeyboardInterrupt:
    fooocus_proc.terminate()
    tunnel_proc.terminate()
    server_proc.terminate()
