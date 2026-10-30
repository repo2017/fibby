import asyncio
import os
import requests
import numpy as np
from PIL import Image, ImageDraw

print("=" * 60)
print("MASK APPLICATION E2E TEST: Starting...")
print("=" * 60)

# 1. Create a base image (solid light blue background with a green circle in the center)
base_img = Image.new('RGB', (512, 512), color=(100, 150, 220))
draw = ImageDraw.Draw(base_img)
draw.ellipse((200, 200, 312, 312), fill=(0, 200, 0)) # Green circle
base_path = os.path.abspath("temp_inputs/e2e_base.png")
os.makedirs("temp_inputs", exist_ok=True)
base_img.save(base_path)

# 2. Create a separate black & white mask image
mask_img = Image.new('RGB', (512, 512), color=(0, 0, 0))
draw_m = ImageDraw.Draw(mask_img)
draw_m.ellipse((190, 190, 322, 322), fill=(255, 255, 255))
mask_path = os.path.abspath("temp_inputs/e2e_mask.png")
mask_img.save(mask_path)

print("Base image and separate mask images created successfully.")

# 3. Send to FastAPI /api/inpaint endpoint
print("\nSending base image and mask to FastAPI /api/inpaint...")
with open(base_path, "rb") as f_img, open(mask_path, "rb") as f_mask:
    files = {
        "image": ("e2e_base.png", f_img, "image/png"),
        "mask": ("e2e_mask.png", f_mask, "image/png")
    }
    data = {
        "prompt": "a glowing golden coin with intricate details",
        "negative_prompt": "blurry, low quality"
    }

    res = requests.post("http://127.0.0.1:8000/api/inpaint", files=files, data=data, timeout=360)
    print("Response status code:", res.status_code)
    res_json = res.json()
    print("Response payload:", res_json)

    if res.status_code == 200 and "result" in res_json and len(res_json["result"]) > 0:
        out_url = res_json["result"][0]
        print(f"Downloading generated result from: {out_url}")

        if out_url.startswith("http"):
            r = requests.get(out_url)
            if r.status_code == 200:
                with open("e2e_mask_result.png", "wb") as out_f:
                    out_f.write(r.content)
                print("\nSUCCESS! Saved E2E mask result to e2e_mask_result.png!")
        else:
            import base64
            header, b64_str = out_url.split(",", 1)
            with open("e2e_mask_result.png", "wb") as out_f:
                out_f.write(base64.b64decode(b64_str))
            print("\nSUCCESS! Saved E2E mask result to e2e_mask_result.png!")
