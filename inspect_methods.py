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

        elements = page.locator("text=Inpaint or Outpaint")
        print("Count of 'Inpaint or Outpaint':", await elements.count())
        for i in range(await elements.count()):
            print(f"Elem {i}:", await elements.nth(i).evaluate("el => el.tagName + ' | ' + el.className"))

        await b.close()

asyncio.run(inspect())
