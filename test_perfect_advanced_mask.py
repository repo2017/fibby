import asyncio
from playwright.async_api import async_playwright
import os
from PIL import Image, ImageDraw

async def test_perfect():
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

        # Base image: blue square
        img = Image.new('RGB', (512, 512), color=(100, 150, 220))
        img.save(base_path)

        # Mask image: black background with white circle
        mask = Image.new('RGB', (512, 512), color=(0, 0, 0))
        draw = ImageDraw.Draw(mask)
        draw.ellipse((200, 200, 300, 300), fill=(255, 255, 255))
        mask.save(mask_path)

        file_inputs = await page.locator("input[type='file']").all()
        print("Total file inputs:", len(file_inputs))

        if len(file_inputs) > 5:
            await file_inputs[5].set_input_files(base_path)
            await file_inputs[5].evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")
            print("Set base image on file input 5")

        if len(file_inputs) > 7:
            await file_inputs[7].set_input_files(mask_path)
            await file_inputs[7].evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")
            print("Set mask image on file input 7")

        await page.wait_for_timeout(4000)
        await page.screenshot(path="advanced_mask_both_rendered.png")
        print("Screenshot saved to advanced_mask_both_rendered.png")
        await b.close()

asyncio.run(test_perfect())
