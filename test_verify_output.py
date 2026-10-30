import asyncio
from playwright.async_api import async_playwright
import os

async def verify():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        file_inputs = page.locator("input[type='file']")

        os.makedirs("temp_inputs", exist_ok=True)
        with open("temp_inputs/img_test.png", "wb") as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')
        with open("temp_inputs/mask_test.png", "wb") as f:
            f.write(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82')

        await file_inputs.nth(6).set_input_files("temp_inputs/img_test.png")
        await file_inputs.nth(7).set_input_files("temp_inputs/mask_test.png")
        await page.wait_for_timeout(2000)

        await page.locator("textarea").first.fill("a majestic lion")
        await page.locator("#generate_button").click()

        print("Clicked generate. Monitoring image sources...")
        for t in range(20):
            await page.wait_for_timeout(3000)
            imgs = await page.locator("img").all()
            print(f"--- Poll {t} ---")
            for idx, img in enumerate(imgs):
                src = await img.get_attribute("src")
                if src and "svg" not in src and "logo" not in src:
                    print(f"  img {idx}: {src}")

        await b.close()

asyncio.run(verify())
