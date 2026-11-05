# Fibby Studio Cloud-Worker Integration Guide (v1.9.3)

This guide documents the final production-ready architecture connecting your **Render Cloud Controller (`fibby.onrender.com`)** to your **Local GPU Worker**.

---

## 1. Architecture & Startup Flow
1. **1-Click Local Startup (`restart_all.bat` / `run_backend.py`)**:
   - Automatically starts Fooocus (`port 7865`).
   - Starts the **FastAPI server (`port 8000`) first** and verifies it is live (`200 OK`).
   - Starts the **Cloudflare Tunnel (`cloudflared`)** and automatically pushes the fresh live URL to Render via `/api/update-worker-url`.
2. **Render Cloud Controller (`fibby.onrender.com`)**:
   - Handles SQLite user authentication (`users.db`), 100 free signup tokens, and token billing (`image_count * 3`).
   - Persists the active Cloudflare tunnel URL in SQLite so it survives Render restarts and sleep mode.
   - Forwards generation tasks securely across the tunnel using a **Secret Header Barrier (`X-Fibby-Secret: fibby_secret_123`)** to protect your PC GPU from public internet hijacking.
3. **Secure Image Proxy Stream (`/api/outputs/{filename}?token=...`)**:
   - Token-gated image access control ensures that only the exact user who paid tokens and generated the images can view or download them.
