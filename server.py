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

# Permanent local storage for Fibby
FIBBY_OUTPUTS_DIR = os.path.abspath("outputs")
os.makedirs(FIBBY_OUTPUTS_DIR, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=FIBBY_OUTPUTS_DIR), name="outputs")

def extract_and_store_generated_images(start_time=None, count=2):
    """
    Finds the 2 generated PNGs created during this run (after start_time),
    copies them into Fibby's local 'outputs' folder, and returns static Fibby URLs.
    """
    found_paths = []
    seen_filenames = set()
    min_ctime = (start_time - 10) if start_time else 0

    # 1. Search Temp/fooocus subdirectories
    temp_dir = r"C:\Users\nstra\AppData\Local\Temp\fooocus"
    if os.path.exists(temp_dir):
        subdirs = [os.path.join(temp_dir, d) for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
        subdirs.sort(key=os.path.getmtime, reverse=True)

        for sd in subdirs:
            if start_time and os.path.getmtime(sd) < min_ctime:
                continue
            pngs = glob.glob(os.path.join(sd, "*.png"))
            if pngs:
                pngs.sort(key=os.path.getctime, reverse=True)
                p = pngs[0]
                fname = os.path.basename(p)
                if fname not in seen_filenames and os.path.getsize(p) > 50000:
                    seen_filenames.add(fname)
                    found_paths.append((os.path.getctime(p), p))

    # 2. Search Fooocus outputs folder
    out_dir = r"C:\ai\Fooocus_win64_2-5-0\Fooocus_win64_2-5-0\Fooocus\outputs"
    if os.path.exists(out_dir):
        pngs = glob.glob(os.path.join(out_dir, "**", "*.png"), recursive=True)
        for p in pngs:
            try:
                ctime = os.path.getctime(p)
                fname = os.path.basename(p)
                if ctime >= min_ctime and fname not in seen_filenames and os.path.getsize(p) > 50000:
                    seen_filenames.add(fname)
                    found_paths.append((ctime, p))
            except:
                pass

    # Sort chronologically (oldest first)
    found_paths.sort(key=lambda x: x[0])

    # Take the count newest files
    if len(found_paths) > count:
        found_paths = found_paths[-count:]

    # Copy files to Fibby's static 'outputs' directory
    stored_urls = []
    for ctime, pth in found_paths:
        dest_filename = f"{int(ctime)}_{os.path.basename(pth)}"
        dest_path = os.path.join(FIBBY_OUTPUTS_DIR, dest_filename)
        shutil.copy2(pth, dest_path)
        url = f"http://127.0.0.1:8000/outputs/{dest_filename}"
        stored_urls.append(url)
        print(f"[Fibby Storage] Stored {pth} -> {dest_path}")

    # Safety duplicate if only 1 image found
    while len(stored_urls) < count and len(stored_urls) > 0:
        stored_urls.append(stored_urls[0])

    print(f"[Fibby Storage] Final stored URLs ({len(stored_urls)} returned): {stored_urls}")
    return stored_urls

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

            print("[Playwright] Enabling 'Advanced' mode to set Image Number = 2...")
            try:
                adv_chk = page.locator("label:has-text('Advanced') input[type='checkbox']").first
                if await adv_chk.count() > 0 and not await adv_chk.is_checked():
                    await adv_chk.check()
                    print("[Playwright] Checked 'Advanced' checkbox!")

                await page.wait_for_selector("div:has-text('Image Number')", timeout=10000)
                await asyncio.sleep(0.5)

                num_set = False
                for inp in await page.locator("input[type='number']").all():
                    p_text = await inp.evaluate("el => el.closest('.component, .form, div')?.innerText || ''")
                    if "Image Number" in p_text:
                        await inp.click()
                        await inp.fill("2")
                        await inp.press("Enter")
                        await inp.evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")
                        val = await inp.input_value()
                        print(f"[Playwright] Successfully set Image Number input to: {val}")
                        num_set = True
                        break
                if not num_set:
                    print("[Playwright Warning]: Image Number input element was not found in DOM!")
            except Exception as ex:
                print(f"[Playwright] Advanced/Image Number setting error: {ex}")

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
                    print("[Playwright] Drawing 200px fallback mask in center...")
                    await page.mouse.move(cx - 80, cy - 80)
                    await page.mouse.down()
                    for r in range(10, 100, 15):
                        for angle in range(0, 360, 20):
                            import math
                            mx = cx + r * math.cos(math.radians(angle))
                            my = cy + r * math.sin(math.radians(angle))
                            await page.mouse.move(mx, my)
                    await page.mouse.up()

            await asyncio.sleep(1)
            start_time = time.time()

            print("[Playwright] Clicking Generate button...")
            await page.locator("#generate_button").click(force=True)

            print("[Playwright] Generation started! Waiting for Fooocus to finish processing...")

            try:
                await page.wait_for_selector("#stop_button", state="visible", timeout=20000)
                print("[Playwright] Fooocus generation is actively running...")
            except Exception:
                pass

            await page.wait_for_selector("#stop_button", state="hidden", timeout=600000)
            print("[Playwright] Fooocus generation completed! Storing generated output files...")

            await asyncio.sleep(3)

            # Store the 2 generated images in Fibby's own local static folder and return Fibby URLs
            stored_urls = extract_and_store_generated_images(start_time=start_time, count=2)

            if not stored_urls or len(stored_urls) == 0:
                raise Exception("No generated output images found or stored.")

            await asyncio.sleep(1)
            await browser.close()

            return {"result": stored_urls}

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
