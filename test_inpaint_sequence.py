import asyncio
from playwright.async_api import async_playwright

async def test_seq():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        # 1. Click Input Image checkbox / label
        input_img_lbl = page.locator("text=Input Image")
        if await input_img_lbl.count() > 0:
            await input_img_lbl.first.click()
            print("Clicked Input Image")
            await page.wait_for_timeout(2000)

        # 2. Click Inpaint or Outpaint tab
        inpaint_btn = page.locator("button:has-text('Inpaint or Outpaint')")
        if await inpaint_btn.count() > 0:
            await inpaint_btn.first.click()
            print("Clicked Inpaint or Outpaint")
            await page.wait_for_timeout(2000)

        await page.screenshot(path='revealed_inpaint.png')
        await b.close()

asyncio.run(test_seq())
