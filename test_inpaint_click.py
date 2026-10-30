import asyncio
from playwright.async_api import async_playwright

async def test_click():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(5000)

        # Click Inpaint or Outpaint tab
        inpaint_tab = page.locator("button:has-text('Inpaint or Outpaint')")
        if await inpaint_tab.count() > 0:
            await inpaint_tab.click()
            print("Clicked Inpaint or Outpaint tab")
            await page.wait_for_timeout(2000)

        await page.screenshot(path='inpaint_tab.png')
        await b.close()

asyncio.run(test_click())
