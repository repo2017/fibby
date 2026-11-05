# Fibby Studio Cloud-Worker Integration Guide (v1.8.4)

This guide explains the complete architecture connecting your **Render Cloud Controller (`fibby.onrender.com`)** to your **Local GPU Worker** running Fooocus on your PC.

---

## 1. Architecture Flow
1. **User** visits **`fibby.onrender.com`**.
2. **Authentication & Tokens**: Render handles SQLite user registration, login, 100 free signup tokens, and token billing (`image_count * 3`).
3. **Async Job Dispatch**: When the user draws a mask and clicks Generate, Render dispatches an async job to your local PC via Cloudflare Tunnel (`cloudflared`).
4. **Local GPU Worker**: Your PC runs Playwright + Fooocus, generates the images, and stores them in `outputs/`.
5. **Image Proxy Stream**: Render securely streams the generated images back to the user's browser via `/api/outputs/{filename}` to bypass Cloudflare captchas and mobile download restrictions.

---

## 2. 1-Click Local Stack Management (`restart_all.bat`)
To run Fooocus, Cloudflare Tunnel, and Fibby Server together in a single clean process without multiple console windows:
1. Double-click **`restart_all.bat`** in `C:\ai\focusclient\`.
2. It automatically kills any stray processes, starts Fooocus, opens a rock-solid Cloudflare Quick Tunnel (`trycloudflare.com`), and boots the FastAPI server on port 8000.

---

## 3. Environment Variables (Render Dashboard)
In your Render Dashboard (`dashboard.render.com`) -> your Fibby service -> **Environment**:
- **`LOCAL_WORKER_URL`**: Set to your active Cloudflare tunnel endpoint (e.g. `https://<your-tunnel>.trycloudflare.com/api/inpaint`).
