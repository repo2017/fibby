import asyncio
from playwright.async_api import async_playwright
import os
from PIL import Image, ImageDraw

async def test_adv_mask():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False, slow_mo=100)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        print("1. Enabling Input Image...")
        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        print("2. Clicking Inpaint or Outpaint...")
        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        print("3. Enabling 'Enable Advanced Masking Features'...")
        adv_cb = page.locator("text=Enable Advanced Masking Features").locator("input[type='checkbox']")
        if await adv_cb.count() > 0 and not await adv_cb.is_checked():
            await adv_cb.click()
            await page.wait_for_timeout(1500)

        print("4. Creating test base image and separate mask image...")
        os.makedirs("temp_inputs", exist_ok=True)
        base_path = os.path.abspath("temp_inputs/adv_base.png")
        mask_path = os.path.abspath("temp_inputs/adv_mask.png")

        # Base image: blue square with green circle
        base_img = Image.new('RGB', (512, 512), color=(100, 150, 220))
        draw = ImageDraw.Draw(base_img)
        draw.ellipse((200, 200, 312, 312), fill=(0, 200, 0))
        base_img.save(base_path)

        # Mask image: black background with white circle over the green circle
        mask_img = Image.new('RGB', (512, 512), color=(0, 0, 0))
        draw_m = ImageDraw.Draw(mask_img)
        draw_m.ellipse((190, 190, 322, 322), fill=(255, 255, 255))
        mask_img.save(mask_path)

        print("5. Finding file inputs...")
        file_inputs = await page.locator("input[type='file']").all()
        print(f"Total file inputs found: {len(file_inputs)}")

        # Upload base image and mask to respective slots
        # In Advanced Masking, input image is usually first, mask upload is second or third
        if len(file_inputs) > 6:
            print("Uploading base image to file input 6...")
            await file_inputs[6].set_input_files(base_path)
        if len(file_inputs) > 7:
            print("Uploading mask image to file input 7...")
            await file_inputs[7].set_input_files(mask_path)

        await page.wait_for_timeout(3000)
        await page.screenshot(path="advanced_mask_upload_proof.png")
        print("Screenshot saved to advanced_mask_upload_proof.png")

        await b.close()

asyncio.run(test_adv_mask())
