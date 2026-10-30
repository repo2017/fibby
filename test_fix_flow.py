import asyncio
from playwright.async_api import async_playwright
import os

async def test():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        # Click Input Image checkbox
        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        # Click Inpaint or Outpaint tab
        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        # Select Method: Modify Content
        print("Selecting Modify Content...")
        method_input = page.locator("label:has-text('Method') input").first
        await method_input.click()
        await method_input.fill("Modify Content")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1000)

        # Upload base image to first file input
        print("Uploading image...")
        os.makedirs("temp_inputs", exist_ok=True)
        img_path = os.path.abspath("temp_inputs/test_img.png")
        with open(img_path, "wb") as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')

        await page.locator("input[type='file']").first.set_input_files(img_path)
        await page.wait_for_timeout(2000)

        print("Test completed successfully!")
        await b.close()

asyncio.run(test())
