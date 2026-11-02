import requests
from PIL import Image
import io
import time
import json

print("--- Testing Live Render v1.4.0 E2E ---")

reg_url = "https://fibby.onrender.com/api/register"
res = requests.post(reg_url, json={"email": "v140test@example.com", "password": "password123"})
token = None
if res.status_code == 200:
    token = res.json().get("token")
    print("Registered test user. Token:", token)
else:
    login_url = "https://fibby.onrender.com/api/login"
    login_res = requests.post(login_url, json={"email": "v140test@example.com", "password": "password123"})
    token = login_res.json().get("token")
    print("Logged in test user. Token:", token)

img = Image.new("RGB", (3000, 2000), color=(50, 100, 200))
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format="PNG")
img_bytes = img_byte_arr.getvalue()

inpaint_url = "https://fibby.onrender.com/api/inpaint"
files = {"image": ("highres_test.png", img_bytes, "image/png")}
data = {
    "prompt": "a glowing yellow star",
    "image_count": "2",
    "auth_token": token,
    "mask_points": json.dumps([{"x": 1500, "y": 1000, "type": "down"}, {"x": 1600, "y": 1100, "type": "move"}, {"type": "up"}]),
    "canvas_width": "3000",
    "canvas_height": "2000",
    "brush_size": "297"
}

print("Sending high-res inpaint request to Render...")
try:
    resp = requests.post(inpaint_url, files=files, data=data, timeout=60)
    print("Response Status Code:", resp.status_code)
    print("Response Body:", resp.text)

    if resp.status_code == 200:
        job_id = resp.json().get("job_id")
        if job_id:
            print("Polling job status...")
            for i in range(10):
                time.sleep(4)
                status_res = requests.get(f"https://fibby.onrender.com/api/job-status?job_id={job_id}")
                print(f"Poll {i+1}:", status_res.status_code, status_res.text)
                if "completed" in status_res.text or "error" in status_res.text:
                    break
except Exception as e:
    print("Request failed:", e)
