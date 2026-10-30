import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(6000)

        file_inputs = await page.locator("input[type='file']").count()
        textareas = await page.locator("textarea").count()
        buttons = await page.locator("button").all_inner_texts()

        print("FILE INPUTS:", file_inputs)
        print("TEXTAREAS:", textareas)
        print("BUTTONS:", [btn.strip() for btn in buttons if btn.strip()][:15])

        await b.close()

asyncio.run(inspect())
