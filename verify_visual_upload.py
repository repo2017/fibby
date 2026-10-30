import asyncio
from playwright.async_api import async_playwright
import os

async def verify():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False, slow_mo=200)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        print("Clicking Input Image...")
        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1500)

        print("Clicking Inpaint or Outpaint...")
        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1500)

        os.makedirs("temp_inputs", exist_ok=True)
        img_path = os.path.abspath("temp_inputs/visual_test.png")
        # Create a distinctive red 100x100 square test image so it's visually obvious
        from PIL import Image
        im = Image.new('RGB', (200, 200), color='red')
        im.save(img_path)

        print("Setting file on file input...")
        file_input = page.locator("input[type='file']").first
        await file_input.set_input_files(img_path)

        print("Dispatching events...")
        await page.evaluate("""() => {
            const fi = document.querySelector("input[type='file']");
            if (fi) {
                fi.dispatchEvent(new Event('change', { bubbles: true }));
                fi.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""")

        await page.wait_for_timeout(3000)

        screenshot_path = os.path.abspath("upload_proof_visual.png")
        await page.screenshot(path=screenshot_path)
        print(f"Visual proof screenshot saved to: {screenshot_path}")

        await page.wait_for_timeout(5000)
        await b.close()

asyncio.run(verify())
