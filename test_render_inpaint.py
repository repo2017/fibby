import requests
from PIL import Image
import io
import time

print("Waiting 120 seconds for Render to finish deploying...")
time.sleep(120)

print("1. Logging in / registering on live Render app...")
url_reg = 'https://fibby.onrender.com/api/register'
reg_res = requests.post(url_reg, json={'email': 'autotest@example.com', 'password': 'password123'})
token = None
if reg_res.status_code == 200:
    token = reg_res.json().get('token')
    print("Registered successfully. Token:", token)
else:
    url_login = 'https://fibby.onrender.com/api/login'
    login_res = requests.post(url_login, json={'email': 'autotest@example.com', 'password': 'password123'})
    token = login_res.json().get('token')
    print("LoggedIn successfully. Token:", token)

print("2. Testing /api/inpaint on live Render app...")
img = Image.new('RGB', (512, 512), color=(50, 100, 200))
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='PNG')
img_bytes = img_byte_arr.getvalue()

url_inpaint = 'https://fibby.onrender.com/api/inpaint'
files = {'image': ('test.png', img_bytes, 'image/png')}
data = {
    'prompt': 'a glowing yellow star',
    'image_count': '2',
    'auth_token': token,
    'mask_points': '[]',
    'canvas_width': '512',
    'canvas_height': '512'
}

try:
    res = requests.post(url_inpaint, files=files, data=data, timeout=300)
    print('Inpaint Status:', res.status_code)
    print('Inpaint Response Body:', res.text)
except Exception as e:
    print('Inpaint Error:', e)
