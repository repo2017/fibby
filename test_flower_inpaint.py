import asyncio
import os
import requests
import base64
from PIL import Image, ImageDraw

print("1. Generating test flower image with green leaves...")
# Create a 512x512 photo with a light blue background, stem, flower bloom, and green leaves
img = Image.new('RGB', (512, 512), color=(200, 220, 255))
draw = ImageDraw.Draw(img)

# Stem & Green Leaves
draw.line([(256, 256), (256, 480)], fill=(30, 140, 30), width=12)
draw.ellipse((120, 320, 240, 380), fill=(40, 160, 40)) # Left leaf
draw.ellipse((270, 340, 390, 400), fill=(40, 160, 40)) # Right leaf

# Flower Petals
draw.ellipse((196, 196, 316, 316), fill=(230, 50, 80)) # Center bloom

# Paint white mask on the right leaf on the image
draw.ellipse((270, 340, 390, 400), fill=(255, 255, 255)) # White mask on right leaf

# Save test flower image
flower_path = os.path.abspath("test_flower.png")
img.save(flower_path)

print("2. Sending request to FastAPI /api/inpaint endpoint...")
with open(flower_path, "rb") as f:
    files = {"image": ("test_flower.png", f, "image/png")}
    data = {
        "prompt": "a bright golden yellow autumn leaf",
        "negative_prompt": "blurry, low quality"
    }

    print("3. Executing full Playwright generation flow (waiting ~2 minutes for local GPU)...")
    res = requests.post("http://127.0.0.1:8000/api/inpaint", files=files, data=data, timeout=360)
    print("Response status code:", res.status_code)
    res_json = res.json()

    if res.status_code == 200 and "result" in res_json and len(res_json["result"]) > 0:
        output_url = res_json["result"][0]
        print("4. Saving generated result...")

        if output_url.startswith("data:image"):
            # Base64 data URI
            header, b64_str = output_url.split(",", 1)
            img_bytes = base64.b64decode(b64_str)
            with open("flower_result.png", "wb") as out_f:
                out_f.write(img_bytes)
            print("Successfully saved generated result to flower_result.png!")
        else:
            img_res = requests.get(output_url)
            if img_res.status_code == 200:
                with open("flower_result.png", "wb") as out_f:
                    out_f.write(img_res.content)
                print("Successfully saved generated result to flower_result.png!")
