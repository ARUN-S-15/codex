# Judge0 Setup Guide - Fix Connection Errors

## Problem
You're seeing this error:
```
⚠️ Error communicating with Judge0: HTTPSConnectionPool... Failed to resolve 'ce.judge0.com'
```

This means your app cannot connect to the Judge0 API server.

---

## ✅ Solution 1: Use Local Judge0 (RECOMMENDED)

Running Judge0 locally is **faster, more reliable, and works offline**!

### Step 1: Install Docker Desktop
1. Download Docker Desktop: https://www.docker.com/products/docker-desktop
2. Install and start Docker Desktop
3. Wait for Docker to fully start (you'll see the Docker icon in your system tray)

### Step 2: Start Judge0
1. Open PowerShell or Command Prompt
2. Navigate to your project's `Judge0` folder:
   ```powershell
   cd E:\codex_1\codex\Judge0
   ```
3. Start Judge0 with Docker Compose:
   ```powershell
   docker-compose up -d
   ```
4. Wait 30 seconds for all services to start

### Step 3: Test It
1. Open your browser and go to: http://localhost:2358
2. You should see the Judge0 API info
3. Now run your code in the CODEX app - it will automatically use the local Judge0!

### Stop Judge0 (when done)
```powershell
docker-compose down
```

---

## ✅ Solution 2: Check Internet Connection

### Test Judge0 API
1. Open your browser
2. Go to: https://ce.judge0.com
3. If it doesn't load, check:
   - Is your internet working?
   - Is your firewall blocking it?
   - Is your antivirus blocking Python/Flask?

### Fix Firewall Issues
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Find Python and check both Private and Public boxes
4. Click OK and try again

---

## ✅ Solution 3: Use RapidAPI (Alternative)

If local Judge0 doesn't work and you have internet issues:

### Step 1: Get API Key
1. Go to: https://rapidapi.com/judge0-official/api/judge0-ce
2. Sign up (free tier available)
3. Subscribe to the free plan
4. Copy your API key

### Step 2: Add Key to app.py
1. Open `app.py`
2. Find this line (near the top):
   ```python
   RAPIDAPI_KEY = None
   ```
3. Change it to:
   ```python
   RAPIDAPI_KEY = "your-api-key-here"
   ```
4. Save and restart your Flask app

---

## 🔍 Troubleshooting

### "Docker command not found"
- Docker is not installed or not in PATH
- Restart your computer after installing Docker
- Make sure Docker Desktop is running

### "Port 2358 already in use"
- Judge0 is already running - that's good!
- Or another app is using that port
- Stop the other app or change the port in `docker-compose.yml`

### "Connection refused on localhost:2358"
- Judge0 services are still starting (wait 30-60 seconds)
- Run `docker-compose ps` to check if all services are "Up"
- Run `docker-compose logs` to see any errors

### Still not working?
1. Stop Judge0: `docker-compose down`
2. Remove old containers: `docker-compose down -v`
3. Pull fresh images: `docker-compose pull`
4. Start again: `docker-compose up -d`

---

## 📊 Which Solution to Choose?

| Solution | Speed | Reliability | Offline | Setup Time |
|----------|-------|-------------|---------|------------|
| **Local Judge0 (Docker)** | ⚡ Fastest | ✅ Best | ✅ Yes | 5-10 min |
| **RapidAPI** | 🐌 Slower | ✅ Good | ❌ No | 2 min |
| **Free API (ce.judge0.com)** | 🐌 Slowest | ⚠️ Unreliable | ❌ No | 0 min |

**Recommendation**: Use Local Judge0 with Docker for the best experience!

---

## 🎯 Quick Start Commands

```powershell
# Navigate to project
cd E:\codex_1\codex

# Start Judge0 (in Judge0 folder)
cd Judge0
docker-compose up -d

# Wait 30 seconds, then test
# Open browser: http://localhost:2358

# Run your Flask app (in main folder)
cd ..
python app.py

# When done, stop Judge0
cd Judge0
docker-compose down
```

---

## ✨ Tips

1. **Keep Docker Running**: Leave Docker Desktop running while developing
2. **Auto-start**: Docker can start Judge0 automatically on boot
3. **Check Status**: Use `docker-compose ps` to see running services
4. **View Logs**: Use `docker-compose logs -f` to see what's happening
5. **Reset Everything**: Use `docker-compose down -v && docker-compose up -d` for a fresh start

---

**Need more help?** Check the official Judge0 docs: https://github.com/judge0/judge0
