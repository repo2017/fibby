import asyncio
from playwright.async_api import async_playwright
import os

async def test_fc():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        os.makedirs("temp_inputs", exist_ok=True)
        img_path = os.path.abspath("temp_inputs/test_img.png")
        with open(img_path, "wb") as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')

        print("Waiting for file chooser...")
        async with page.expect_file_chooser() as fc_info:
            # Click 'Click to Upload' or dropzone area
            await page.locator("text=Click to Upload").first.click()
        file_chooser = await fc_info.value
        await file_chooser.set_files(img_path)

        print("File chooser set files successfully!")
        await page.wait_for_timeout(5000)
        await b.close()

asyncio.run(test_fc())
