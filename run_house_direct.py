import requests
import os
import base64
from PIL import Image, ImageDraw

print("Step 1: Downloading/Preparing house image...")
house_path = os.path.abspath("temp_inputs/house_base.png")

if not os.path.exists(house_path):
    res = requests.get("https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=600&auto=format&fit=crop", timeout=10)
    with open(house_path, "wb") as f:
        f.write(res.content)

# Draw mask over the house area on the image
img = Image.open(house_path).convert('RGB')
draw = ImageDraw.Draw(img)

w, h = img.size
# Draw white mask over the central building
draw.rectangle((w * 0.2, h * 0.2, w * 0.8, h * 0.8), fill=(255, 255, 255))

mask_input_path = os.path.abspath("temp_inputs/house_masked_input.png")
img.save(mask_input_path)
print("Composited house + mask image saved to:", mask_input_path)

print("\nStep 2: Sending request to FastAPI /api/inpaint (Prompt: 'a shiny red luxury sports car')...")
with open(mask_input_path, "rb") as f:
    files = {"image": ("house_masked.png", f, "image/png")}
    data = {
        "prompt": "a shiny red luxury sports car parked on grass",
        "negative_prompt": "blurry, low quality"
    }

    print("Step 3: Waiting for Playwright automation & local Fooocus SDXL model generation (~2 mins)...")
    res = requests.post("http://127.0.0.1:8000/api/inpaint", files=files, data=data, timeout=360)
    print("Response status code:", res.status_code)
    res_json = res.json()
    print("Response payload keys:", res_json.keys() if isinstance(res_json, dict) else type(res_json))

    if res.status_code == 200 and "result" in res_json and len(res_json["result"]) > 0:
        out_url = res_json["result"][0]
        print(f"Step 4: Downloading generated result image from: {out_url[:80]}...")

        if out_url.startswith("data:image"):
            header, b64_str = out_url.split(",", 1)
            img_bytes = base64.b64decode(b64_str)
            with open("house_to_car_final_result.png", "wb") as out_f:
                out_f.write(img_bytes)
        else:
            r = requests.get(out_url)
            if r.status_code == 200:
                with open("house_to_car_final_result.png", "wb") as out_f:
                    out_f.write(r.content)

        print("\nSUCCESS! Saved house-to-car inpainted image to house_to_car_final_result.png!")
