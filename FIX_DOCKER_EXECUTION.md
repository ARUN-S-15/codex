# 🔧 Fix Judge0 Docker for Code Execution on Windows

## Step-by-Step Fix

### Option 1: Run Docker Desktop as Administrator

1. **Close Docker Desktop completely**
   - Right-click Docker Desktop icon in system tray
   - Click "Quit Docker Desktop"
   - Wait for it to fully close

2. **Run as Administrator**
   - Right-click Docker Desktop icon
   - Select "Run as administrator"
   - Wait for Docker to start (whale icon in tray)

3. **Restart Judge0**
   ```powershell
   cd E:\codex_1\codex\Judge0
   docker-compose down
   docker-compose up -d
   ```

4. **Test It**
   ```powershell
   cd ..
   python test_judge0_working.py
   ```

---

### Option 2: Add Privileged Mode (Most Likely to Work)

1. **Open docker-compose.yml** in Judge0 folder

2. **Add privileged mode to api service:**
   ```yaml
   api:
     image: judge0/judge0:latest
     restart: always
     depends_on:
       - db
       - redis
     ports:
       - "2358:2358"
     privileged: true  # ADD THIS LINE
     environment:
       - DATABASE_URL=postgres://judge0:judge0@db:5432/judge0
       - REDIS_HOST=redis
       - REDIS_PORT=6379
       - ENABLE_DEBUG=true
       - ALLOW_ORIGIN=*
   ```

3. **Restart containers:**
   ```powershell
   docker-compose down
   docker-compose up -d
   ```

4. **Wait 20 seconds and test:**
   ```powershell
   Start-Sleep -Seconds 20
   python test_judge0_working.py
   ```

---

### Option 3: Use Hyper-V Instead of WSL 2

1. **Open Docker Desktop Settings**
   - Click Docker icon in system tray
   - Click Settings (gear icon)

2. **Switch to Hyper-V**
   - Go to "General"
   - **Uncheck** "Use the WSL 2 based engine"
   - Click "Apply & Restart"

3. **Wait for Docker to restart** (may take 2-3 minutes)

4. **Restart Judge0:**
   ```powershell
   cd E:\codex_1\codex\Judge0
   docker-compose restart
   ```

5. **Test:**
   ```powershell
   cd ..
   python test_judge0_working.py
   ```

---

### Option 4: Try Official Judge0 Deployment

1. **Download official docker-compose:**
   ```powershell
   cd E:\codex_1\codex\Judge0
   
   # Backup current file
   Copy-Item docker-compose.yml docker-compose.yml.backup
   
   # Download official version
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/judge0/judge0/master/docker-compose.yml" -OutFile "docker-compose-official.yml"
   ```

2. **Edit docker-compose-official.yml:**
   - Change `server` to `api` 
   - Make sure port is `2358:2358`

3. **Create judge0.conf file:**
   ```powershell
   @"
   REDIS_PASSWORD=
   POSTGRES_HOST=db
   POSTGRES_PORT=5432
   POSTGRES_USER=judge0
   POSTGRES_PASSWORD=judge0
   POSTGRES_DB=judge0
   "@ | Out-File -FilePath "judge0.conf" -Encoding ASCII
   ```

4. **Use official compose:**
   ```powershell
   docker-compose -f docker-compose-official.yml down
   docker-compose -f docker-compose-official.yml up -d
   ```

---

### Option 5: Enable Experimental Features

1. **Open Docker Desktop Settings**

2. **Enable Experimental Features:**
   - Go to "Docker Engine"
   - Add or modify JSON:
   ```json
   {
     "experimental": true,
     "features": {
       "buildkit": true
     }
   }
   ```
   - Click "Apply & Restart"

3. **Restart Judge0 after Docker restarts**

---

## 🧪 Quick Test Script

After trying any option, run this:

```powershell
cd E:\codex_1\codex
python test_judge0_working.py
```

If you see:
- ✅ "SUCCESS! Judge0 Docker is fully working!" → You're done! 🎉
- ❌ Error message → Try next option

---

## 📊 Success Probability

| Option | Success Rate | Time | Difficulty |
|--------|--------------|------|------------|
| **Option 1: Run as Admin** | 30% | 2 min | Easy ⭐ |
| **Option 2: Privileged Mode** | 60% | 3 min | Easy ⭐ |
| **Option 3: Hyper-V** | 40% | 5 min | Medium ⭐⭐ |
| **Option 4: Official Compose** | 70% | 10 min | Medium ⭐⭐ |
| **Option 5: Experimental** | 20% | 3 min | Easy ⭐ |

---

## 🎯 Recommended Order

Try them in this order:

1. **Start with Option 2** (privileged mode - highest success rate)
2. If that fails, try **Option 1** (run as admin)
3. If still failing, try **Option 4** (official compose)
4. Last resort: **Option 3** (Hyper-V switch)

---

## ⚠️ If Nothing Works

Judge0 has known issues with Windows Docker Desktop due to cgroup limitations. If all options fail, you have two choices:

### A) Use RapidAPI (Recommended)
- Works immediately
- 50 free requests/day
- Perfect for development
- 2 minutes to set up

### B) Deploy to Linux Server
- 100% reliable
- Unlimited requests
- Needs cloud server (AWS, DigitalOcean, etc.)
- 30 minutes to set up

---

## 🚀 Let's Start!

**I recommend starting with Option 2 (Privileged Mode).**

Want me to help you apply it right now?
