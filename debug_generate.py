import asyncio
from playwright.async_api import async_playwright
import os

async def debug():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        method_input = page.locator("label:has-text('Method') input").first
        await method_input.click()
        await method_input.fill("Modify Content")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1000)

        os.makedirs("temp_inputs", exist_ok=True)
        img_path = os.path.abspath("temp_inputs/visual_test.png")
        from PIL import Image
        im = Image.new('RGB', (300, 300), color='red')
        im.save(img_path)

        inpaint_tab = page.locator("#component-70, .tabitem:has-text('Inpaint or Outpaint')")
        inpaint_file_input = inpaint_tab.locator("input[type='file']").first
        await inpaint_file_input.set_input_files(img_path)
        await page.evaluate("""(el) => {
            if (el) {
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""", await inpaint_file_input.element_handle())
        await page.wait_for_timeout(2000)

        main_textarea = page.locator("textarea").first
        await main_textarea.fill("a blue flower", force=True)
        await page.evaluate("""(el) => {
            if (el) {
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""", await main_textarea.element_handle())

        print("Clicking Generate...")
        gen_btn = page.locator("#generate_button")
        await gen_btn.click()

        for i in range(10):
            await page.wait_for_timeout(3000)
            print(f"Check {i}:")
            # Check progress bar or error toast or buttons
            btns = await page.locator("button").all_inner_texts()
            print("  Buttons:", [b.strip() for b in btns if b.strip()][:8])
            await page.screenshot(path=f"gen_step_{i}.png")

        await b.close()

asyncio.run(debug())
