import asyncio
from playwright.async_api import async_playwright

async def run_test():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        # 1. Click Input Image checkbox
        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        # 2. Click Inpaint or Outpaint tab
        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        # 3. Set files on file inputs
        file_inputs = page.locator("input[type='file']")
        count = await file_inputs.count()
        print(f"Found {count} file inputs")

        # Inpaint image is usually one of the active file inputs
        # Let's set file on input 6 and 7 (or iterate/try)
        if count > 6:
            await file_inputs.nth(6).set_input_files("temp_inputs/img_test.png")
        if count > 7:
            await file_inputs.nth(7).set_input_files("temp_inputs/mask_test.png")

        await page.wait_for_timeout(2000)

        # 4. Fill prompt
        await page.locator("textarea").first.fill("a futuristic robot")

        # 5. Click Generate
        await page.locator("#generate_button").click()
        print("Clicked generate, waiting for image...")

        # Wait for result image
        try:
            await page.wait_for_selector("img[src*='file='], .gallery img", timeout=60000)
            print("Generation success!")
            img = page.locator("img[src*='file='], .gallery img").last
            print("Result src:", await img.get_attribute("src"))
        except Exception as e:
            print("Timed out waiting for result:", e)

        await page.wait_for_timeout(5000)
        await b.close()

if __name__ == "__main__":
    import os
    os.makedirs("temp_inputs", exist_ok=True)
    with open("temp_inputs/img_test.png", "wb") as f:
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
    with open("temp_inputs/mask_test.png", "wb") as f:
        f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')

    asyncio.run(run_test())
