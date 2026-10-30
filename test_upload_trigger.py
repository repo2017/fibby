import asyncio
from playwright.async_api import async_playwright
import os

async def test_up():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        # Check if clicking upload box opens file chooser
        # In Gradio, clicking the dropzone area triggers file chooser
        dropzones = page.locator(".file-dropzone, .upload-button, div:has-text('Drop Image Here')")
        print("Dropzones count:", await dropzones.count())

        await b.close()

asyncio.run(test_up())
