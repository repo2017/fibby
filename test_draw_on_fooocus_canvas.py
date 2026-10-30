import asyncio
from playwright.async_api import async_playwright
import os
from PIL import Image

async def test_canvas_draw():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False, slow_mo=50)
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
        base_path = os.path.abspath("temp_inputs/clean_base.png")
        img = Image.new('RGB', (512, 512), color=(100, 150, 220))
        img.save(base_path)

        inpaint_tab = page.locator("#component-70")
        fi = inpaint_tab.locator("input[type='file']").first
        await fi.set_input_files(base_path)
        await fi.evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")
        await page.wait_for_timeout(3000)

        print("Drawing mask strokes directly on Fooocus inpaint canvas...")
        canvas = inpaint_tab.locator("canvas").first
        box = await canvas.bounding_box()
        if box:
            cx = box["x"] + box["width"] / 2
            cy = box["y"] + box["height"] / 2

            # Draw a circle/square of mask strokes on Fooocus canvas
            await page.mouse.move(cx - 50, cy - 50)
            await page.mouse.down()
            for dx in range(-50, 50, 5):
                await page.mouse.move(cx + dx, cy - 50)
            for dy in range(-50, 50, 5):
                await page.mouse.move(cx + 50, cy + dy)
            for dx in range(50, -50, -5):
                await page.mouse.move(cx + dx, cy + 50)
            for dy in range(50, -50, -5):
                await page.mouse.move(cx - 50, cy + dy)
            await page.mouse.up()
            print("Successfully painted mask on Fooocus canvas!")

        await page.wait_for_timeout(2000)

        # Fill prompt
        main_textarea = page.locator("textarea").first
        await main_textarea.click()
        await main_textarea.fill("a glowing golden coin")
        await page.evaluate("""(el) => {
            if (el) {
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""", await main_textarea.element_handle())
        await page.wait_for_timeout(1000)

        print("Clicking Generate button...")
        await page.locator("#generate_button").click(force=True)

        await page.wait_for_timeout(15000)
        await page.screenshot(path="canvas_generation_started.png")
        print("Screenshot saved to canvas_generation_started.png")
        await b.close()

asyncio.run(test_canvas_draw())
