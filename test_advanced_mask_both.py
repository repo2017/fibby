import asyncio
from playwright.async_api import async_playwright
import os
from PIL import Image, ImageDraw

async def test_both():
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

        # Target input image file input inside active tab (.tabitem:not(.hide))
        active_tab = page.locator(".tabitem:not(.hide)")
        input_fi = active_tab.locator("input[type='file']").first
        await input_fi.set_input_files(base_path)
        await input_fi.evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")

        # Target mask upload file input
        mask_block = page.locator("text=Mask Upload").locator("xpath=ancestor::div[contains(@class, 'block')]").first
        mask_fi = mask_block.locator("input[type='file']").first
        await mask_fi.set_input_files(mask_path)
        await mask_fi.evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")

        print("Both base image and mask uploaded successfully in active tab!")
        await page.wait_for_timeout(4000)
        await page.screenshot(path="advanced_mask_both_perfect.png")
        print("Screenshot saved to advanced_mask_both_perfect.png")
        await b.close()

asyncio.run(test_both())
