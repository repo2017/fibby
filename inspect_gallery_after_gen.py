import asyncio
from playwright.async_api import async_playwright
import os
from PIL import Image, ImageDraw

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
        img_path = os.path.abspath("temp_inputs/visual_flower.png")
        img = Image.new('RGB', (512, 512), color=(200, 220, 255))
        draw = ImageDraw.Draw(img)
        draw.line([(256, 256), (256, 480)], fill=(30, 140, 30), width=12)
        draw.ellipse((120, 320, 240, 380), fill=(40, 160, 40))
        draw.ellipse((270, 340, 390, 400), fill=(255, 255, 255)) # Mask
        img.save(img_path)

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
        await main_textarea.fill("a bright golden autumn leaf", force=True)

        print("Initial images in #final_gallery BEFORE generate:")
        init_imgs = await page.locator("#final_gallery img").all()
        for i, im in enumerate(init_imgs):
            print(f"  Before Img {i}: {await im.get_attribute('src')}")

        print("Clicking Generate...")
        await page.locator("#generate_button").click()

        try:
            await page.wait_for_selector("#stop_button", state="visible", timeout=20000)
        except:
            pass

        await page.wait_for_selector("#stop_button", state="hidden", timeout=300000)
        print("Generation finished!")
        await page.wait_for_timeout(3000)

        print("Images in #final_gallery AFTER generate:")
        after_imgs = await page.locator("#final_gallery img").all()
        for i, im in enumerate(after_imgs):
            src = await im.get_attribute('src')
            print(f"  After Img {i}: {src}")

        await b.close()

asyncio.run(inspect())
