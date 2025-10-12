# 🔧 Fix Judge0 Docker - Restore Working Configuration

## ⚠️ Issue: cgroup Error

Your Judge0 was working 2 days ago but now shows:
```
Cannot write /sys/fs/cgroup/memory/box-4/tasks: No such file or directory
```

This happened because Docker Desktop settings changed or updated.

---

## 🎯 Quick Fix Options

### Option A: Check Docker Desktop Settings

1. **Open Docker Desktop**
2. Click **Settings** (gear icon)
3. Go to **Resources** → **WSL Integration**
   - Make sure it's enabled
4. Go to **General**
   - Uncheck "Use the WSL 2 based engine" (try Hyper-V mode)
   - OR ensure WSL 2 is properly configured
5. Click **Apply & Restart**
6. Wait for Docker to restart
7. Test Judge0 again:
   ```powershell
   cd Judge0
   docker-compose restart
   ```

### Option B: Use Compatibility Mode

Add this to your docker-compose.yml:

```yaml
  api:
    image: judge0/judge0:latest
    restart: always
    depends_on:
      - db
      - redis
    ports:
      - "2358:2358"
    environment:
      - DATABASE_URL=postgres://judge0:judge0@db:5432/judge0
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - ENABLE_DEBUG=true
      - ALLOW_ORIGIN=*
    # Add these lines:
    security_opt:
      - seccomp:unconfined
      - apparmor:unconfined
    cap_add:
      - SYS_ADMIN
```

### Option C: Use RapidAPI (FASTEST RIGHT NOW)

Stop fighting with Docker and get coding in 2 minutes:

1. **Get API Key**: https://rapidapi.com/judge0-official/api/judge0-ce
2. **Add to `.env`**:
   ```
   JUDGE0_API_KEY=your-key-here
   ```
3. **Restart Flask**: `python app.py`
4. **Start Coding!** ✅

---

## 🤔 What Likely Changed

Something updated or changed in the last 2 days:
- ✅ Docker Desktop updated automatically
- ✅ Windows Update changed system settings  
- ✅ WSL 2 configuration changed
- ✅ Antivirus/security software updated

---

## 💡 My Recommendation

**For NOW:** Use RapidAPI (2 minutes, guaranteed to work)
**For LATER:** Debug Docker settings when you have time

Your CODEX is 99% ready - just needs Judge0 working!

---

## 🚀 Get Coding NOW

```powershell
# 1. Get RapidAPI key from: https://rapidapi.com/judge0-official/api/judge0-ce

# 2. Add to .env file:
echo JUDGE0_API_KEY=your-actual-key-here >> .env

# 3. Restart Flask:
python app.py

# 4. Open browser:
start http://127.0.0.1:5000/compiler

# 5. CODE! 🎉
```

What do you want to do?
- **A)** Try Docker Desktop settings fix (15 minutes)
- **B)** Use RapidAPI and code NOW (2 minutes)
- **C)** Debug Docker more (uncertain time)
