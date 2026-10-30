import requests
from PIL import Image, ImageDraw
import io

print("Creating a test photo with a drawn mask area...")
# Create a 512x512 photo (blue background with a red square)
img = Image.new('RGB', (512, 512), color = (50, 100, 200))
draw = ImageDraw.Draw(img)
# Draw white mask stroke in center
draw.ellipse((200, 200, 300, 300), fill=(255, 255, 255))

img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='PNG')
img_bytes = img_byte_arr.getvalue()

files = {
    'image': ('test_inpaint_input.png', img_bytes, 'image/png')
}
data = {
    'prompt': 'a glowing yellow star',
    'negative_prompt': 'blurry, low quality'
}

print("Testing /api/inpaint against server...")
try:
    from fastapi.testclient import TestClient
    from server import app
    client = TestClient(app)

    response = client.post("/api/inpaint", files=files, data=data)
    print("Response status code:", response.status_code)
    print("Response payload:", response.json())
except Exception as e:
    print("Test failed with exception:", e)
