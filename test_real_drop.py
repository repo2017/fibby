import asyncio
from playwright.async_api import async_playwright
import os
import base64

async def test_drop():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        # Create a test red 300x300 image and get its base64 data
        from PIL import Image
        import io
        im = Image.new('RGB', (300, 300), color='red')
        buf = io.BytesIO()
        im.save(buf, format='PNG')
        b64_data = base64.b64encode(buf.getvalue()).decode('utf-8')
        data_url = f"data:image/png;base64,{b64_data}"

        print("Simulating real DragEvent drop on Gradio Image Editor dropzone...")

        success = await page.evaluate("""async (dataUrl) => {
            const res = await fetch(dataUrl);
            const blob = await res.blob();
            const file = new File([blob], 'image.png', { type: 'image/png' });
            const dt = new DataTransfer();
            dt.items.add(file);

            // Find all potential dropzone targets in active tab
            const dropzones = Array.from(document.querySelectorAll('.tabitem:not(.hide) div, .tabitem:not(.hide) label, .tabitem:not(.hide) canvas'));
            let target = dropzones.find(el => el.innerText && el.innerText.includes('Drop Image Here'));
            if (!target) target = document.querySelector('.tabitem:not(.hide)');

            if (target) {
                target.dispatchEvent(new DragEvent('dragenter', { bubbles: true, cancelable: true, dataTransfer: dt }));
                target.dispatchEvent(new DragEvent('dragover', { bubbles: true, cancelable: true, dataTransfer: dt }));
                target.dispatchEvent(new DragEvent('drop', { bubbles: true, cancelable: true, dataTransfer: dt }));
                return true;
            }
            return false;
        }""", data_url)

        print("Drop simulated:", success)
        await page.wait_for_timeout(4000)

        screenshot_path = "real_drop_proof.png"
        await page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
        await b.close()

asyncio.run(test_drop())
