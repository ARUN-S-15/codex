# 🚀 Quick Deploy Guide - Get CODEX Online in 15 Minutes!

## ✅ What You'll Get
- 🌐 Public URL: `https://your-codex.onrender.com`
- 📱 Works on all devices (mobile, tablet, desktop)
- 🔒 HTTPS enabled (secure)
- 🆓 Completely FREE hosting
- 🔄 Auto-deploy when you push to GitHub

---

## 📋 Step-by-Step Deployment

### **STEP 1: Push Code to GitHub** (3 minutes)

Your code is ready! Just commit and push:

```powershell
# Add all changes
git add .

# Commit with message
git commit -m "Ready for deployment - Google OAuth configured"

# Push to GitHub
git push origin master
```

**Don't have the remote set up?** Run this first:
```powershell
# Go to GitHub.com and create a new repository called "codex"
# Then run:
git remote add origin https://github.com/ESAKKIKANNANP/codex.git
git push -u origin master
```

---

### **STEP 2: Create Render Account** (2 minutes)

1. Go to: **https://render.com**
2. Click **"Get Started for Free"**
3. Sign up with **GitHub** (easiest option)
4. Authorize Render to access your repositories
5. ✅ Done!

---

### **STEP 3: Deploy to Render** (10 minutes)

#### 3.1 Create Web Service

1. In Render Dashboard, click **"New +"** button
2. Select **"Web Service"**
3. Click **"Connect a repository"**
4. Select your **"codex"** repository
5. Click **"Connect"**

#### 3.2 Configure Service

Fill in these settings:

```
Name:              codex-platform
Environment:       Python 3
Region:            Oregon (USA) - or closest to you
Branch:            master
Root Directory:    (leave blank)
Build Command:     pip install -r requirements.txt
Start Command:     gunicorn app:app --bind 0.0.0.0:$PORT
Instance Type:     Free
```

#### 3.3 Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**

Add these **REQUIRED** variables:

```env
# Flask Configuration
FLASK_ENV=production
SECRET_KEY=a7f9d8e6c4b2a1f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1

# Database (we'll add MySQL next)
DB_TYPE=mysql

# Google Gemini AI (already have)
GEMINI_API_KEY=AIzaSyB1sXQQb23SDvakAAm9RYflw0d9wlVYSqU

# Google OAuth (already configured)
GOOGLE_CLIENT_ID=698286024055-pjdn05lr364hfcsbipq17o9uldfioie8.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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

# Judge0 (optional - add if you have RapidAPI key)
JUDGE0_API_KEY=your-judge0-key-if-you-have
```

**Don't click "Create Web Service" yet!** We need to set up the database first.

---

### **STEP 4: Create MySQL Database** (5 minutes)

#### 4.1 Create Database

1. Click **"New +"** button again
2. Select **"MySQL"**
3. Fill in:
   ```
   Name:          codex-database
   Database:      codex
   User:          codex_user
   Region:        Same as your web service (Oregon)
   MySQL Version: 8.0
   Plan:          Free (1 GB storage)
   ```
4. Click **"Create Database"**
5. Wait 2-3 minutes for provisioning

#### 4.2 Get Database Connection Info

1. Click on your new database
2. Scroll down to **"Connections"**
3. Copy the **Internal Database URL** (looks like: `mysql://user:pass@host:port/dbname`)

Example:
```
mysql://codex_user:abc123xyz@codex-database.internal:3306/codex
```

Parse this into:
- **Host**: `codex-database.internal`
- **Port**: `3306`
- **User**: `codex_user`
- **Password**: `abc123xyz`
- **Database**: `codex`

#### 4.3 Add Database Variables to Web Service

1. Go back to your **Web Service** (codex-platform)
2. Click **"Environment"** in left sidebar
3. Click **"Add Environment Variable"**
4. Add these:

```env
MYSQL_HOST=your-internal-database-host
MYSQL_PORT=3306
MYSQL_USER=codex_user
MYSQL_PASSWORD=your-database-password
MYSQL_DATABASE=codex
```

---

### **STEP 5: Deploy!** 🚀

1. Click **"Create Web Service"** (if first time)
   OR
   Click **"Manual Deploy"** → **"Deploy latest commit"** (if already created)

2. Watch the deployment logs in real-time
3. You'll see:
   ```
   ==> Building...
   ==> Installing dependencies...
   ==> Starting server...
   ==> Your service is live! 🎉
   ```

4. Wait 5-10 minutes for first deployment

---

### **STEP 6: Update Google OAuth Redirect URI** (2 minutes)

Your app is now live! Update Google OAuth:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Click your OAuth Client ID
3. Add new **Authorized redirect URI**:
   ```
   https://codex-platform.onrender.com/login/google/callback
   ```
   *(Replace `codex-platform` with your actual Render app name)*

4. Click **"SAVE"**
5. Wait 1-2 minutes for Google to update

---

## 🎉 YOU'RE LIVE!

Your CODEX platform is now accessible at:
```
https://codex-platform.onrender.com
```

**Share this URL with anyone to test on their devices!** 📱💻🖥️

---

## 📱 Test on Other Devices

### Test on Your Phone:
1. Open browser on phone
2. Go to: `https://codex-platform.onrender.com`
3. Test login with Google
4. Test code execution
5. Test all features

### Test on Friend's Device:
1. Share the URL
2. They can create account or use Google login
3. Test features work properly

---

## ⚠️ Important Notes

### Free Tier Limitations:
- **Sleeps after 15 minutes** of inactivity
- First request after sleep takes 30-60 seconds to wake up
- **750 hours/month** of runtime (enough for testing)
- **512 MB RAM** (sufficient for your app)

### To Stay Always Online:
Upgrade to **Starter Plan** ($7/month):
- No sleep
- 1 GB RAM
- Faster performance
- Custom domain

---

## 🔄 Auto-Deploy Updates

Every time you push to GitHub, Render automatically redeploys!

```powershell
# Make changes to your code
# Then:
git add .
git commit -m "Update feature X"
git push origin master

# Render automatically redeploys in 3-5 minutes! 🎉
```

---

## 🐛 Troubleshooting

### Issue: "Application Error"
**Solution:**
1. Check logs in Render dashboard
2. Look for Python errors
3. Verify all environment variables are set

### Issue: Database Connection Failed
**Solution:**
1. Verify MySQL database is running
2. Check database credentials match
3. Use **Internal Database URL** (not external)

### Issue: Google OAuth Not Working
**Solution:**
1. Verify redirect URI is added in Google Console
2. Check CLIENT_ID and CLIENT_SECRET are correct
3. Wait 1-2 minutes after updating Google Console

### Issue: Judge0 Not Working
**Solution:**
- Judge0 public API should work by default
- If slow, sign up for RapidAPI Judge0 (free tier)
- Add `JUDGE0_API_KEY` environment variable

---

## 📊 Monitor Your App

### View Logs:
1. Go to Render Dashboard
2. Click on your web service
3. Click **"Logs"** tab
4. See real-time application logs

### View Metrics:
1. Click **"Metrics"** tab
2. See CPU, Memory, Request stats

---

## 🎯 Next Steps After Deployment

1. ✅ Test all features on mobile device
2. ✅ Share URL with friends for feedback
3. ✅ Monitor logs for errors
4. ✅ Set up uptime monitoring: https://uptimerobot.com
5. ✅ Consider custom domain (optional)

---

## 💡 Pro Tips

### Keep App Awake (Free):
Use a service like **UptimeRobot** to ping your app every 5 minutes:
1. Sign up: https://uptimerobot.com
2. Add monitor with your URL
3. Set interval to 5 minutes
4. App never sleeps! 🎉

### Custom Domain:
1. Buy domain from Namecheap ($8/year)
2. In Render, go to Settings → Custom Domain
3. Add your domain
4. Update DNS records
5. Free SSL certificate automatically provisioned!

---

## 🌟 Your Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web service created and configured
- [ ] MySQL database created and connected
- [ ] Environment variables added
- [ ] Google OAuth redirect URI updated
- [ ] Deployment successful (check logs)
- [ ] Website loads in browser
- [ ] Login/Register works
- [ ] Google OAuth works
- [ ] Code execution works
- [ ] Tested on mobile device
- [ ] Shared URL with friends

---

**You're all set! Your CODEX platform is live and ready for testing!** 🚀

Need help? Check the full **DEPLOYMENT_GUIDE.md** for detailed troubleshooting.
