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

        # Check dropdowns
        dropdowns = await page.locator(".gr-dropdown, [data-testid='dropdown'], select").all()
        print("Dropdown count:", len(dropdowns))
        for i, d in enumerate(dropdowns):
            print(f"Dropdown {i}:", await d.inner_text())

        # Check visible file dropzones / upload buttons
        upload_boxes = await page.locator(".file-dropzone, .upload-button, button:has-text('Upload')").all()
        print("Upload boxes count:", len(upload_boxes))

        await b.close()

asyncio.run(inspect())
