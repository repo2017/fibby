import asyncio
from playwright.async_api import async_playwright

async def dbg():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(5000)

        # Check if there's any error banner or text
        text = await page.inner_text("body")
        if "Error" in text or "CUDA" in text or "Exception" in text:
            print("Found error text on page!")

        await b.close()

asyncio.run(dbg())
