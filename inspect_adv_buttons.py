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

        await page.locator("text=Enable Advanced Masking Features").click()
        await page.wait_for_timeout(1500)

        # Print all buttons visible in active tab
        buttons = await page.locator(".tabitem:not(.hide) button").all_inner_texts()
        print("Buttons in active tab:", [b.strip() for b in buttons if b.strip()])

        # Print all labels / checkboxes
        labels = await page.locator(".tabitem:not(.hide) label").all_inner_texts()
        print("Labels in active tab:", [l.strip() for l in labels if l.strip()])

        await b.close()

asyncio.run(inspect())
