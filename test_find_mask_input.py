import asyncio
from playwright.async_api import async_playwright

async def test_find():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)
        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        await page.locator("text=Enable Advanced Masking Features").click()
        await page.wait_for_timeout(1500)

        # Find file input inside Mask Upload block
        mask_block = page.locator("text=Mask Upload").locator("xpath=ancestor::div[contains(@class, 'block')]").first
        mask_fi = mask_block.locator("input[type='file']").first
        print("Found mask file input inside Mask Upload block:", await mask_fi.count())

        input_block = page.locator(".image-container").first
        input_fi = input_block.locator("input[type='file']").first
        print("Found input image file input:", await input_fi.count())

        await b.close()

asyncio.run(test_find())
