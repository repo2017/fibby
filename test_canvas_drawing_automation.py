import asyncio
from playwright.async_api import async_playwright
import os
from PIL import Image

async def test_draw():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False, slow_mo=50)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        os.makedirs("temp_inputs", exist_ok=True)
        img_path = os.path.abspath("temp_inputs/clean_base.png")
        img = Image.new('RGB', (512, 512), color=(100, 150, 220))
        img.save(img_path)

        # Upload clean base image to inpaint tab file input
        inpaint_tab = page.locator("#component-70, .tabitem:has-text('Inpaint or Outpaint')")
        file_input = inpaint_tab.locator("input[type='file']").first
        await file_input.set_input_files(img_path)
        await page.evaluate("""(el) => {
            if (el) {
                el.dispatchEvent(new Event('change', { bubbles: true }));
                el.dispatchEvent(new Event('input', { bubbles: true }));
            }
        }""", await file_input.element_handle())
        await page.wait_for_timeout(3000)

        # Locate Fooocus canvas
        canvas = inpaint_tab.locator("canvas").first
        box = await canvas.bounding_box()
        if box:
            print("Canvas bounding box:", box)
            # Simulate drawing on Fooocus canvas
            start_x = box["x"] + box["width"] / 2 - 50
            start_y = box["y"] + box["height"] / 2 - 50

            await page.mouse.move(start_x, start_y)
            await page.mouse.down()
            for i in range(100):
                await page.mouse.move(start_x + i, start_y + i)
            await page.mouse.up()
            print("Successfully drew stroke on Fooocus canvas!")

        await page.wait_for_timeout(3000)
        await page.screenshot(path="canvas_drawn_proof.png")
        print("Screenshot saved to canvas_drawn_proof.png")
        await b.close()

asyncio.run(test_draw())
