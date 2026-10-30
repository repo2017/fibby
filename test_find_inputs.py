import asyncio
from playwright.async_api import async_playwright

async def find_inputs():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        # Find file inputs inside containers containing specific text
        # Let's check containers with 'Input Image' and 'Mask Upload'
        for label in ["Input Image", "Mask Upload"]:
            container = page.locator(f"text={label}").locator("xpath=ancestor::div[contains(@class, 'block')]").first
            if await container.count() > 0:
                fi = container.locator("input[type='file']")
                print(f"File input for '{label}': count = {await fi.count()}")
            else:
                print(f"Container for '{label}' not found directly")

        await b.close()

asyncio.run(find_inputs())
