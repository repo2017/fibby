import requests
from PIL import Image
import io
import json
import time

print("=== Running Live App End-to-End Test (v1.9.2) ===")

# 1. Register or login
reg_url = "https://fibby.onrender.com/api/register"
res = requests.post(reg_url, json={"email": "e2etest_v192@example.com", "password": "password123"})
token = None
if res.status_code == 200:
    token = res.json().get("token")
    print("Registered test user. Token:", token)
else:
    login_url = "https://fibby.onrender.com/api/login"
    login_res = requests.post(login_url, json={"email": "e2etest_v192@example.com", "password": "password123"})
    token = login_res.json().get("token")
    print("Logged in test user. Token:", token)

# 2. Create test image
img = Image.new("RGB", (1024, 1024), color=(60, 120, 220))
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format="PNG")
img_bytes = img_byte_arr.getvalue()

# 3. Test /api/inpaint
inpaint_url = "https://fibby.onrender.com/api/inpaint"
files = {"image": ("test_v192.png", img_bytes, "image/png")}
data = {
    "prompt": "a glowing neon cyber helmet",
    "image_count": "2",
    "auth_token": token,
    "mask_points": json.dumps([{"x": 512, "y": 512, "type": "down"}, {"x": 600, "y": 600, "type": "move"}, {"type": "up"}]),
    "canvas_width": "1024",
    "canvas_height": "1024",
    "disp_width": "350",
    "brush_size": "35"
}

print("Sending inpaint request to https://fibby.onrender.com/api/inpaint...")
resp = requests.post(inpaint_url, files=files, data=data, timeout=60)
print("Response Status Code:", resp.status_code)
print("Response Body:", resp.text)

if resp.status_code == 200:
    job_id = resp.json().get("job_id")
    if job_id:
        print(f"Job dispatched successfully! Job ID: {job_id}")
        print("Polling job status...")
        for i in range(15):
            time.sleep(4)
            status_res = requests.get(f"https://fibby.onrender.com/api/job-status?job_id={job_id}")
            print(f"Poll {i+1}:", status_res.status_code, status_res.text)
            if "completed" in status_res.text or "error" in status_res.text:
                break
else:
    print("Inpaint dispatch failed!")
