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

        # Get outerHTML of the entire active tabitem
        tab_html = await page.evaluate("""() => {
            const activeTab = document.querySelector('.tabitem:not(.hide)');
            return activeTab ? activeTab.outerHTML : 'Active tab not found';
        }""")

        print("Active tab HTML length:", len(tab_html))
        # Print snippet of HTML
        print(tab_html[:2000])

        await b.close()

asyncio.run(inspect())
