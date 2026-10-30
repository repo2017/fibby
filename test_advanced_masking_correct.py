import asyncio
from playwright.async_api import async_playwright
import os
from PIL import Image, ImageDraw

async def test_adv_correct():
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

        file_inputs = await page.locator("input[type='file']").all()
        print("Total file inputs on page:", len(file_inputs))

        # Let's find file inputs inside #component-70 or active tab
        active_file_inputs = await page.locator(".tabitem:not(.hide) input[type='file']").all()
        print("File inputs in active tab:", len(active_file_inputs))

        if len(active_file_inputs) >= 2:
            await active_file_inputs[0].set_input_files(base_path)
            await active_file_inputs[1].set_input_files(mask_path)
            for fi in active_file_inputs[:2]:
                await fi.evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")

        await page.wait_for_timeout(3000)
        await page.screenshot(path="advanced_mask_success.png")
        print("Screenshot saved to advanced_mask_success.png")
        await b.close()

asyncio.run(test_adv_correct())
