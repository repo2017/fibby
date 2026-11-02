import asyncio
from playwright.async_api import async_playwright
import json

async def analyze_fooocus():
    print("=== Analyzing Fooocus UI via Playwright ===")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        print("Navigating to http://127.0.0.1:7865...")
        await page.goto("http://127.0.0.1:7865", timeout=60000)
        await page.wait_for_selector("body", timeout=30000)
        await asyncio.sleep(2)

        print("\n--- Searching for Input Image & Inpaint tabs ---")
        input_img_lbl = page.locator("text=Input Image")
        if await input_img_lbl.count() > 0:
            await input_img_lbl.first.click()
            await asyncio.sleep(1)

        inpaint_btn = page.locator("button:has-text('Inpaint or Outpaint')")
        if await inpaint_btn.count() > 0:
            await inpaint_btn.first.click()
            await asyncio.sleep(1)

        inpaint_tab = page.locator("#component-70")

        print("\n--- Inspecting file inputs under Inpaint tab ---")
        file_inputs = await inpaint_tab.locator("input[type='file']").all()
        print(f"Found {len(file_inputs)} file input(s) in Inpaint tab.")

        print("\n--- Inspecting canvas element under Inpaint tab ---")
        canvas_el = inpaint_tab.locator("canvas").first
        if await canvas_el.count() > 0:
            box = await canvas_el.bounding_box()
            print(f"Canvas bounding box on screen: {box}")

            canvas_info = await canvas_el.evaluate("""el => ({
                width: el.width,
                height: el.height,
                styleWidth: el.style.width,
                styleHeight: el.style.height,
                offsetWidth: el.offsetWidth,
                offsetHeight: el.offsetHeight,
                clientWidth: el.clientWidth,
                clientHeight: el.clientHeight
            })""")
            print(f"Canvas element DOM properties: {json.dumps(canvas_info, indent=2)}")
        else:
            print("No canvas element found!")

        print("\n--- Inspecting sliders and number inputs in Fooocus ---")
        inputs = await page.locator("input[type='range'], input[type='number']").all()
        for i, inp in enumerate(inputs):
            p_text = await inp.evaluate("el => el.closest('.component, .form, div, label')?.innerText || ''")
            val = await inp.evaluate("el => el.value")
            inp_type = await inp.evaluate("el => el.type")
            print(f"Input [{i}] ({inp_type}): value='{val}' | text='{p_text.strip().replace(chr(10), ' ')}'")

        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(analyze_fooocus())
