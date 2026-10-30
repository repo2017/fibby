import asyncio
from playwright.async_api import async_playwright
import os
from PIL import Image, ImageDraw

async def test_upload():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)
        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        # Click 'Enable Advanced Masking Features'
        await page.locator("text=Enable Advanced Masking Features").click()
        await page.wait_for_timeout(1500)

        os.makedirs("temp_inputs", exist_ok=True)
        base_path = os.path.abspath("temp_inputs/adv_base.png")
        mask_path = os.path.abspath("temp_inputs/adv_mask.png")

        img = Image.new('RGB', (512, 512), color=(100, 150, 220))
        img.save(base_path)

        mask = Image.new('RGB', (512, 512), color=(0, 0, 0))
        draw = ImageDraw.Draw(mask)
        draw.ellipse((200, 200, 300, 300), fill=(255, 255, 255))
        mask.save(mask_path)

        # Find all file inputs on page when advanced masking is active
        file_inputs = await page.locator("input[type='file']").all()
        print("Total file inputs:", len(file_inputs))

        # Fooocus in advanced masking has input image file input and mask upload file input
        # Let's find which inputs are inside the inpaint tab
        # Typically, when advanced masking is checked, file_inputs[6] is base image and file_inputs[7] is mask upload (or similar)
        # Let's test setting files on inputs 6 and 7, and dispatching change/input events
        if len(file_inputs) > 6:
            await file_inputs[6].set_input_files(base_path)
            await file_inputs[6].evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")
            print("Set base image on file input 6")

        if len(file_inputs) > 7:
            await file_inputs[7].set_input_files(mask_path)
            await file_inputs[7].evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")
            print("Set mask image on file input 7")

        await page.wait_for_timeout(4000)
        await page.screenshot(path="advanced_mask_thumbnails_proof.png")
        print("Screenshot saved to advanced_mask_thumbnails_proof.png")

        await b.close()

asyncio.run(test_upload())
