import asyncio
from playwright.async_api import async_playwright
import os
from PIL import Image, ImageDraw
import io

async def inspect():
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
        await main_textarea.fill("a yellow duck", force=True)

        print("Clicking Generate...")
        await page.locator("#generate_button").click()

        # Wait for Stop button to appear then hide
        try:
            await page.wait_for_selector("#stop_button", state="visible", timeout=15000)
            print("Generation in progress...")
        except:
            pass

        await page.wait_for_selector("#stop_button", state="hidden", timeout=300000)
        print("Generation finished! Inspecting all image elements...")
        await page.wait_for_timeout(2000)

        imgs = await page.locator("img").all()
        print(f"Total img elements on page: {len(imgs)}")
        for i, img in enumerate(imgs):
            src = await img.get_attribute("src")
            parent_id = await img.evaluate("el => el.closest('[id]') ? el.closest('[id]').id : 'no-id'")
            parent_class = await img.evaluate("el => el.parentElement.className")
            src_snippet = src[:60] if src else "None"
            print(f"Img {i}: parent_id={parent_id} | class={parent_class} | src={src_snippet}")

        await b.close()

asyncio.run(inspect())
