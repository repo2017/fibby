import subprocess
import time

print("==================================================")
print("  Fibby Permanent Tunnel Watchdog (fibby-worker)")
print("==================================================")

while True:
    try:
        print("[Tunnel Watchdog] Starting localtunnel on port 8000...")
        process = subprocess.Popen(["npx", "-y", "localtunnel", "--port", "8000", "--subdomain", "fibby-worker"], shell=True)
        process.wait()
    except Exception as e:
        print(f"[Tunnel Watchdog] Error: {e}")
    print("[Tunnel Watchdog] Tunnel disconnected. Auto-restarting in 3 seconds...")
    time.sleep(3)
