import asyncio
from playwright.async_api import async_playwright
import os

async def test_img_input():
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

        file_inputs = await page.locator(".tabitem:not(.hide) input[type='file']").all()
        print("File inputs in active tab:", len(file_inputs))

        if len(file_inputs) > 0:
            await file_inputs[0].set_input_files(img_path)
            await page.evaluate("""() => {
                const fi = document.querySelector(".tabitem:not(.hide) input[type='file']");
                if (fi) {
                    fi.dispatchEvent(new Event('change', { bubbles: true }));
                    fi.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }""")
            print("Set files on active tab file input 0")

        await page.wait_for_timeout(5000)
        await page.screenshot(path="upload_active_tab_proof.png")
        await b.close()

asyncio.run(test_img_input())
