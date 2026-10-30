from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from playwright.async_api import async_playwright
import shutil
import os
import glob
import re
import asyncio
import traceback
import time
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FOOOCUS_URL = "http://127.0.0.1:7865"
OUTPUT_SEARCH_DIRS = [
    r"C:\ai\Fooocus_win64_2-5-0\Fooocus_win64_2-5-0\Fooocus\outputs",
    r"C:\Users\nstra\AppData\Local\Temp\fooocus"
]

def get_latest_generated_image():
    valid_pngs = []
    for s_dir in OUTPUT_SEARCH_DIRS:
        if not os.path.exists(s_dir):
            continue
        pngs = glob.glob(os.path.join(s_dir, "**", "*.png"), recursive=True)
        for p in pngs:
            try:
                filename = os.path.basename(p)
                ctime = os.path.getctime(p)
                if (re.search(r'\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}', filename) or "fooocus" in p.lower()) and os.path.getsize(p) > 50000:
                    valid_pngs.append((ctime, p))
            except:
                pass

    if valid_pngs:
        valid_pngs.sort(key=lambda x: x[0], reverse=True)
        latest_path = valid_pngs[0][1]
        print(f"[Playwright] Found latest Fooocus generated output file: {latest_path}")
        return f"{FOOOCUS_URL}/file={latest_path.replace('\\', '/')}"
    return None

@app.post("/api/inpaint")
async def inpaint(
    image: UploadFile = File(...),
    mask: UploadFile = File(default=None),
    prompt: str = Form(...),
    negative_prompt: str = Form(default=""),
    mask_points: str = Form(default="[]"),
    canvas_width: float = Form(default=512),
    canvas_height: float = Form(default=512)
):
    temp_dir = "temp_inputs"
    os.makedirs(temp_dir, exist_ok=True)

    image_path = os.path.abspath(os.path.join(temp_dir, f"img_{image.filename}"))
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    try:
        points = json.loads(mask_points)
    except:
        points = []

    browser = None
    try:
        print("[Playwright] Launching browser (lightning fast, slow_mo=0)...")
        async with async_playwright() as p:
            # Removed slow_mo for instant execution speed
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            print(f"[Playwright] Navigating to {FOOOCUS_URL}...")
            await page.goto(FOOOCUS_URL, timeout=60000)

            print("[Playwright] Waiting for Fooocus UI to load...")
            await page.wait_for_selector("body", timeout=30000)
            await asyncio.sleep(3)

            print("[Playwright] Enabling 'Input Image'...")
            input_img_lbl = page.locator("text=Input Image")
            if await input_img_lbl.count() > 0:
                await input_img_lbl.first.click()
                await asyncio.sleep(1)

            print("[Playwright] Clicking 'Inpaint or Outpaint' tab...")
            inpaint_btn = page.locator("button:has-text('Inpaint or Outpaint')")
            if await inpaint_btn.count() > 0:
                await inpaint_btn.first.click()
                await asyncio.sleep(1)

            print("[Playwright] Setting Inpaint Method to 'Modify Content'...")
            try:
                method_input = page.locator("label:has-text('Method') input").first
                if await method_input.count() > 0:
                    await method_input.click()
                    await method_input.fill("Modify Content")
                    await page.keyboard.press("Enter")
                    await asyncio.sleep(0.5)
            except Exception as ex:
                print(f"[Playwright] Method selection warning: {ex}")

            print("[Playwright] Uploading base image into Inpaint Canvas slot...")
            inpaint_tab = page.locator("#component-70")
            fi = inpaint_tab.locator("input[type='file']").first
            await fi.set_input_files(image_path)
            await fi.evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")

            print("[Playwright] Waiting for canvas image preview to render...")
            await asyncio.sleep(2)

            print("[Playwright] Replaying optimized mask strokes instantly onto Fooocus canvas...")
            canvas_el = inpaint_tab.locator("canvas").first
            box = await canvas_el.bounding_box()
            if box and points:
                scale_x = box["width"] / float(canvas_width)
                scale_y = box["height"] / float(canvas_height)

                for pt in points:
                    pt_type = pt.get("type")
                    if pt_type == "down":
                        await page.mouse.move(box["x"] + pt["x"] * scale_x, box["y"] + pt["y"] * scale_y)
                        await page.mouse.down()
                    elif pt_type == "move":
                        await page.mouse.move(box["x"] + pt["x"] * scale_x, box["y"] + pt["y"] * scale_y)
                    elif pt_type == "up":
                        await page.mouse.up()
                try:
                    await page.mouse.up()
                except:
                    pass
                print("[Playwright] Mask strokes replayed successfully!")
            else:
                if box:
                    cx = box["x"] + box["width"] / 2
                    cy = box["y"] + box["height"] / 2
                    await page.mouse.move(cx - 50, cy - 50)
                    await page.mouse.down()
                    for dx in range(-50, 50, 10):
                        await page.mouse.move(cx + dx, cy - 50)
                    for dy in range(-50, 50, 10):
                        await page.mouse.move(cx + 50, cy + dy)
                    await page.mouse.up()

            await asyncio.sleep(1)

            print(f"[Playwright] Entering prompt into main box: '{prompt}'...")
            main_textarea = page.locator("textarea").first
            await main_textarea.click()
            await main_textarea.fill(prompt)
            await page.evaluate("""(el) => {
                if (el) {
                    el.dispatchEvent(new Event('change', { bubbles: true }));
                    el.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }""", await main_textarea.element_handle())
            await asyncio.sleep(1)

            print("[Playwright] Clicking Generate button...")
            await page.locator("#generate_button").click(force=True)

            print("[Playwright] Generation started! Waiting for Fooocus to finish processing...")

            try:
                await page.wait_for_selector("#stop_button", state="visible", timeout=20000)
                print("[Playwright] Fooocus generation is actively running...")
            except Exception:
                pass

            await page.wait_for_selector("#stop_button", state="hidden", timeout=600000)
            print("[Playwright] Fooocus generation completed! Extracting generated output file...")

            await asyncio.sleep(3)

            # Extract generated output file
            img_src = get_latest_generated_image()

            # Fallback to DOM gallery
            if not img_src:
                gallery_imgs = page.locator("#final_gallery img, #component-7 img, div[data-testid='gallery'] img")
                count = await gallery_imgs.count()
                if count > 0:
                    for i in range(count - 1, -1, -1):
                        src = await gallery_imgs.nth(i).get_attribute("src")
                        if src and ("/file=" in src or "blob:" in src) and "data:image" not in src:
                            img_src = src
                            break

            if not img_src:
                all_imgs = await page.locator("img[src*='/file=']").all()
                if len(all_imgs) > 0:
                    img_src = await all_imgs[-1].get_attribute("src")

            if not img_src:
                raise Exception("No generated output image found.")

            print(f"[Playwright] Final generated image source URL: {img_src}")

            if img_src and img_src.startswith("/"):
                img_src = FOOOCUS_URL + img_src

            if img_src:
                img_src = img_src.replace("\\", "/")

            await asyncio.sleep(1)
            await browser.close()

            return {"result": [img_src]}

    except Exception as e:
        print("[Playwright Error]:", traceback.format_exc())
        if browser:
            try:
                await browser.close()
            except:
                pass
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
