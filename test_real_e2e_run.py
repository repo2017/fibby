import requests
from PIL import Image, ImageDraw
import io
import json
import os
import math
import urllib.request

print("--- Step 1: Creating 768x768 base photo with BIG mask area ---")
img_w, img_h = 768, 768
img = Image.new('RGB', (img_w, img_h), color=(30, 20, 50))
draw = ImageDraw.Draw(img)

# Draw a background pattern
draw.rectangle((50, 50, 718, 718), outline=(100, 50, 200), width=10)

# Generate dense stroke points for a BIG 200px circular mask in center
cx, cy = img_w // 2, img_h // 2
mask_radius = 160

# Draw mask on image
draw.ellipse((cx - mask_radius, cy - mask_radius, cx + mask_radius, cy + mask_radius), fill=(230, 40, 40))

img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='PNG')
img_bytes = img_byte_arr.getvalue()

# Create mouse stroke points for Playwright to replay on Fooocus canvas
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
    'canvas_height': str(img_h)
}

print(f"--- Step 2: Testing /api/inpaint (Sending base image & {len(points)} stroke points for BIG mask) ---")
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
                if fsize < 50000:
                    print(f"  [WARNING] File size is suspiciously small: {fsize} bytes")
            else:
                print(f"  [ERROR] Failed to save {out_filename}")

        if len(results) >= 2:
            print(f"\nComparing Variation 1 vs Variation 2 URLs:")
            print(f"  URL 1: {results[0]}")
            print(f"  URL 2: {results[1]}")
            if results[0] != results[1]:
                print("\n[VERIFIED SUCCESS] Both variation URLs are distinct and unique!")
            else:
                print("\n[WARNING] Both URLs in result array are identical.")

except Exception as e:
    import traceback
    print("Test failed with exception:", traceback.format_exc())
