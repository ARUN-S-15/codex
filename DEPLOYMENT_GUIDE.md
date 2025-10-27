# 🚀 CODEX Deployment Guide - Make Your Website Live!

## 📋 Quick Comparison: Best Hosting Options

| Platform | Difficulty | Cost | Best For | Setup Time |
|----------|-----------|------|----------|------------|
| **Render** | ⭐ Easy | Free | Flask apps | 10 min |
| **Railway** | ⭐ Easy | Free | Full-stack | 10 min |
| **PythonAnywhere** | ⭐⭐ Medium | Free | Python apps | 15 min |
| **Heroku** | ⭐⭐ Medium | $5/mo | Production | 20 min |
| **Vercel** | ⭐⭐⭐ Hard | Free | Frontend only | N/A (won't work) |

---

## 🏆 **RECOMMENDED: Render.com** (EASIEST & FREE!)

### ✅ Why Render?
- ✨ **100% FREE** (no credit card needed)
- 🚀 **Automatic deployment** from GitHub
- 💾 **Free MySQL database** included
- 🔒 **Free SSL certificate** (HTTPS)
- 📊 **Easy monitoring** dashboard
- ⚡ **Fast setup** (10 minutes)

---

## 📖 Step-by-Step Guide: Deploy to Render

### **STEP 1: Prepare Your Code** ✅ (Already Done!)

Your project already has:
- ✅ `render.yaml` - Render configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `runtime.txt` - Python version
- ✅ `.env` template - Environment variables

---

### **STEP 2: Push Code to GitHub** (5 minutes)

#### Option A: Using GitHub Desktop (EASIEST)
1. Download **GitHub Desktop**: https://desktop.github.com/
2. Open GitHub Desktop
3. Click **"Add"** → **"Add Existing Repository"**
4. Select your folder: `E:\codex_1\codex`
5. Click **"Publish Repository"**
6. Uncheck **"Keep this code private"** (or keep checked)
7. Click **"Publish"**
8. Done! ✅

#### Option B: Using Git Command Line
```bash
# Navigate to your project
cd E:\codex_1\codex

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - CODEX platform"

# Create repository on GitHub.com first, then:
git remote add origin https://github.com/YOUR_USERNAME/codex.git
git branch -M master
git push -u origin master
```

---

### **STEP 3: Create Render Account** (2 minutes)

1. Go to: **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with **GitHub** (easiest) or email
4. Verify your email
5. Done! ✅

---

### **STEP 4: Deploy Your Website** (5 minutes)

#### 4.1 Connect GitHub
1. In Render Dashboard, click **"New +"**
2. Select **"Web Service"**
3. Click **"Connect GitHub"**
4. Authorize Render to access your repos
5. Select your **codex** repository

#### 4.2 Configure Service
Fill in these settings:

**Basic Settings:**
```
Name:                codex-platform
Environment:         Python 3
Region:              Choose closest to you (e.g., Oregon USA, Frankfurt EU, Singapore)
Branch:              master
Root Directory:      (leave empty)
```

**Build & Deploy:**
```
Build Command:       pip install -r requirements.txt
Start Command:       gunicorn app:app
```

**Instance Type:**
```
Select:              Free (512 MB RAM, Shared CPU)
```

#### 4.3 Add Environment Variables
Click **"Advanced"** → **"Add Environment Variable"**

Add these variables:

```env
# Required Variables
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this-12345
DB_TYPE=mysql

# MySQL Database (Render will provide these after creating database)
MYSQL_HOST=your-render-mysql-host
MYSQL_PORT=3306
MYSQL_USER=codex_user
MYSQL_PASSWORD=your-database-password
MYSQL_DATABASE=codex

# Google Gemini AI (for AI features)
GEMINI_API_KEY=your-gemini-api-key

# Judge0 API (for code execution)
JUDGE0_API_KEY=your-judge0-rapidapi-key

# Email Settings (optional - for password reset)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# OAuth (optional - for Google/GitHub login)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-secret
```

#### 4.4 Create MySQL Database
1. In Render Dashboard, click **"New +"**
2. Select **"MySQL"**
3. Fill in:
   ```
   Name:     codex-database
   Database: codex
   User:     codex_user
   Region:   Same as your web service
   Plan:     Free (1 GB storage)
   ```
4. Click **"Create Database"**
5. Wait 2-3 minutes for database to be ready
6. Copy the **Internal Database URL**
7. Go back to your **Web Service** → **Environment**
8. Update the MySQL variables with the database details

#### 4.5 Deploy!
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for first deployment
3. Watch the logs in real-time
4. When you see **"Your service is live"** → Done! ✅

---

### **STEP 5: Get Your Website URL** 🎉

Your website will be live at:
```
https://codex-platform.onrender.com
```

Or use a custom domain:
```
https://yourname.com
```

---

## 🎯 Alternative Option: Railway.app

### Why Railway?
- Also FREE
- Easier database setup
- Better performance
- $5 credit per month

### Quick Deploy to Railway:

1. **Sign up**: https://railway.app
2. **Click "New Project"**
3. **Deploy from GitHub repo**
4. **Add MySQL database** (1 click)
5. **Add environment variables**
6. **Deploy!**

Railway automatically:
- Detects Python app
- Installs dependencies
- Starts your app
- Provides HTTPS URL

---

## 🔑 Getting API Keys (Required)

### 1. Google Gemini API Key (FREE)
**For AI features (Explain, Debug, Optimize)**

1. Go to: https://makersuite.google.com/app/apikey
2. Click **"Get API Key"**
3. Click **"Create API key in new project"**
4. Copy the key
5. Add to environment variables: `GEMINI_API_KEY=your-key-here`

### 2. Judge0 RapidAPI Key (FREE)
**For code execution**

1. Go to: https://rapidapi.com/judge0-official/api/judge0-ce
2. Click **"Sign Up"** (free)
3. Click **"Subscribe to Test"**
4. Select **"Basic (Free)"** plan
5. Copy your **X-RapidAPI-Key**
6. Add to environment: `JUDGE0_API_KEY=your-key-here`

### 3. Gmail App Password (Optional)
**For password reset emails**

1. Go to: https://myaccount.google.com/apppasswords
2. Select **"Mail"** and **"Other"**
3. Enter "CODEX Platform"
4. Click **"Generate"**
5. Copy the 16-character password
6. Add to environment:
   ```
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   ```

---

## 🌐 Custom Domain (Optional)

### Free Domain Options:
1. **Freenom**: https://freenom.com (Free .tk, .ml, .ga domains)
2. **InfinityFree**: https://infinityfree.net (Free subdomain)
3. **No-IP**: https://noip.com (Free subdomain)

### Paid Domain (Recommended):
1. **Namecheap**: $8.88/year (.com)
2. **Google Domains**: $12/year
3. **Cloudflare**: $8.57/year + free SSL

### Connect Custom Domain to Render:
1. In Render Dashboard, go to your service
2. Click **"Settings"** → **"Custom Domain"**
3. Click **"Add Custom Domain"**
4. Enter your domain (e.g., `codex.yourname.com`)
5. Add the DNS records to your domain provider:
   ```
   Type: CNAME
   Name: codex (or @)
   Value: codex-platform.onrender.com
   ```
6. Wait 5-60 minutes for DNS propagation
7. Render will automatically provision SSL certificate

---

## 📊 Monitoring Your Website

### Render Dashboard:
- **Logs**: See real-time application logs
- **Metrics**: CPU, Memory, Request stats
- **Events**: Deployment history
- **Shell**: Access terminal (for debugging)

### Uptime Monitoring (Free):
1. **UptimeRobot**: https://uptimerobot.com
   - Monitors your site every 5 minutes
   - Email alerts if site is down
   - Free for up to 50 monitors

2. **Pingdom**: https://pingdom.com
   - Free tier available
   - Uptime reports

---

## 🚨 Common Issues & Solutions

### Issue 1: "Application Error" on Render
**Solution:**
- Check logs in Render dashboard
- Verify all environment variables are set
- Ensure `requirements.txt` has all dependencies
- Check database connection string

### Issue 2: "Module not found"
**Solution:**
- Add missing package to `requirements.txt`
- Redeploy (Render will reinstall)

### Issue 3: Database connection failed
**Solution:**
- Verify MySQL database is running
- Check database credentials in environment variables
- Ensure database URL is correct

### Issue 4: Judge0 code execution not working
**Solution:**
- Verify `JUDGE0_API_KEY` is set
- Check RapidAPI subscription is active
- Test API key at: https://rapidapi.com/judge0-official/api/judge0-ce

### Issue 5: AI features (Explain/Debug/Optimize) not working
**Solution:**
- Verify `GEMINI_API_KEY` is set
- Check Google AI Studio quota
- Test key at: https://makersuite.google.com

---

## 💰 Cost Breakdown

### FREE Tier (Render):
- ✅ Web service (512 MB RAM)
- ✅ MySQL database (1 GB storage)
- ✅ SSL certificate
- ✅ 750 hours/month runtime
- ⚠️ Sleeps after 15 min inactivity (wakes on request)

### Paid Tier ($7/month):
- ✅ Always online (no sleep)
- ✅ More RAM (1 GB+)
- ✅ Faster response times
- ✅ Custom domain included

---

## 🎯 Deployment Checklist

Before going live, ensure:

- [ ] All code pushed to GitHub
- [ ] Environment variables configured
- [ ] Database created and connected
- [ ] Gemini API key added (for AI features)
- [ ] Judge0 API key added (for code execution)
- [ ] Test website loads: `https://your-app.onrender.com`
- [ ] Test login/register works
- [ ] Test code execution works
- [ ] Test AI features work (if keys added)
- [ ] Custom domain configured (optional)
- [ ] Uptime monitoring set up (optional)

---

## 🚀 Quick Start Commands

### Update Your Code After Changes:
```bash
cd E:\codex_1\codex
git add .
git commit -m "Update: description of changes"
git push
```

Render will automatically redeploy! ⚡

---

## 📞 Need Help?

### Render Support:
- Docs: https://render.com/docs
- Community: https://community.render.com
- Status: https://status.render.com

### CODEX Issues:
- Check logs in Render dashboard
- Review environment variables
- Verify API keys are valid
- Test locally first: `python app.py`

---

## 🎉 Success! Your Website is Live!

**Share your CODEX platform:**
```
🌐 Website: https://codex-platform.onrender.com
📱 Mobile: Works on all devices!
🔒 Secure: HTTPS enabled
🚀 Fast: CDN powered
💻 Features:
   - Multi-language compiler
   - AI code assistant
   - 12 practice problems
   - Save & share projects
```

---

## 🔄 What's Next?

1. **Share with friends**: Post on social media
2. **Collect feedback**: Ask users what they like/need
3. **Add features**: Based on user requests
4. **Monitor usage**: Check analytics
5. **Upgrade if needed**: If you get lots of traffic

---

## 🏆 Comparison: All Hosting Options

| Feature | Render | Railway | PythonAnywhere | Heroku |
|---------|--------|---------|----------------|--------|
| **Free Tier** | ✅ Yes | ✅ Yes ($5 credit) | ✅ Yes | ❌ No ($7/mo) |
| **MySQL DB** | ✅ Free | ✅ Free | ❌ Paid only | ❌ Paid only |
| **SSL (HTTPS)** | ✅ Free | ✅ Free | ✅ Free | ✅ Free |
| **Custom Domain** | ✅ Free | ✅ Free | ❌ Paid only | ✅ Free |
| **Auto Deploy** | ✅ Yes | ✅ Yes | ❌ Manual | ✅ Yes |
| **Sleep/Idle** | ⚠️ 15 min | ⚠️ Yes | ❌ No | ⚠️ 30 min |
| **Setup Time** | 10 min | 10 min | 15 min | 20 min |
| **Difficulty** | ⭐ Easy | ⭐ Easy | ⭐⭐ Medium | ⭐⭐ Medium |

---

## ✅ My Recommendation

### For Beginners: **Render.com**
- Easiest setup
- Free forever
- Great documentation
- Good for learning

### For Serious Projects: **Railway.app**
- Better performance
- Easier database setup
- $5 credit/month (enough for small projects)
- Professional features

### For Long-term: **Paid Hosting**
- Heroku ($7/mo)
- DigitalOcean ($5/mo)
- AWS Lightsail ($3.50/mo)

---

**Start with Render (free), upgrade later if needed!** 🚀

Your CODEX platform will be live and accessible worldwide in just 15 minutes! 🌍
