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

        file_inputs = page.locator("input[type='file']")
        count = await file_inputs.count()
        print("Total file inputs:", count)

        for i in range(count):
            elem = file_inputs.nth(i)
            # Find parent or label text
            outer_html = await elem.evaluate("el => el.outerHTML")
            parent_text = await elem.evaluate("el => el.closest('.gr-block, .gr-box, div').innerText.substring(0, 100)")
            print(f"--- File Input {i} ---")
            print("Parent text snippet:", parent_text.replace('\n', ' '))

        await b.close()

asyncio.run(inspect())
