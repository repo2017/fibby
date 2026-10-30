import asyncio
from playwright.async_api import async_playwright
import os

async def test_active():
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
        img_path = os.path.abspath("temp_inputs/visual_test.png")
        from PIL import Image
        im = Image.new('RGB', (200, 200), color='red')
        im.save(img_path)

        # Click "Click to Upload" inside the visible pane
        upload_box = page.locator("text=Click to Upload").first

        async with page.expect_file_chooser() as fc_info:
            await upload_box.click()
        fc = await fc_info.value
        await fc.set_files(img_path)

        print("File chooser uploaded successfully!")
        await page.wait_for_timeout(5000)
        await page.screenshot(path="upload_success_proof.png")
        await b.close()

asyncio.run(test_active())
