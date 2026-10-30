import asyncio
from playwright.async_api import async_playwright

async def test_order():
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
        count = await file_inputs.count()
        print("Total file inputs:", count)

        for i in range(count):
            box = await file_inputs.nth(i).bounding_box()
            print(f"File input {i} box:", box)

        await b.close()

asyncio.run(test_order())
