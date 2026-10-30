import asyncio
from playwright.async_api import async_playwright

async def find_input():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        # Find all file inputs and check which one is visible or inside the active tab
        inputs = await page.locator("input[type='file']").all()
        print("Total file inputs:", len(inputs))
        for i, inp in enumerate(inputs):
            visible = await inp.is_visible()
            box = await inp.bounding_box()
            print(f"Input {i}: visible={visible}, box={box}")

        await b.close()

asyncio.run(find_input())
