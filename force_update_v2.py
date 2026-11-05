import requests

print("=== Forcing Tunnel URL Update to Render (v2) ===")
url = "https://fibby.onrender.com/api/update-worker-url"
data = {
    "secret": "fibby_secret_123",
    "url": "https://salvador-knows-bug-females.trycloudflare.com/api/inpaint"
}
try:
    resp = requests.post(url, json=data, timeout=15)
    print("Status:", resp.status_code)
    print("Response:", resp.text)
except Exception as e:
    print("Error:", e)
