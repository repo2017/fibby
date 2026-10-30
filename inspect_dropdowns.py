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

        dropdowns = await page.locator("select, .dropdown, [role='combobox'], span:has-text('Inpaint or Outpaint')").all_inner_texts()
        print("Dropdowns / Options found:")
        for d in dropdowns:
            if d.strip():
                print(" -", d.strip()[:100])

        await b.close()

asyncio.run(inspect())
