import asyncio
from playwright.async_api import async_playwright

async def test_click():
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
        print("Successfully clicked Enable Advanced Masking Features!")
        await page.wait_for_timeout(2000)
        await page.screenshot(path="adv_mask_checked.png")
        await b.close()

asyncio.run(test_click())
