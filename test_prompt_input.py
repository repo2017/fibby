import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto("http://127.0.0.1:7865")
        await page.wait_for_selector("body")
        await asyncio.sleep(2)

        prompt = "a glowing golden disco ball"
        negative_prompt = "blurry, dark"

        print("--- Finding Main Prompt textarea ---")
        main_ta = page.locator("textarea[placeholder*='paste parameters'], textarea[placeholder*='Type prompt here or']").first
        if await main_ta.count() > 0:
            await main_ta.click()
            await main_ta.fill(prompt)
            await main_ta.evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")
            print("Entered main prompt:", await main_ta.input_value())

        print("--- Finding Negative Prompt textarea ---")
        neg_ta = page.locator("textarea[placeholder*='Describing what you do not want'], textarea[placeholder='Type prompt here.']").first
        if await neg_ta.count() > 0:
            await neg_ta.click()
            await neg_ta.fill(negative_prompt)
            await neg_ta.evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")
            print("Entered negative prompt:", await neg_ta.input_value())

        await asyncio.sleep(3)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
