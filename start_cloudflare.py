import subprocess
import time
import re

print("==================================================")
print("  Starting Cloudflare Permanent Tunnel (cloudflared)")
print("==================================================")

while True:
    try:
        process = subprocess.Popen(
            [r"C:\ai\focusclient\cloudflared.exe", "tunnel", "--url", "http://127.0.0.1:8000"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        url_found = False
        for line in process.stdout:
            print(line, end="")
            match = re.search(r"https://[a-zA-Z0-9\-]+\.trycloudflare\.com", line)
            if match and not url_found:
                url = match.group(0)
                url_found = True
                api_url = f"{url}/api/inpaint"
                print(f"\n>>> CLOUDFLARE TUNNEL URL: {url} <<<\n")
                with open("active_tunnel_url.txt", "w") as f:
                    f.write(api_url)
                print(f">>> Saved API URL to active_tunnel_url.txt: {api_url} <<<\n")

        process.wait()
    except Exception as e:
        print(f"[Cloudflare Watchdog] Error: {e}")

    print("[Cloudflare Watchdog] Tunnel disconnected. Restarting in 3 seconds...")
    time.sleep(3)
