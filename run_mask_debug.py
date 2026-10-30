import asyncio
import os, time
from PIL import Image, ImageDraw
import requests, io

base_img = Image.new('RGB', (512, 512), color=(100, 150, 220))
draw = ImageDraw.Draw(base_img)
draw.ellipse((200, 200, 312, 312), fill=(0, 200, 0))

mask_img = Image.new('RGB', (512, 512), color=(0, 0, 0))
draw_m = ImageDraw.Draw(mask_img)
draw_m.ellipse((190, 190, 322, 322), fill=(255, 255, 255))

buf_img = io.BytesIO()
base_img.save(buf_img, format='PNG')
img_bytes = buf_img.getvalue()

buf_mask = io.BytesIO()
mask_img.save(buf_mask, format='PNG')
mask_bytes = buf_mask.getvalue()

from fastapi import UploadFile
import server

async def run_dbg():
    u_img = UploadFile(filename="base.png", file=io.BytesIO(img_bytes))
    u_mask = UploadFile(filename="mask.png", file=io.BytesIO(mask_bytes))
    print("Executing server.inpaint()...")
    res = await server.inpaint(image=u_img, mask=u_mask, prompt="a glowing golden coin", negative_prompt="blurry")
    print("Result response body:", res)

asyncio.run(run_dbg())
