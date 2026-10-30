import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        # Find element containing 'Method'
        method_label = page.locator("text=Method").first
        if await method_label.count() > 0:
            print("Found Method label!")
            parent = method_label.locator("xpath=ancestor::label | ancestor::div[contains(@class, 'block')]").first
            print("Parent inner text:", await parent.inner_text())

        await b.close()

asyncio.run(inspect())
