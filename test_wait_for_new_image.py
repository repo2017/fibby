import asyncio
from playwright.async_api import async_playwright
import os
from PIL import Image
import time

async def test_wait():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        # Count existing images in final gallery
        initial_gallery_count = await page.locator("#final_gallery img").count()
        print("Initial images in #final_gallery:", initial_gallery_count)

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
        await main_textarea.fill("a bright green tree", force=True)
        await page.evaluate("""(el) => {
            if (el) {
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""", await main_textarea.element_handle())

        print("Clicking Generate button...")
        await page.locator("#generate_button").click()

        # Wait for Stop button to become visible (generation started)
        await page.wait_for_selector("#stop_button", state="visible", timeout=10000)
        print("Generation started! Stop button is visible.")

        # Wait for Stop button to become hidden (generation complete)
        print("Waiting for generation to complete (waiting for Stop button to hide)...")
        start_t = time.time()
        await page.wait_for_selector("#stop_button", state="hidden", timeout=300000)
        duration = time.time() - start_t
        print(f"Generation completed in {duration:.1f} seconds!")

        # Extract new image
        final_imgs = page.locator("#final_gallery img")
        new_count = await final_imgs.count()
        print(f"New images count in #final_gallery: {new_count}")

        if new_count > 0:
            final_src = await final_imgs.last.get_attribute("src")
            print("Final generated image src:", final_src)

        await b.close()

asyncio.run(test_wait())
