import asyncio
import os, time
from PIL import Image, ImageDraw
import io

print("Creating test flower image...")
img = Image.new('RGB', (512, 512), color=(200, 220, 255))
draw = ImageDraw.Draw(img)
draw.line([(256, 256), (256, 480)], fill=(30, 140, 30), width=12)
draw.ellipse((120, 320, 240, 380), fill=(40, 160, 40)) # Left leaf
draw.ellipse((270, 340, 390, 400), fill=(255, 255, 255)) # Right leaf (mask)
draw.ellipse((196, 196, 316, 316), fill=(230, 50, 80)) # Bloom

buf = io.BytesIO()
img.save(buf, format='PNG')
img_bytes = buf.getvalue()

from fastapi import UploadFile
import server

async def run_flower():
    upload_file = UploadFile(filename="test_flower.png", file=io.BytesIO(img_bytes))
    res = await server.inpaint(image=upload_file, prompt="a bright golden autumn leaf", negative_prompt="blurry")
    print("Result response:", res)

asyncio.run(run_flower())
