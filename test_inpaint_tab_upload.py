import asyncio
from playwright.async_api import async_playwright
import os

async def test_inpaint_tab():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        print("1. Clicking 'Input Image'...")
        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        print("2. Clicking 'Inpaint or Outpaint' tab...")
        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        # Target file inputs specifically inside #component-70 (Inpaint or Outpaint tab container)
        inpaint_tab = page.locator("#component-70")
        inpaint_file_inputs = inpaint_tab.locator("input[type='file']")

        count = await inpaint_file_inputs.count()
        print("Inpaint tab file inputs count:", count)

        os.makedirs("temp_inputs", exist_ok=True)
        img_path = os.path.abspath("temp_inputs/test_img.png")
        from PIL import Image
        im = Image.new('RGB', (300, 300), color='red')
        im.save(img_path)

        if count > 0:
            print("Uploading image to #component-70 input 0...")
            await inpaint_file_inputs.nth(0).set_input_files(img_path)
            await page.evaluate("""(el) => {
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }""", await inpaint_file_inputs.nth(0).element_handle())

        await page.wait_for_timeout(3000)
        await page.screenshot(path="inpaint_tab_upload_proof.png")
        print("Screenshot saved to inpaint_tab_upload_proof.png")
        await b.close()

asyncio.run(test_inpaint_tab())
