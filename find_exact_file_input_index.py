import asyncio
from playwright.async_api import async_playwright
import os

async def find_exact_index():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=False)
        page = await b.new_page()
        await page.goto('http://127.0.0.1:7865')
        await page.wait_for_timeout(4000)

        await page.locator("text=Input Image").first.click()
        await page.wait_for_timeout(1000)

        await page.locator("button:has-text('Inpaint or Outpaint')").first.click()
        await page.wait_for_timeout(1000)

        os.makedirs("temp_inputs", exist_ok=True)
        img_path = os.path.abspath("temp_inputs/visual_test.png")
        from PIL import Image
        im = Image.new('RGB', (300, 300), color='red')
        im.save(img_path)

        file_inputs = await page.locator("input[type='file']").all()
        print("Total file inputs found:", len(file_inputs))

        for i, inp in enumerate(file_inputs):
            print(f"Testing upload on file input index {i}...")
            try:
                await inp.set_input_files(img_path)
                await page.evaluate("""(inputElem) => {
                    if (inputElem) {
                        inputElem.dispatchEvent(new Event('change', { bubbles: true }));
                        inputElem.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                }""", inp)
                await page.wait_for_timeout(1000)

                # Check if 'Drop Image Here' is gone from the inpaint panel
                inpaint_pane_text = await page.locator("#component-3").inner_text() if await page.locator("#component-3").count() > 0 else ""

                screenshot_filename = f"test_index_{i}.png"
                await page.screenshot(path=screenshot_filename)
                print(f"  Index {i} screenshot saved to {screenshot_filename}")

            except Exception as e:
                print(f"  Index {i} failed: {e}")

        await b.close()

asyncio.run(find_exact_index())
