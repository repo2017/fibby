from fastapi.testclient import TestClient
from server import app
from PIL import Image
import io
import os

client = TestClient(app)

# Create dummy test image and mask bytes
img = Image.new('RGB', (512, 512), color = 'red')
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='PNG')
img_bytes = img_byte_arr.getvalue()

mask = Image.new('RGB', (512, 512), color = 'black')
mask_byte_arr = io.BytesIO()
mask.save(mask_byte_arr, format='PNG')
mask_bytes = mask_byte_arr.getvalue()

print("Testing FastAPI /api/inpaint endpoint with TestClient...")
files = {
    'image': ('test_img.png', img_bytes, 'image/png'),
    'mask': ('test_mask.png', mask_bytes, 'image/png')
}
data = {
    'prompt': 'a beautiful landscape',
    'negative_prompt': 'blurry'
}

response = client.post("/api/inpaint", files=files, data=data)
print("Response status code:", response.status_code)
print("Response JSON:", response.json())
