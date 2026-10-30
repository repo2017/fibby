import os
from PIL import Image, ImageDraw
import numpy as np

print("Testing mask export logic...")
# 1. Create base image
base = Image.new('RGB', (300, 300), color=(100, 150, 200))
base_path = "temp_inputs/test_base.png"
os.makedirs("temp_inputs", exist_ok=True)
base.save(base_path)

# 2. Simulate user drawing red strokes on top of base image
masked_img = base.copy()
draw = ImageDraw.Draw(masked_img)
draw.ellipse((100, 100, 200, 200), fill=(230, 40, 40)) # Red brush stroke
masked_path = "temp_inputs/test_masked.png"
masked_img.save(masked_path)

# 3. Apply the exact logic from index.html (extracting difference and turning it white)
base_np = np.array(base, dtype=np.int16)
masked_np = np.array(masked_img, dtype=np.int16)

diff = np.abs(masked_np - base_np).sum(axis=2)
mask_indices = diff > 10

# Create export image: base image where mask region is pure white (255, 255, 255)
export_np = np.array(base, dtype=np.uint8)
export_np[mask_indices] = [255, 255, 255]

export_img = Image.fromarray(export_np)
export_path = "temp_inputs/test_export.png"
export_img.save(export_path)

print("Exported image saved to:", export_path)
# Check if pixels in mask region are white
export_px = np.array(export_img)
sample_color = export_px[150, 150]
print("Color at center of mask (should be [255, 255, 255]):", sample_color.tolist())

assert np.all(sample_color == [255, 255, 255]), "Mask export failed!"
print("Mask export verification PASSED successfully!")
