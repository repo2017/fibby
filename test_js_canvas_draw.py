import asyncio
from playwright.async_api import async_playwright
import os
import base64
from PIL import Image, ImageDraw
import io

async def test_js():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)
        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        # Upload base image
        os.makedirs("temp_inputs", exist_ok=True)
        base_path = os.path.abspath("temp_inputs/js_base.png")
        img = Image.new('RGB', (512, 512), color=(100, 150, 220))
        img.save(base_path)

        inpaint_tab = page.locator("#component-70")
        fi = inpaint_tab.locator("input[type='file']").first
        await fi.set_input_files(base_path)
        await fi.evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")
        await page.wait_for_timeout(3000)

        # Create a test mask image with a specific shape (e.g. a star or circle)
        mask = Image.new('RGBA', (512, 512), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(mask)
        draw.ellipse((150, 150, 350, 350), fill=(230, 40, 40, 180)) # Red mask circle
        buf = io.BytesIO()
        mask.save(buf, format='PNG')
        mask_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        mask_data_url = f"data:image/png;base64,{mask_b64}"

        print("Injecting mask directly into Fooocus canvas via JS...")
        await page.evaluate("""async (maskDataUrl) => {
            const canvas = document.querySelector("#component-70 canvas");
            if (!canvas) return;
            const ctx = canvas.getContext('2d');

            const img = new Image();
            img.src = maskDataUrl;
            await new Promise((resolve) => { img.onload = resolve; });

            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

            canvas.dispatchEvent(new Event('change', { bubbles: true }));
            canvas.dispatchEvent(new Event('input', { bubbles: true }));
        }""", mask_data_url)

        print("Mask injected successfully via JS!")
        await page.wait_for_timeout(3000)
        await page.screenshot(path="js_canvas_injected_proof.png")
        print("Screenshot saved to js_canvas_injected_proof.png")
        await b.close()

asyncio.run(test_js())
