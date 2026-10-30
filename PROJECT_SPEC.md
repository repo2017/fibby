# Project Specification: Fibby (AI Inpainting & Modification Studio)

> **OpenSpec AI Handover Document**
> This specification documents the architecture, workflows, and technical protocols of **Fibby** to allow any AI assistant or developer to understand, maintain, and extend the project seamlessly.

---

## 1. Executive Summary
**Fibby** is a web-based AI inpainting and modification studio that bridges a modern HTML5 Canvas frontend with a local instance of **Fooocus** (Stable Diffusion XL) running at `http://127.0.0.1:7865`. 
Because Fooocus does not expose named API endpoints (`api_name=None`) and requires full UI state, Fibby utilizes a **FastAPI backend (`server.py`)** powered by **Async Playwright browser automation** to control the local Fooocus UI programmatically.

---

## 2. Tech Stack & Requirements
* **Backend**: Python 3.10+, FastAPI, Uvicorn, Playwright (`playwright.async_api`).
* **Frontend**: Vanilla HTML5, CSS3, HTML5 Canvas API (custom drawing mask overlay).
* **AI Engine**: Local Fooocus instance (`http://127.0.0.1:7865`).
* **OS / Environment**: Windows (Python virtual environments, absolute paths, local filesystem outputs).

---

## 3. Architecture & File Structure
```
C:/ai/focusclient/
├── server.py              # FastAPI backend & Async Playwright Fooocus automation
├── index.html             # Web frontend (Canvas mask drawing & API client)
├── PROJECT_SPEC.md        # This OpenSpec AI handover document
└── temp_inputs/           # Temporary storage for uploaded base images & masks
```

---

## 4. Core Workflows & Technical Protocols

### A. Frontend Canvas Masking (`index.html`)
1. User uploads a base image (`imageUpload`).
2. Renders on an HTML5 `<canvas>` (`imageCanvas`).
3. User draws brush strokes over the image (rendered with Fooocus's signature red brush overlay `rgba(230, 40, 40, 0.6)`).
4. Upon clicking **Generate**, the client records the user's stroke points (`mask_points`) and canvas dimensions, sending a `FormData` request to `http://127.0.0.1:8000/api/inpaint`.

### B. Backend Automation (`server.py`)
1. **FastAPI Endpoint (`/api/inpaint`)**: Receives the base image, prompt, and stroke points.
2. **Playwright Automation**:
   - Launches a browser instance and navigates to `http://127.0.0.1:7865`.
   - Enables **Input Image** and switches to the **Inpaint or Outpaint** tab.
   - Sets the Inpaint Method to **Modify Content**.
   - Uploads the base image into Fooocus's primary input slot (`#component-70 input[type='file']`).
   - Replays the user's exact drawing coordinates onto Fooocus's canvas via Playwright mouse events (`page.mouse.move`, `page.mouse.down`, `page.mouse.up`).
   - Types the prompt into the main prompt textarea (`textarea.first`) and triggers `#generate_button`.
3. **Completion Detection & Output Extraction**:
   - Waits for Fooocus to process the generation cycle (`#stop_button` state visible -> hidden).
   - Scans output search directories (`Fooocus/outputs/` and `Temp/fooocus/`) using absolute file creation time (`os.path.getctime`) to extract the newly generated high-resolution SDXL output PNG.
   - Returns the file URL to the frontend for display.

---

## 5. Setup & Local Execution Guide
1. Start local Fooocus instance at `http://127.0.0.1:7865`.
2. Start the Fibby FastAPI server:
   ```bash
   python server.py
   ```
3. Open `http://127.0.0.1:8000/` in your browser.

---

## 6. Guidelines for Future AI Instances
* **Do not use raw HTTP/JSON APIs for Fooocus**: Fooocus runs Gradio blocks without named API endpoints (`api_name=None`). Always use Playwright browser automation.
* **Respect File Handling**: Always handle absolute paths and temporary cleanup in `server.py`.
* **Testing**: Use dedicated Python test scripts (`run_flower_direct.py`, `run_house_in_proc.py`) to verify end-to-end generation flows.
