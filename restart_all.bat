@echo off
echo ==================================================
echo   Stopping all Python, Node, and Cloudflare processes...
echo ==================================================
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
taskkill /f /im cloudflared.exe >nul 2>&1
echo All previous processes terminated.

echo ==================================================
echo   Starting Fibby Studio Unified Backend & Tunnel
echo ==================================================
cd /d C:\ai\focusclient
python run_backend.py
pause
