import asyncio
from playwright.async_api import async_playwright

async def test_files():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        inpaint_btn = page.locator("button:has-text('Inpaint or Outpaint')")
        if await inpaint_btn.count() > 0:
            await inpaint_btn.first.click()
            await page.wait_for_timeout(1000)

        file_inputs = page.locator("input[type='file']")
        count = await file_inputs.count()
        print("Visible/total file inputs after opening inpaint tab:", count)
        for i in range(count):
            print(f"File input {i} visible:", await file_inputs.nth(i).is_visible())

        await b.close()

asyncio.run(test_files())
