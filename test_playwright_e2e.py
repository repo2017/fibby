import requests
from PIL import Image
import io
import time

print("Creating dummy image and mask for end-to-end test...")
img = Image.new('RGB', (512, 512), color = 'blue')
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='PNG')
img_bytes = img_byte_arr.getvalue()

mask = Image.new('RGB', (512, 512), color = 'black')
mask_byte_arr = io.BytesIO()
mask.save(mask_byte_arr, format='PNG')
mask_bytes = mask_byte_arr.getvalue()

files = {
    'image': ('test_blue.png', img_bytes, 'image/png'),
    'mask': ('test_mask.png', mask_bytes, 'image/png')
}
data = {
    'prompt': 'a cute cat',
    'negative_prompt': 'blurry'
}

print("Testing FastAPI inpaint endpoint with Playwright automation...")
try:
    # Note: Make sure server.py is running or test via TestClient
    from fastapi.testclient import TestClient
    from server import app
    client = TestClient(app)

    response = client.post("/api/inpaint", files=files, data=data)
    print("Response status:", response.status_code)
    print("Response body:", response.json())
except Exception as e:
    print("Test failed with exception:", e)
