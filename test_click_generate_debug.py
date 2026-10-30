import asyncio
from playwright.async_api import async_playwright
import os
from PIL import Image
import io

async def test_gen():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        # Fill prompt
        main_textarea = page.locator("textarea").first
        await main_textarea.fill("a yellow duck", force=True)
        await page.evaluate("""(el) => {
            if (el) {
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""", await main_textarea.element_handle())

        os.makedirs("temp_inputs", exist_ok=True)
        img_path = os.path.abspath("temp_inputs/visual_test.png")
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

        print("Clicking Generate button...")
        gen_btn = page.locator("#generate_button")
        await gen_btn.click()

        # Check immediately if Stop button is visible or if generation started
        for sec in range(10):
            await page.wait_for_timeout(1000)
            stop_visible = await page.locator("#stop_button").is_visible()
            gen_visible = await page.locator("#generate_button").is_visible()
            print(f"Sec {sec}: stop_button visible={stop_visible}, generate_button visible={gen_visible}")

        await b.close()

asyncio.run(test_gen())
