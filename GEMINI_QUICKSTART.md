# 🚀 Quick Start: Enable AI Features

## Step 1: Get Your FREE Gemini API Key (2 minutes)

1. Visit: **https://aistudio.google.com/app/apikey**
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Choose **"Create API key in new project"**
5. Copy your API key (starts with `AIzaSy...`)

## Step 2: Add to .env File (1 minute)

Create a file named `.env` in your project root (if it doesn't exist):

```bash
# .env file
GEMINI_API_KEY=AIzaSyA_paste_your_actual_key_here
```

**Important:** 
- Replace `AIzaSyA_paste_your_actual_key_here` with your actual key
- Don't share this file or commit it to Git
- `.env` is already in `.gitignore`

## Step 3: Restart Your App

```bash
python app.py
```

## ✅ That's It!

Your app now has:
- 🤖 AI-powered code explanations for ALL languages
- ⚡ Intelligent code optimization
- 🎯 Context-aware analysis
- 📚 Educational insights

## 🎮 Try It Now!

1. **Explain Code**: Paste any code → Click "Explain" → Get intelligent breakdown
2. **Optimize Code**: Write inefficient code → Click "Optimize" → See improvements

## ⚠️ Troubleshooting

**"GEMINI_API_KEY not found" warning?**
- Make sure `.env` file is in the root folder (same as `app.py`)
- Check there's no space before or after the `=` sign
- Restart the app after adding the key

**Still doesn't work?**
- Check if `.env` file has the correct name (not `.env.txt`)
- Use absolute path: Check file location matches your app

## 🔒 Free Tier Limits

- ✅ 15 requests per minute
- ✅ 1,500 requests per day  
- ✅ Perfect for learning and development!

---

**Need help?** Check `AI_SETUP_GUIDE.md` for detailed instructions!
