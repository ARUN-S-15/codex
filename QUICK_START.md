# 🚀 CODEX - Quick Start Guide

## ⚡ Get Your CODEX Working in 2 Minutes!

Your Judge0 local Docker setup has some configuration issues. Let's use **RapidAPI** instead - it's faster to set up and works perfectly!

---

## 📋 Option 1: RapidAPI (RECOMMENDED - Works Now!)

### Step 1: Get Your Free API Key (2 minutes)

1. Go to: https://rapidapi.com/judge0-official/api/judge0-ce
2. Click "Sign Up" (top right)
3. Create account with Google/GitHub/Email
4. Click "Subscribe to Test" → Select **BASIC (FREE)** plan
   - ✅ 50 requests/day FREE
   - ✅ No credit card needed
5. Copy your API key from the code example

### Step 2: Add Key to CODEX

1. Open `.env` file in your CODEX folder
2. Find this line:
   ```
   JUDGE0_API_KEY=
   ```
3. Paste your key:
   ```
   JUDGE0_API_KEY=your-actual-key-here
   ```
4. Save the file

### Step 3: Restart Flask

```powershell
# Stop Flask (press Ctrl+C in Flask terminal)
# Then start again:
python app.py
```

### Step 4: TEST IT!

1. Open: http://127.0.0.1:5000/compiler
2. Write code:
   ```python
   print("My CODEX works!")
   ```
3. Click "Run Code"
4. **See output instantly!** ✅

---

## 🐋 Option 2: Fix Docker (Advanced - Takes Time)

The local Judge0 Docker has connection issues between containers. This requires:

1. **Troubleshooting Docker networking**
2. **Checking firewall settings**
3. **Possibly rebuilding images**
4. **Can take 30-60 minutes to debug**

**Not recommended right now** - RapidAPI is faster!

---

## 📊 What's Already Working

✅ Flask app running on http://127.0.0.1:5000
✅ MySQL database connected
✅ Activity history system ready
✅ Code editor with syntax highlighting
✅ Multiple language support
✅ Debug, Optimize, Explain features
✅ Judge0 API failover configured

❓ **Just needs:** API key to execute code

---

## 🎯 Next Steps After Adding API Key

Once you add the RapidAPI key and restart Flask:

### Test All Features:
1. **Run Code** - Python, JavaScript, C, C++, Java
2. **Debug Code** - Get linter feedback
3. **Optimize Code** - Performance suggestions
4. **Explain Code** - Line-by-line analysis
5. **History** - See all your activities saved

### Try This Full Test:
```python
# Test all features with this code
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
```

- Click **Run** → See output
- Click **Debug** → Get code analysis
- Click **Optimize** → Get suggestions
- Click **Explain** → Understand the code
- Check **History** sidebar → See it saved!

---

## 💡 Why RapidAPI Instead of Docker?

| Feature | RapidAPI | Docker Local |
|---------|----------|--------------|
| Setup Time | 2 minutes | 30-60 minutes |
| Reliability | 99.9% | Needs debugging |
| Speed | Fast | Very fast (when working) |
| Maintenance | Zero | Regular updates |
| Free Tier | 50/day | Unlimited |
| Internet | Required | Not required |
| **Status** | ✅ **WORKS NOW** | ❌ Needs fixing |

**Winner:** RapidAPI for getting started fast!

---

## 🔧 If You Still Want Docker

I can help fix the Docker setup, but it will take more time. The issues are:

1. Redis container connectivity
2. Judge0 config file not loading properly
3. Network DNS resolution between containers

**Estimated time to fix:** 30-60 minutes
**Estimated time with RapidAPI:** 2 minutes

Your choice! 🚀

---

## ✅ Quick Decision Matrix

**Choose RapidAPI if:**
- ✅ You want to code NOW
- ✅ You're okay with 50 requests/day for testing
- ✅ You have internet connection
- ✅ You want zero maintenance

**Choose Docker if:**
- ✅ You need unlimited requests
- ✅ You have time to debug
- ✅ You want offline capability
- ✅ You're comfortable with Docker troubleshooting

---

## 📞 Need Help?

After you add the RapidAPI key, if anything doesn't work:

1. Check `.env` file (no spaces around `=`)
2. Restart Flask completely
3. Clear browser cache (Ctrl+Shift+Del)
4. Try in Incognito/Private mode

---

**🎊 Your CODEX is 2 minutes away from being fully operational!**

Just add that API key and start coding! 🚀💻
