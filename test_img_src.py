import asyncio
from playwright.async_api import async_playwright

async def test_src():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(5000)

        imgs = page.locator("img")
        count = await imgs.count()
        print("Total images on page:", count)
        for i in range(count):
            print(i, await imgs.nth(i).get_attribute("src"))

        await b.close()

asyncio.run(test_src())
