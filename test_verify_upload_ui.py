import asyncio
from playwright.async_api import async_playwright
import os

async def verify_upload():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False, slow_mo=200)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        print("1. Clicking 'Input Image'...")
        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1500)

        print("2. Clicking 'Inpaint or Outpaint' tab...")
        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1500)

        os.makedirs("temp_inputs", exist_ok=True)
        img_path = os.path.abspath("temp_inputs/test_img.png")
        with open(img_path, "wb") as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')

        print("3. Uploading file via file input...")
        file_input = page.locator("input[type='file']").first
        await file_input.set_input_files(img_path)

        print("4. Dispatching events...")
        await page.evaluate("""() => {
            const fi = document.querySelector("input[type='file']");
            if (fi) {
                fi.dispatchEvent(new Event('change', { bubbles: true }));
                fi.dispatchEvent(new Event('input', { bubbles: true }));
                const dropzone = fi.closest('.wrap, .file-dropzone, div');
                if (dropzone) {
                    dropzone.dispatchEvent(new DragEvent('drop', { bubbles: true }));
                }
            }
        }""")

        await page.wait_for_timeout(3000)

        # Check if an image thumbnail appeared in the dropzone / image container
        thumbnails = await page.locator(".image-container img, .file-dropzone img, .wrap img").count()
        print(f"Thumbnail images found on page: {thumbnails}")

        await page.screenshot(path="upload_verification.png")
        print("Screenshot saved to upload_verification.png")

        await page.wait_for_timeout(5000)
        await b.close()

asyncio.run(verify_upload())
