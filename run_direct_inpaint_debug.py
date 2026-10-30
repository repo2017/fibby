import asyncio
import os, time
from PIL import Image, ImageDraw
import io

print("Testing inpaint function execution directly...")

# Create test flower image
img = Image.new('RGB', (512, 512), color=(200, 220, 255))
draw = ImageDraw.Draw(img)
draw.line([(256, 256), (256, 480)], fill=(30, 140, 30), width=12)
draw.ellipse((120, 320, 240, 380), fill=(40, 160, 40))
draw.ellipse((270, 340, 390, 400), fill=(255, 255, 255))

buf = io.BytesIO()
img.save(buf, format='PNG')
img_bytes = buf.getvalue()

from fastapi import UploadFile
import server

async def run_direct():
    upload_file = UploadFile(filename="flower_direct.png", file=io.BytesIO(img_bytes))
    res = await server.inpaint(image=upload_file, prompt="a golden yellow leaf", negative_prompt="blurry")
    print("Result response:", res)

asyncio.run(run_direct())
