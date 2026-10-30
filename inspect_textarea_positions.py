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

        textareas = await page.locator("textarea").all()
        for i, ta in enumerate(textareas):
            ph = await ta.get_attribute("placeholder")
            box = await ta.bounding_box()
            print(f"TextArea {i}: placeholder={ph} | box={box}")

        gen_btn = await page.locator("#generate_button").bounding_box()
        print("Generate button box:", gen_btn)

        await b.close()

asyncio.run(inspect())
