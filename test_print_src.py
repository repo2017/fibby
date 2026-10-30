import asyncio
from playwright.async_api import async_playwright
import os

async def print_src():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)
        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        img_path = os.path.abspath("temp_inputs/test_img.png")
        file_input = page.locator("input[type='file']").first
        await file_input.set_input_files(img_path)

        await page.evaluate("""() => {
            const fi = document.querySelector("input[type='file']");
            if (fi) {
                fi.dispatchEvent(new Event('change', { bubbles: true }));
                fi.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""")

        await page.wait_for_timeout(3000)

        imgs = await page.locator("img").all()
        for i, img in enumerate(imgs):
            src = await img.get_attribute("src")
            print(f"Img {i} src: {src[:80] if src else 'None'}")

        await b.close()

asyncio.run(print_src())
