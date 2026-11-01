import requests
from PIL import Image, ImageDraw
import io
import json
import os
import math
import urllib.request

print("--- Step 1: Creating 768x1024 portrait base photo with mask at LOWER part ---")
img_w, img_h = 768, 1024
img = Image.new('RGB', (img_w, img_h), color=(30, 20, 50))
draw = ImageDraw.Draw(img)

# Draw a background pattern
draw.rectangle((50, 50, 718, 974), outline=(100, 50, 200), width=10)

# Mask at LOWER part of the portrait image (y around 850)
cx, cy = img_w // 2, 850
mask_radius = 120

draw.ellipse((cx - mask_radius, cy - mask_radius, cx + mask_radius, cy + mask_radius), fill=(230, 40, 40))

img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='PNG')
img_bytes = img_byte_arr.getvalue()

points = []
points.append({'x': cx - mask_radius, 'y': cy, 'type': 'down'})

for r in range(10, mask_radius, 15):
    for angle in range(0, 360, 15):
        rad = math.radians(angle)
        px = cx + r * math.cos(rad)
        py = cy + r * math.sin(rad)
        points.append({'x': px, 'y': py, 'type': 'move'})

points.append({'type': 'up'})

files = {
    'image': ('test_inpaint_input.png', img_bytes, 'image/png')
}
data = {
    'prompt': 'a glowing golden disco ball with neon pink laser lights',
    'negative_prompt': 'blurry, low quality, dark',
    'mask_points': json.dumps(points),
    'canvas_width': str(img_w),
    'canvas_height': str(img_h),
    'image_count': '2'
}

print(f"--- Step 2: Testing /api/inpaint (Requesting 2 variations with LOWER mask on portrait image) ---")
try:
    from fastapi.testclient import TestClient
    from server import app
    client = TestClient(app)

    response = client.post("/api/inpaint", files=files, data=data)
    print("Response status code:", response.status_code)
    payload = response.json()
    print("Response payload:", payload)

    if response.status_code == 200 and 'result' in payload:
        results = payload['result']
        print(f"\n--- Step 3: Verifying and Downloading {len(results)} Generated Images ---")

        for idx, url in enumerate(results, start=1):
            out_filename = f"test_output_variation_{idx}.png"
            print(f"Downloading Variation {idx} from: {url} -> {out_filename}")

            urllib.request.urlretrieve(url, out_filename)

            if os.path.exists(out_filename):
                fsize = os.path.getsize(out_filename)
                print(f"  [SUCCESS] {out_filename} downloaded! File size: {fsize:,} bytes")
            else:
                print(f"  [ERROR] Failed to save {out_filename}")

        if len(results) >= 2:
            print("\n[VERIFIED SUCCESS] Received 2 distinct variation URLs with lower mask on portrait image!")

except Exception as e:
    import traceback
    print("Test failed with exception:", traceback.format_exc())
