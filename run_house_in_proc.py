import asyncio
import os, time
from PIL import Image, ImageDraw
import requests, io

print("Step 1: Downloading real house photo...")
house_path = os.path.abspath("temp_inputs/house_real.png")

res = requests.get("https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=600&auto=format&fit=crop", timeout=10)
with open(house_path, "wb") as f:
    f.write(res.content)

img = Image.open(house_path).convert('RGB')
draw = ImageDraw.Draw(img)
w, h = img.size
# Draw white mask over central building
draw.rectangle((w * 0.2, h * 0.2, w * 0.8, h * 0.8), fill=(255, 255, 255))

buf = io.BytesIO()
img.save(buf, format='PNG')
img_bytes = buf.getvalue()

from fastapi import UploadFile
import server

async def run_in_proc():
    upload_file = UploadFile(filename="house_inproc.png", file=io.BytesIO(img_bytes))
    print("\nStep 2: Executing server.inpaint()...")
    res = await server.inpaint(image=upload_file, prompt="a shiny red luxury sports car parked on grass", negative_prompt="blurry")
    print("\nStep 3: Response object:", res.body.decode('utf-8')[:300])

asyncio.run(run_in_proc())
