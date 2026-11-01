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

        print("--- Enabling Advanced ---")
        adv_chk = page.locator("label:has-text('Advanced') input[type='checkbox']").first
        if await adv_chk.count() > 0 and not await adv_chk.is_checked():
            await adv_chk.check()
            await asyncio.sleep(1)

        print("--- Entering Main Prompt ---")
        main_ta = page.locator("textarea[placeholder*='paste parameters'], textarea[placeholder*='Type prompt here or']").first
        if await main_ta.count() > 0:
            await main_ta.scroll_into_view_if_needed()
            await main_ta.click()
            await main_ta.fill(prompt)
            await main_ta.evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")
            print("Main prompt entered successfully!")

        print("--- Entering Negative Prompt ---")
        # Find visible textarea whose parent or label mentions Negative Prompt
        neg_ta = None
        for ta in await page.locator("textarea").all():
            if await ta.is_visible():
                lbl = await ta.evaluate("el => el.closest('.component, .form, div, label')?.innerText || ''")
                if "Negative Prompt" in lbl:
                    neg_ta = ta
                    break

        if neg_ta:
            await neg_ta.scroll_into_view_if_needed()
            await neg_ta.click()
            await neg_ta.fill(negative_prompt)
            await neg_ta.evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")
            print("Negative prompt entered successfully!")
        else:
            print("Negative prompt textarea not visible, skipping or scrolling...")

        await asyncio.sleep(3)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
