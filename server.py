from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from playwright.async_api import async_playwright
from pydantic import BaseModel
import shutil
import os
import glob
import re
import asyncio
import traceback
import time
import json
import sqlite3
import hashlib
import secrets

app = FastAPI()

@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

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

# SQLite Database & Auth Setup
DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            tokens INTEGER DEFAULT 100
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

@app.post("/api/register")
@app.post("/api/register/")
async def register(data: UserRegister):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        p_hash = hash_password(data.password)
        cursor.execute("INSERT INTO users (email, password_hash, tokens) VALUES (?, ?, 100)", (data.email, p_hash))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return JSONResponse(status_code=400, content={"error": "Email already registered."})

    session_token = secrets.token_hex(32)
    cursor.execute("INSERT INTO sessions (token, email) VALUES (?, ?)", (session_token, data.email))
    conn.commit()
    conn.close()
    return {"token": session_token, "email": data.email, "tokens": 100}

@app.post("/api/login")
@app.post("/api/login/")
async def login(data: UserLogin):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    p_hash = hash_password(data.password)
    cursor.execute("SELECT tokens FROM users WHERE email = ? AND password_hash = ?", (data.email, p_hash))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return JSONResponse(status_code=400, content={"error": "Invalid email or password."})

    tokens = row[0]
    session_token = secrets.token_hex(32)
    cursor.execute("REPLACE INTO sessions (token, email) VALUES (?, ?)", (session_token, data.email))
    conn.commit()
    conn.close()
    return {"token": session_token, "email": data.email, "tokens": tokens}

@app.get("/api/me")
@app.get("/api/me/")
async def me(token: str = None):
    if not token:
        return JSONResponse(status_code=401, content={"error": "Unauthorized"})
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM sessions WHERE token = ?", (token,))
    s_row = cursor.fetchone()
    if not s_row:
        conn.close()
        return JSONResponse(status_code=401, content={"error": "Invalid session"})
    email = s_row[0]
    cursor.execute("SELECT tokens FROM users WHERE email = ?", (email,))
    u_row = cursor.fetchone()
    conn.close()
    if not u_row:
        return JSONResponse(status_code=404, content={"error": "User not found"})
    return {"email": email, "tokens": u_row[0]}

def extract_and_store_generated_images(start_time=None, count=2):
    found_paths = []
    seen_filenames = set()

    temp_dir = r"C:\Users\nstra\AppData\Local\Temp\fooocus"
    if os.path.exists(temp_dir):
        subdirs = [os.path.join(temp_dir, d) for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
        subdirs.sort(key=os.path.getmtime, reverse=True)

        target_subdirs = subdirs[:max(count * 2, 6)]
        for sd in target_subdirs:
            pngs = glob.glob(os.path.join(sd, "*.png"))
            if pngs:
                pngs.sort(key=os.path.getctime, reverse=True)
                p = pngs[0]
                fname = os.path.basename(p)
                if fname not in seen_filenames and os.path.getsize(p) > 50000:
                    seen_filenames.add(fname)
                    found_paths.append((os.path.getctime(p), p))

    out_dir = r"C:\ai\Fooocus_win64_2-5-0\Fooocus_win64_2-5-0\Fooocus\outputs"
    if os.path.exists(out_dir):
        pngs = glob.glob(os.path.join(out_dir, "**", "*.png"), recursive=True)
        for p in pngs:
            try:
                ctime = os.path.getctime(p)
                fname = os.path.basename(p)
                if fname not in seen_filenames and os.path.getsize(p) > 50000:
                    seen_filenames.add(fname)
                    found_paths.append((ctime, p))
            except:
                pass

    found_paths.sort(key=lambda x: x[0])
    if len(found_paths) > count:
        found_paths = found_paths[-count:]

    stored_urls = []
    for ctime, pth in found_paths:
        dest_filename = f"{int(ctime)}_{os.path.basename(pth)}"
        dest_path = os.path.join(FIBBY_OUTPUTS_DIR, dest_filename)
        shutil.copy2(pth, dest_path)
        url = f"http://127.0.0.1:8000/outputs/{dest_filename}"
        stored_urls.append(url)
        print(f"[Fibby Storage] Stored {pth} -> {dest_path}")

    while len(stored_urls) < count and len(stored_urls) > 0:
        stored_urls.append(stored_urls[0])

    return stored_urls

@app.post("/api/inpaint")
async def inpaint(
    image: UploadFile = File(...),
    mask: UploadFile = File(default=None),
    prompt: str = Form(...),
    negative_prompt: str = Form(default=""),
    mask_points: str = Form(default="[]"),
    canvas_width: float = Form(default=512),
    canvas_height: float = Form(default=512),
    image_count: int = Form(default=2),
    auth_token: str = Form(default="")
):
    token_cost = image_count * 3
    if not auth_token:
        return JSONResponse(status_code=401, content={"error": "Authentication required. Please register or login."})

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM sessions WHERE token = ?", (auth_token,))
    s_row = cursor.fetchone()
    if not s_row:
        conn.close()
        return JSONResponse(status_code=401, content={"error": "Invalid or expired session token."})
    email = s_row[0]

    cursor.execute("SELECT tokens FROM users WHERE email = ?", (email,))
    u_row = cursor.fetchone()
    if not u_row or u_row[0] < token_cost:
        conn.close()
        return JSONResponse(status_code=400, content={"error": f"Insufficient tokens! Required: {token_cost} tokens ({image_count} images × 3), Available: {u_row[0] if u_row else 0} tokens."})

    current_tokens = u_row[0]
    new_tokens = current_tokens - token_cost
    cursor.execute("UPDATE users SET tokens = ? WHERE email = ?", (new_tokens, email))
    conn.commit()
    conn.close()

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

            print(f"[Playwright] Enabling 'Advanced' mode to set Image Number = {image_count}...")
            try:
                adv_chk = page.locator("label:has-text('Advanced') input[type='checkbox']").first
                if await adv_chk.count() > 0 and not await adv_chk.is_checked():
                    await adv_chk.check()

                await page.wait_for_selector("div:has-text('Image Number')", timeout=10000)
                await asyncio.sleep(0.5)

                for inp in await page.locator("input[type='number']").all():
                    p_text = await inp.evaluate("el => el.closest('.component, .form, div')?.innerText || ''")
                    if "Image Number" in p_text:
                        await inp.click()
                        await inp.fill(str(image_count))
                        await inp.press("Enter")
                        await inp.evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")
                        break
            except Exception as ex:
                print(f"[Playwright] Advanced/Image Number setting error: {ex}")

            print("[Playwright] Uploading base image into Inpaint Canvas slot...")
            inpaint_tab = page.locator("#component-70")
            fi = inpaint_tab.locator("input[type='file']").first
            await fi.set_input_files(image_path)
            await fi.evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")

            print("[Playwright] Waiting for canvas image preview to render...")
            await asyncio.sleep(2)

            canvas_el = inpaint_tab.locator("canvas").first
            await canvas_el.scroll_into_view_if_needed()
            await asyncio.sleep(1)

            print("[Playwright] Replaying optimized mask strokes instantly onto Fooocus canvas...")
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
            else:
                if box:
                    cx = box["x"] + box["width"] / 2
                    cy = box["y"] + box["height"] / 2
                    await page.mouse.move(cx - 80, cy - 80)
                    await page.mouse.down()
                    for r in range(10, 100, 15):
                        for angle in range(0, 360, 20):
                            import math
                            mx = cx + r * math.cos(math.radians(angle))
                            my = cy + r * math.sin(math.radians(angle))
                            await page.mouse.move(mx, my)
                    await page.mouse.up()

            print("[Playwright] Waiting for uploaded image preview to appear in Fooocus...")
            try:
                await page.wait_for_selector("#component-70 img, .image-container img, img[src*='blob:']", timeout=15000)
            except:
                pass

            await asyncio.sleep(3)

            print(f"[Playwright] Entering prompt into main box: '{prompt}'...")
            main_ta = page.locator("textarea[placeholder*='paste parameters'], textarea[placeholder*='Type prompt here or']").first
            if await main_ta.count() > 0:
                await main_ta.scroll_into_view_if_needed()
                await main_ta.click()
                await main_ta.fill(prompt)
                await main_ta.evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")
                await asyncio.sleep(0.5)

            if negative_prompt:
                neg_ta = page.locator("textarea[placeholder='Type prompt here.'], textarea[placeholder*='Describing what you do not want']").first
                if await neg_ta.count() > 0:
                    await neg_ta.scroll_into_view_if_needed()
                    await neg_ta.click()
                    await neg_ta.fill(negative_prompt)
                    await neg_ta.evaluate("el => { el.dispatchEvent(new Event('change', { bubbles: true })); el.dispatchEvent(new Event('input', { bubbles: true })); }")
                    await asyncio.sleep(0.5)

            start_time = time.time()

            print("[Playwright] Clicking Generate button...")
            await page.locator("#generate_button").click(force=True)

            print("[Playwright] Generation started! Waiting for Fooocus to finish processing...")

            try:
                await page.wait_for_selector("#stop_button", state="visible", timeout=20000)
            except Exception:
                pass

            await page.wait_for_selector("#stop_button", state="hidden", timeout=600000)
            print("[Playwright] Fooocus generation completed! Storing generated output files...")

            await asyncio.sleep(3)

            stored_urls = extract_and_store_generated_images(start_time=start_time, count=image_count)

            if not stored_urls or len(stored_urls) == 0:
                raise Exception("No generated output images found or stored.")

            await asyncio.sleep(1)
            await browser.close()

            return {"result": stored_urls, "tokens_remaining": new_tokens}

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
