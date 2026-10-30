import asyncio
from playwright.async_api import async_playwright
import os
import requests
from PIL import Image, ImageDraw

async def run_full_test():
    print("=" * 60)
    print("STEP 1: Creating/Downloading realistic house base image...")
    print("=" * 60)

    os.makedirs("temp_inputs", exist_ok=True)
    house_path = os.path.abspath("temp_inputs/house_base.png")

    # Try fetching a real house image from Unsplash / public domain, or create a detailed house photo
    try:
        res = requests.get("https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=600&auto=format&fit=crop", timeout=10)
        if res.status_code == 200:
            with open(house_path, "wb") as f:
                f.write(res.content)
            print("Successfully downloaded house photo from web!")
        else:
            raise Exception("Web fetch failed")
    except Exception as e:
        print("Fallback: generating structured house photo...")
        img = Image.new('RGB', (600, 600), color=(135, 206, 235)) # Sky
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 400, 600, 600), fill=(34, 139, 34)) # Grass
        draw.rectangle((150, 200, 450, 420), fill=(180, 100, 60)) # House body
        draw.polygon([(120, 200), (300, 80), (480, 200)], fill=(120, 40, 40)) # Roof
        draw.rectangle((260, 300, 340, 420), fill=(100, 50, 20)) # Door
        draw.rectangle((180, 240, 240, 300), fill=(255, 255, 200)) # Window 1
        draw.rectangle((360, 240, 420, 300), fill=(255, 255, 200)) # Window 2
        img.save(house_path)

    async with async_playwright() as p:
        print("\n" + "=" * 60)
        print("STEP 2: Launching browser and navigating to Web Application...")
        print("=" * 60)

        browser = await p.chromium.launch(headless=False, slow_mo=150)
        page = await browser.new_page()

        await page.goto("http://127.0.0.1:8000/", timeout=30000)
        await page.wait_for_timeout(2000)
        print("Web app loaded successfully!")

        print("\n" + "=" * 60)
        print("STEP 3: Uploading house image to Web Application canvas...")
        print("=" * 60)

        upload_input = page.locator("#imageUpload")
        await upload_input.set_input_files(house_path)
        await page.wait_for_timeout(2000)

        # Verify canvas is visible
        canvas = page.locator("#imageCanvas")
        await canvas.wait_for(state="visible")
        print("Canvas editor rendered with uploaded house image!")

        print("\n" + "=" * 60)
        print("STEP 4: Drawing mask on canvas over the house area...")
        print("=" * 60)

        box = await canvas.bounding_box()
        if box:
            # Draw brush strokes over the center house area
            center_x = box["x"] + box["width"] / 2
            center_y = box["y"] + box["height"] / 2

            await page.mouse.move(center_x - 80, center_y - 20)
            await page.mouse.down()
            for dx in range(-80, 80, 10):
                for dy in range(-40, 40, 10):
                    await page.mouse.move(center_x + dx, center_y + dy)
                    await page.wait_for_timeout(20)
            await page.mouse.up()
            print("Mask successfully painted over house region!")

        await page.wait_for_timeout(2000)
        await page.screenshot(path="step4_mask_drawn.png")
        print("Saved screenshot of drawn mask: step4_mask_drawn.png")

        print("\n" + "=" * 60)
        print("STEP 5: Typing prompt 'a red luxury sports car'...")
        print("=" * 60)

        prompt_box = page.locator("#prompt")
        await prompt_box.fill("a shiny red luxury sports car parked on grass")
        await page.wait_for_timeout(1500)

        print("\n" + "=" * 60)
        print("STEP 6: Clicking 'Generate Modification' button...")
        print("=" * 60)

        gen_btn = page.locator("#generateBtn")
        await gen_btn.click()
        print("Generation triggered on client! Server automation running...")

        print("\n" + "=" * 60)
        print("STEP 7: Waiting for Fooocus local SDXL inpainting completion...")
        print("=" * 60)

        # Wait for result image element to become visible (timeout 5 minutes)
        result_img = page.locator("#result-img")
        await result_img.wait_for(state="visible", timeout=300000)

        result_src = await result_img.get_attribute("src")
        print(f"Generation complete! Result image source URL: {result_src}")

        await page.wait_for_timeout(3000)
        await page.screenshot(path="step8_final_web_result.png")
        print("Saved web app final screenshot: step8_final_web_result.png")

        print("\n" + "=" * 60)
        print("STEP 8: Downloading final image file for visual inspection...")
        print("=" * 60)

        if result_src:
            if result_src.startswith("data:image"):
                import base64
                header, b64_data = result_src.split(",", 1)
                img_bytes = base64.b64decode(b64_data)
                with open("house_to_car_result.png", "wb") as out_f:
                    out_f.write(img_bytes)
            else:
                r = requests.get(result_src)
                if r.status_code == 200:
                    with open("house_to_car_result.png", "wb") as out_f:
                        out_f.write(r.content)

            print("Final generated image saved to house_to_car_result.png!")

        await browser.close()

asyncio.run(run_full_test())
