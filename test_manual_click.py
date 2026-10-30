import asyncio
from playwright.async_api import async_playwright
import os
from PIL import Image, ImageDraw

async def test_why_no_gen():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()

        # Listen for console messages and page errors
        page.on("console", lambda msg: print(f"[Browser Console] {msg.type}: {msg.text}"))
        page.on("pageerror", lambda err: print(f"[Browser Error] {err}"))

        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        print("1. Enabling Input Image...")
        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        print("2. Clicking Inpaint or Outpaint...")
        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        print("3. Setting Method: Modify Content...")
        method_input = page.locator("label:has-text('Method') input").first
        await method_input.click()
        await method_input.fill("Modify Content")
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(1000)

        os.makedirs("temp_inputs", exist_ok=True)
        img_path = os.path.abspath("temp_inputs/visual_flower.png")
        img = Image.new('RGB', (512, 512), color=(200, 220, 255))
        draw = ImageDraw.Draw(img)
        draw.line([(256, 256), (256, 480)], fill=(30, 140, 30), width=12)
        draw.ellipse((120, 320, 240, 380), fill=(40, 160, 40))
        draw.ellipse((270, 340, 390, 400), fill=(255, 255, 255)) # Mask
        img.save(img_path)

        print("4. Uploading image to canvas file input...")
        inpaint_tab = page.locator("#component-70, .tabitem:has-text('Inpaint or Outpaint')")
        inpaint_file_input = inpaint_tab.locator("input[type='file']").first
        await inpaint_file_input.set_input_files(img_path)
        await page.evaluate("""(el) => {
            if (el) {
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""", await inpaint_file_input.element_handle())
        await page.wait_for_timeout(3000)

        print("5. Filling prompt...")
        main_textarea = page.locator("textarea").first
        await main_textarea.fill("a bright golden autumn leaf", force=True)
        await page.evaluate("""(el) => {
            if (el) {
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""", await main_textarea.element_handle())
        await page.wait_for_timeout(1000)

        print("6. Clicking Generate button...")
        gen_btn = page.locator("#generate_button")
        await gen_btn.click()

        for i in range(15):
            await page.wait_for_timeout(1000)
            stop_vis = await page.locator("#stop_button").is_visible()
            gen_vis = await page.locator("#generate_button").is_visible()
            print(f"  Sec {i}: #stop_button visible={stop_vis}, #generate_button visible={gen_vis}")

        await b.close()

asyncio.run(test_why_no_gen())
