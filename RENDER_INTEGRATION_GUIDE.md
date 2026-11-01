# Render "zerotrust" to Local Fibby Worker Integration Guide

This guide explains how to connect your **Render "zerotrust" app** to your local **Fibby GPU Worker** running on your computer with Fooocus.

---

## 1. Architecture Flow
1. **User** visits your **Render "zerotrust"** website.
2. User registers/logins (Render handles SQLite/PostgreSQL DB, 100 free signup tokens, and token deduction of `image_count * 3` tokens).
3. When the user clicks **Generate**, Render sends a secure POST webhook request to your **Local Fibby Worker** via a public tunnel URL.
4. Your **Local Fibby Worker** runs Playwright + Fooocus on your local GPU, generates the requested images (2 to 6 variations), stores them locally, and returns the image URLs back to Render.
5. Render displays the generated variations to the user.

---

## 2. Webhook Dispatch Code for Render ("zerotrust")
In your Render "zerotrust" backend (Node.js/Express or Python/FastAPI), when handling the `/api/inpaint` or generation request after deducting tokens, forward the payload to your local tunnel worker:

### Node.js / Express Example (on Render):
```javascript
const axios = require('axios');
const FormData = require('form-data');

async function forwardToLocalFibbyWorker(req, res) {
    try {
        const LOCAL_WORKER_URL = process.env.LOCAL_WORKER_URL; // e.g. https://my-fibby.loca.lt/api/inpaint

        const form = new FormData();
        form.append('image', req.files.image.data, { filename: 'base.png' });
        form.append('prompt', req.body.prompt);
        form.append('mask_points', req.body.mask_points || '[]');
        form.append('canvas_width', req.body.canvas_width || '512');
        form.append('canvas_height', req.body.canvas_height || '512');
        form.append('image_count', req.body.image_count || '2');

        const response = await axios.post(`${LOCAL_WORKER_URL}`, form, {
            headers: {
                ...form.getHeaders()
            },
            timeout: 600000 // 10 minutes timeout for SDXL generation
        });

        return res.json(response.data);
    } catch (error) {
        console.error('Local worker generation error:', error.message);
        return res.status(500).json({ error: 'Local AI worker generation failed.' });
    }
}
```

---

## 3. Exposing Your Local Fibby Worker via Public Tunnel
On your local computer where Fibby and Fooocus are running:

1. Start Fooocus:
   ```cmd
   cd C:\ai\Fooocus_win64_2-5-0\Fooocus_win64_2-5-0
   run.bat
   ```
2. Start Fibby Server:
   ```cmd
   cd C:\ai\focusclient
   python server.py
   ```
3. Expose Port 8000 securely to the internet using **LocalTunnel** or **Cloudflare Tunnel**:
   ```cmd
   npx localtunnel --port 8000
   ```
   This outputs a public URL (e.g. `https://some-name.loca.lt`).
4. Set **`LOCAL_WORKER_URL=https://some-name.loca.lt/api/inpaint`** as an Environment Variable in your Render "zerotrust" app dashboard!
