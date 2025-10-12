# 🔧 Judge0 Connection Fix - Complete Guide

## ❌ Problem
Cannot connect to Judge0 API - code won't run.

## ✅ Solutions (Choose One)

---

### Solution 1: Use Local Judge0 (RECOMMENDED - No Internet Needed!)

#### Step 1: Install Docker Desktop
1. Download from: https://www.docker.com/products/docker-desktop
2. Install and start Docker Desktop
3. Wait for Docker to fully start (whale icon in system tray)

#### Step 2: Start Judge0
```powershell
# Quick start
python start_judge0.py

# Or manually
cd Judge0
docker-compose up -d
```

#### Step 3: Verify
```powershell
# Check status
python start_judge0.py status

# Or check Docker directly
docker ps
```

You should see 3 containers running:
- judge0-api-1
- judge0-db-1
- judge0-redis-1

#### Step 4: Test
- Go to http://127.0.0.1:5000/compiler
- Write some code
- Click "Run Code"
- Should work instantly! ⚡

---

### Solution 2: Use RapidAPI (Requires Signup)

#### Step 1: Get API Key
1. Go to: https://rapidapi.com/judge0-official/api/judge0-ce
2. Sign up for free account
3. Subscribe to free tier (0-50 requests/day)
4. Copy your API key

#### Step 2: Add to .env File
Edit `e:\codex_1\codex\.env`:
```env
JUDGE0_API_KEY=your-rapidapi-key-here
```

#### Step 3: Restart Flask
```powershell
python app.py
```

---

### Solution 3: Use Free Public API (May Be Slow/Unreliable)

The app will automatically try https://ce.judge0.com if:
- Docker is not running
- RapidAPI key is not set

**Note:** This is the least reliable option due to:
- Rate limiting
- Network connectivity issues
- High latency

---

## 🧪 Test Each Endpoint

### Test Local Judge0:
```powershell
curl http://localhost:2358/about
```

Should return Judge0 version info.

### Test Public API:
```powershell
curl https://ce.judge0.com/about
```

Should return Judge0 info (if accessible).

---

## 🛠️ Quick Commands

### Start Judge0:
```powershell
python start_judge0.py
```

### Stop Judge0:
```powershell
python start_judge0.py stop
```

### Check Status:
```powershell
python start_judge0.py status
```

### View Logs:
```powershell
cd Judge0
docker-compose logs -f
```

### Restart Judge0:
```powershell
cd Judge0
docker-compose restart
```

---

## 🐛 Troubleshooting

### Error: "Docker not found"
**Solution:**
- Install Docker Desktop
- Restart your computer after installation
- Make sure Docker Desktop is running

### Error: "Cannot connect to Docker daemon"
**Solution:**
- Start Docker Desktop application
- Wait for it to fully start (green icon in system tray)
- Try again

### Error: "Port 2358 already in use"
**Solution:**
```powershell
# Find what's using the port
netstat -ano | findstr :2358

# Kill the process (replace PID with the number from above)
taskkill /PID <PID> /F

# Restart Judge0
python start_judge0.py
```

### Error: "Containers start but API not responding"
**Solution:**
```powershell
# Check container logs
cd Judge0
docker-compose logs api

# Restart containers
docker-compose restart

# If still fails, rebuild
docker-compose down
docker-compose up -d --build
```

### Error: "Timeout waiting for execution"
**Possible causes:**
- Judge0 containers not fully started
- Infinite loop in your code
- Very slow code execution

**Solution:**
- Wait a minute and try again
- Check your code for infinite loops
- Restart Judge0 containers

---

## ⚡ Performance Comparison

| Method | Speed | Reliability | Internet | Setup |
|--------|-------|-------------|----------|-------|
| **Local Docker** | ⚡⚡⚡ Very Fast | ✅ Excellent | ❌ Not Needed | 🔧 Medium |
| **RapidAPI** | ⚡⚡ Fast | ✅ Good | ✅ Required | 🔧 Easy |
| **Public API** | ⚡ Slow | ⚠️ Unreliable | ✅ Required | 🔧 None |

**Recommendation:** Use Local Docker for best experience!

---

## 📊 Current Configuration

Your app tries endpoints in this order:

1. **http://localhost:2358** (Local Docker)
   - Timeout: 3 seconds
   - No internet needed
   - Fastest option

2. **https://judge0-ce.p.rapidapi.com** (RapidAPI)
   - Timeout: 8 seconds
   - Requires API key
   - Skip if no key

3. **https://ce.judge0.com** (Public)
   - Timeout: 8 seconds
   - May be slow/blocked
   - Last resort

---

## 🎯 Recommended Setup

### For Development (Local):
```powershell
# One-time setup
python start_judge0.py

# Daily use
# Just start Docker Desktop, Judge0 auto-starts
```

### For Production (Server):
```powershell
# Option 1: Deploy Judge0 with your app
docker-compose up -d

# Option 2: Use RapidAPI with paid tier
# Add key to .env file
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Docker Desktop installed and running
- [ ] Judge0 containers running (`docker ps`)
- [ ] API responds (`curl http://localhost:2358/about`)
- [ ] Flask app running (`python app.py`)
- [ ] Can run Python code in compiler
- [ ] Can run C code in compiler
- [ ] Can run Java code in compiler
- [ ] History saves activities
- [ ] Debug button works
- [ ] Explain button works

---

## 💡 Pro Tips

1. **Auto-start Judge0:**
   - Docker Desktop can auto-start Judge0 on boot
   - Set `restart: always` in docker-compose.yml (already set)

2. **Save Resources:**
   - Stop Judge0 when not coding:
     ```powershell
     python start_judge0.py stop
     ```

3. **Monitor Performance:**
   - Check container stats:
     ```powershell
     docker stats
     ```

4. **Update Judge0:**
   ```powershell
   cd Judge0
   docker-compose pull
   docker-compose up -d
   ```

---

## 🎊 Success Indicators

When everything works:

✅ Flask app shows: `✅ MySQL database 'CODEX' initialized successfully!`
✅ Judge0 responds: `curl http://localhost:2358/about`
✅ Code runs instantly in compiler
✅ No error messages
✅ History saves activities
✅ All language support working

---

**Your Judge0 setup is ready when all 3 containers are running!** 🚀

Check status: `docker ps` or `python start_judge0.py status`
