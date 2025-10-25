# 🔐 Complete Setup Guide: Email & OAuth Authentication

**Last Updated**: October 25, 2025  
**Estimated Time**: 30-45 minutes  
**Difficulty**: Beginner-Friendly

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Part 1: Enable Email System](#part-1-enable-email-system)
3. [Part 2: Enable Google OAuth](#part-2-enable-google-oauth)
4. [Part 3: Enable GitHub OAuth](#part-3-enable-github-oauth)
5. [Part 4: Update Login Page](#part-4-update-login-page)
6. [Part 5: Testing & Verification](#part-5-testing--verification)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, make sure you have:

- ✅ CODEX platform running locally
- ✅ Gmail account (for email system)
- ✅ Google account (for Google OAuth)
- ✅ GitHub account (for GitHub OAuth)
- ✅ Text editor open (VS Code, Notepad++, etc.)
- ✅ Browser ready (Chrome, Firefox, Edge)

---

## Part 1: Enable Email System

**Time Required**: ~10 minutes  
**Purpose**: Send verification emails, password resets, and welcome messages

### Step 1.1: Enable 2-Step Verification on Gmail

1. **Open Google Account Security**
   - Go to: https://myaccount.google.com/security
   - Or: Gmail → Profile Picture → "Manage your Google Account" → Security

2. **Find "2-Step Verification"**
   - Scroll down to "How you sign in to Google"
   - Click on **"2-Step Verification"**

3. **Set Up 2-Step Verification** (if not already enabled)
   - Click **"Get Started"**
   - Enter your password
   - Add phone number
   - Enter verification code sent to your phone
   - Click **"Turn On"**
   - ✅ **Status should show: "2-Step Verification is on"**

### Step 1.2: Generate App Password

1. **Go to App Passwords Page**
   - Direct link: https://myaccount.google.com/apppasswords
   - Or: Security → 2-Step Verification → Scroll down → "App passwords"

2. **Create New App Password**
   - You may need to sign in again
   - Under "Select app": Choose **"Mail"**
   - Under "Select device": Choose **"Windows Computer"** (or "Other")
   - If "Other" - enter: **"CODEX Platform"**
   - Click **"Generate"**

3. **Copy the Password**
   - You'll see a 16-character password like: `abcd efgh ijkl mnop`
   - **IMPORTANT**: Copy this immediately! It won't be shown again
   - Example: `qwer tyui opas dfgh`

### Step 1.3: Update .env File

1. **Open Your .env File**
   ```
   Location: e:\codex_1\codex\.env
   ```

2. **Find the Email Configuration Section**
   ```env
   # Email Configuration (for verification and password reset)
   MAIL_ENABLED=false
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USE_SSL=false
   MAIL_USERNAME=your_email@gmail.com
   MAIL_PASSWORD=your_app_password
   MAIL_DEFAULT_SENDER=CODEX Platform <noreply@codex.com>
   ```

3. **Update These Lines**
   ```env
   # Email Configuration (for verification and password reset)
   MAIL_ENABLED=true                                    # ← Change to true
   MAIL_SERVER=smtp.gmail.com                          # ← Keep as is
   MAIL_PORT=587                                        # ← Keep as is
   MAIL_USE_TLS=true                                    # ← Keep as is
   MAIL_USE_SSL=false                                   # ← Keep as is
   MAIL_USERNAME=yourname@gmail.com                     # ← Your Gmail address
   MAIL_PASSWORD=qwer tyui opas dfgh                    # ← App password from Step 1.2
   MAIL_DEFAULT_SENDER=CODEX Platform <yourname@gmail.com>  # ← Your Gmail
   ```

4. **Save the File** (Ctrl+S)

### Step 1.4: Verify Email Setup

1. **Restart Flask Server**
   - In terminal, press `Ctrl+C` to stop
   - Run: `python app.py`

2. **Check Console Output**
   ```
   ✅ Email system enabled            ← Should see this now!
   ```
   
   Instead of:
   ```
   ⚠️ Email system disabled (set MAIL_ENABLED=true in .env to enable)
   ```

3. **Test Email (Optional)**
   - Register a new test account
   - Check if verification email arrives
   - Check spam folder if not in inbox

---

## Part 2: Enable Google OAuth

**Time Required**: ~15 minutes  
**Purpose**: Allow users to sign in with Google account

### Step 2.1: Access Google Cloud Console

1. **Open Google Cloud Console**
   - Go to: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create New Project** (or use existing)
   - Click project dropdown (top left, next to "Google Cloud")
   - Click **"NEW PROJECT"**
   - Project name: **CODEX Platform**
   - Organization: Leave as "No organization" (if personal)
   - Click **"CREATE"**
   - Wait 10-30 seconds for creation
   - Click **"SELECT PROJECT"** in notification

### Step 2.2: Enable Google+ API

1. **Go to API Library**
   - Left sidebar → "APIs & Services" → **"Library"**
   - Or direct link: https://console.cloud.google.com/apis/library

2. **Search for Google+ API**
   - In search box, type: **"Google+ API"**
   - Click on **"Google+ API"** result

3. **Enable the API**
   - Click **"ENABLE"** button
   - Wait 5-10 seconds
   - ✅ You should see "API enabled" message

### Step 2.3: Configure OAuth Consent Screen

1. **Go to OAuth Consent Screen**
   - Left sidebar → "APIs & Services" → **"OAuth consent screen"**
   - Or: https://console.cloud.google.com/apis/credentials/consent

2. **Select User Type**
   - Choose: **"External"** (for testing with any Google account)
   - Click **"CREATE"**

3. **Fill App Information** (Page 1 of 4)
   - App name: **CODEX Platform**
   - User support email: **your_email@gmail.com** (dropdown)
   - App logo: *(optional - skip for now)*
   - Application home page: `http://localhost:5000` *(optional)*
   - Developer contact information: **your_email@gmail.com**
   - Click **"SAVE AND CONTINUE"**

4. **Scopes** (Page 2 of 4)
   - Click **"ADD OR REMOVE SCOPES"**
   - Search for: **"email"**, **"profile"**, **"openid"**
   - Check boxes for:
     - ✅ `.../auth/userinfo.email`
     - ✅ `.../auth/userinfo.profile`
     - ✅ `openid`
   - Click **"UPDATE"**
   - Click **"SAVE AND CONTINUE"**

5. **Test Users** (Page 3 of 4)
   - Click **"+ ADD USERS"**
   - Enter your Gmail: **your_email@gmail.com**
   - Click **"ADD"**
   - Click **"SAVE AND CONTINUE"**

6. **Summary** (Page 4 of 4)
   - Review all settings
   - Click **"BACK TO DASHBOARD"**

### Step 2.4: Create OAuth Credentials

1. **Go to Credentials Page**
   - Left sidebar → "APIs & Services" → **"Credentials"**
   - Or: https://console.cloud.google.com/apis/credentials

2. **Create OAuth Client ID**
   - Click **"+ CREATE CREDENTIALS"** (top)
   - Select **"OAuth client ID"**

3. **Configure OAuth Client**
   - Application type: **Web application**
   - Name: **CODEX OAuth Client**

4. **Add Authorized JavaScript Origins**
   - Click **"+ ADD URI"** under "Authorized JavaScript origins"
   - Add these URLs (one at a time):
     ```
     http://localhost:5000
     ```
   - Click **"+ ADD URI"** again
     ```
     http://127.0.0.1:5000
     ```

5. **Add Authorized Redirect URIs**
   - Click **"+ ADD URI"** under "Authorized redirect URIs"
   - Add these URLs (one at a time):
     ```
     http://localhost:5000/login/google/callback
     ```
   - Click **"+ ADD URI"** again
     ```
     http://127.0.0.1:5000/login/google/callback
     ```

6. **Create Credentials**
   - Click **"CREATE"**
   - A popup appears with your credentials!

### Step 2.5: Copy OAuth Credentials

1. **Copy Client ID**
   - In the popup, you'll see:
     ```
     Your Client ID
     123456789012-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com
     ```
   - Click the **copy icon** or select and copy
   - Paste somewhere temporary (Notepad)

2. **Copy Client Secret**
   - In the same popup:
     ```
     Your Client Secret
     GOCSPX-AbCdEfGhIjKlMnOpQrStUvWxYz
     ```
   - Click the **copy icon** or select and copy
   - Paste in Notepad below Client ID

3. **Keep Popup Open or Download JSON**
   - Click **"DOWNLOAD JSON"** (optional backup)
   - Click **"OK"** to close popup
   - ⚠️ You can always view these in Credentials page later

### Step 2.6: Update .env File with Google Credentials

1. **Open .env File**
   ```
   Location: e:\codex_1\codex\.env
   ```

2. **Find OAuth Configuration - Google Section**
   ```env
   # OAuth Configuration - Google
   GOOGLE_CLIENT_ID=
   GOOGLE_CLIENT_SECRET=
   ```

3. **Paste Your Credentials**
   ```env
   # OAuth Configuration - Google
   GOOGLE_CLIENT_ID=123456789012-abcdefghijklmnopqrstuvwxyz123456.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-AbCdEfGhIjKlMnOpQrStUvWxYz
   ```

4. **Save File** (Ctrl+S)

---

## Part 3: Enable GitHub OAuth

**Time Required**: ~10 minutes  
**Purpose**: Allow users to sign in with GitHub account

### Step 3.1: Access GitHub OAuth Apps Settings

1. **Open GitHub Settings**
   - Go to: https://github.com/settings/developers
   - Or: GitHub → Profile Picture → Settings → Developer settings (left sidebar)

2. **Navigate to OAuth Apps**
   - Left sidebar → Click **"OAuth Apps"**
   - Direct link: https://github.com/settings/developers

### Step 3.2: Create New OAuth App

1. **Click "New OAuth App"**
   - Green button in top right
   - Or: If no apps, click **"Register a new application"**

2. **Fill Application Details**
   - **Application name**: `CODEX Platform`
   - **Homepage URL**: `http://localhost:5000`
   - **Application description** (optional): 
     ```
     Online IDE with multi-language compiler, AI features, and practice problems
     ```
   - **Authorization callback URL**: 
     ```
     http://localhost:5000/login/github/callback
     ```
     ⚠️ **IMPORTANT**: Must be exact! No trailing slash!

3. **Uncheck "Enable Device Flow"** (optional, leave unchecked)

4. **Register Application**
   - Click **"Register application"** button (green)
   - You'll be redirected to your app's settings page

### Step 3.3: Get OAuth Credentials

1. **Copy Client ID**
   - On your app's settings page, you'll see:
     ```
     Client ID
     Iv1.abc123def456ghi789
     ```
   - Click the **copy icon** next to it
   - Or select and copy (Ctrl+C)
   - Paste in Notepad

2. **Generate Client Secret**
   - Find section: "Client secrets"
   - Click **"Generate a new client secret"** button
   - You may need to confirm with password or 2FA

3. **Copy Client Secret IMMEDIATELY**
   - A secret appears (40 characters):
     ```
     a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
     ```
   - **⚠️ CRITICAL**: This is shown ONLY ONCE!
   - Click **copy icon** or select all and copy
   - Paste in Notepad below Client ID
   - If you miss it, you'll need to generate a new one

### Step 3.4: Update .env File with GitHub Credentials

1. **Open .env File**
   ```
   Location: e:\codex_1\codex\.env
   ```

2. **Find OAuth Configuration - GitHub Section**
   ```env
   # OAuth Configuration - GitHub
   GITHUB_CLIENT_ID=
   GITHUB_CLIENT_SECRET=
   ```

3. **Paste Your Credentials**
   ```env
   # OAuth Configuration - GitHub
   GITHUB_CLIENT_ID=Iv1.abc123def456ghi789
   GITHUB_CLIENT_SECRET=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0
   ```

4. **Save File** (Ctrl+S)

---

## Part 4: Update Login Page

**Time Required**: ~10 minutes  
**Purpose**: Add OAuth login buttons to the UI

### Step 4.1: Backup Current Login Page

1. **Open Terminal/PowerShell**
   ```powershell
   cd e:\codex_1\codex\templates
   ```

2. **Create Backup**
   ```powershell
   Copy-Item login.html login.html.backup
   ```

### Step 4.2: Add OAuth Buttons to Login Form

1. **Open login.html**
   ```
   Location: e:\codex_1\codex\templates\login.html
   ```

2. **Find the Login Form Section**
   - Search for: `<button class="btn" type="submit">Login Now</button>`
   - Around line 37

3. **After the login button's `</div>`, add OAuth buttons**
   
   Add this code:
   ```html
        <div class="input-box animation" style="--D:3; --S:24">
          <button class="btn" type="submit">Login Now</button>
        </div>

        <!-- ADD THIS SECTION -->
        <div class="oauth-divider animation" style="--D:4; --S:25">
          <span>or continue with</span>
        </div>

        <div class="oauth-buttons animation" style="--D:5; --S:26">
          <a href="{{ url_for('google_login') }}" class="oauth-btn google">
            <box-icon type='logo' name='google'></box-icon>
            <span>Google</span>
          </a>
          <a href="{{ url_for('github_login') }}" class="oauth-btn github">
            <box-icon type='logo' name='github'></box-icon>
            <span>GitHub</span>
          </a>
        </div>
        <!-- END OF ADDED SECTION -->

        <div class="regi-link animation" style="--D:6; --S:27">
          <p>Don't have an account? <br> <a href="#" class="SignUpLink">Create Account</a></p>
        </div>
   ```

4. **Save File** (Ctrl+S)

### Step 4.3: Add OAuth Button Styles

1. **Open login.css**
   ```
   Location: e:\codex_1\codex\static\style\login.css
   ```

2. **Scroll to the Bottom of the File**

3. **Add OAuth Styles**
   
   Paste this at the end:
   ```css

   /* OAuth Divider */
   .oauth-divider {
       display: flex;
       align-items: center;
       text-align: center;
       margin: 20px 0 15px;
       color: #999;
       font-size: 14px;
   }

   .oauth-divider::before,
   .oauth-divider::after {
       content: '';
       flex: 1;
       border-bottom: 1px solid #444;
   }

   .oauth-divider span {
       padding: 0 15px;
   }

   /* OAuth Buttons Container */
   .oauth-buttons {
       display: flex;
       gap: 10px;
       margin-bottom: 15px;
   }

   /* OAuth Button Base Styles */
   .oauth-btn {
       flex: 1;
       display: flex;
       align-items: center;
       justify-content: center;
       gap: 8px;
       padding: 12px 20px;
       background: transparent;
       border: 2px solid #468be6;
       border-radius: 8px;
       text-decoration: none;
       font-size: 16px;
       font-weight: 600;
       transition: all 0.3s ease;
       color: #fff;
   }

   .oauth-btn:hover {
       transform: translateY(-2px);
       box-shadow: 0 5px 15px rgba(70, 139, 230, 0.3);
   }

   .oauth-btn box-icon {
       font-size: 20px;
   }

   /* Google Button */
   .oauth-btn.google {
       border-color: #4285f4;
   }

   .oauth-btn.google:hover {
       background: #4285f4;
       border-color: #4285f4;
       box-shadow: 0 5px 15px rgba(66, 133, 244, 0.4);
   }

   /* GitHub Button */
   .oauth-btn.github {
       border-color: #333;
   }

   .oauth-btn.github:hover {
       background: #333;
       border-color: #333;
       box-shadow: 0 5px 15px rgba(51, 51, 51, 0.4);
   }
   ```

4. **Save File** (Ctrl+S)

---

## Part 5: Testing & Verification

### Step 5.1: Restart Flask Server

1. **Stop Current Server**
   - In terminal/PowerShell, press `Ctrl+C`

2. **Start Server Again**
   ```powershell
   python app.py
   ```

3. **Check Console Output**
   
   You should now see:
   ```
   ✅ Gemini AI enabled: gemini-2.0-flash-exp
   ✅ Email system enabled                           ← NEW!
   ✅ Google OAuth enabled                           ← NEW!
   ✅ GitHub OAuth enabled                           ← NEW!
   ✅ MySQL database 'CODEX' initialized successfully!
   ```

   Instead of the previous warnings:
   ```
   ⚠️ Email system disabled
   ⚠️ Google OAuth disabled
   ⚠️ GitHub OAuth disabled
   ```

### Step 5.2: Visual Check

1. **Open Browser**
   - Go to: http://127.0.0.1:5000

2. **Check Login Page**
   - ✅ Should see "or continue with" divider
   - ✅ Should see Google button (with blue icon)
   - ✅ Should see GitHub button (with black icon)
   - ✅ Buttons should have hover effect

### Step 5.3: Test Email System

1. **Register a Test Account**
   - Click "Create Account" link
   - Fill in:
     - Username: `test_user_001`
     - Email: your real email
     - Password: `test123456`
     - Confirm: `test123456`
   - Click "Create Account"

2. **Check Email Inbox**
   - Check your Gmail inbox
   - Look for email from "CODEX Platform"
   - Subject: "Welcome to CODEX Platform!" or similar
   - ⚠️ If not in inbox, check **Spam folder**

3. **If Email Received**
   - ✅ Email system is working!
   - Click verification link in email (if required)

### Step 5.4: Test Google OAuth

1. **Go to Login Page**
   - http://127.0.0.1:5000

2. **Click "Google" OAuth Button**
   - You'll be redirected to Google sign-in page

3. **Sign In with Google**
   - Choose your Google account
   - Click "Continue" or "Allow" on permission screen

4. **Check Redirect**
   - You should be redirected back to: http://127.0.0.1:5000/main
   - ✅ You should be logged in!
   - Top right should show your Google profile picture

5. **Verify Database**
   ```powershell
   mysql -u root -p150106 -e "USE CODEX; SELECT username, email, oauth_provider FROM users;"
   ```
   - Should see your Google account with `oauth_provider='google'`

### Step 5.5: Test GitHub OAuth

1. **Logout First**
   - Click profile picture → Logout
   - Or go to: http://127.0.0.1:5000/logout

2. **Go to Login Page**
   - http://127.0.0.1:5000

3. **Click "GitHub" OAuth Button**
   - You'll be redirected to GitHub authorization page

4. **Authorize Application**
   - Review permissions (read email, profile)
   - Click **"Authorize ESAKKIKANNANP"** (green button)

5. **Check Redirect**
   - You should be redirected back to: http://127.0.0.1:5000/main
   - ✅ You should be logged in!
   - Profile should show GitHub username and avatar

6. **Verify Database**
   ```powershell
   mysql -u root -p150106 -e "USE CODEX; SELECT username, email, oauth_provider FROM users;"
   ```
   - Should see your GitHub account with `oauth_provider='github'`

---

## Troubleshooting

### Problem 1: "Email system disabled" after restart

**Symptoms**:
```
⚠️ Email system disabled (set MAIL_ENABLED=true in .env to enable)
```

**Solutions**:

1. **Check .env file**
   ```env
   MAIL_ENABLED=true    ← Must be lowercase 'true', not 'True' or '1'
   ```

2. **Check for quotes**
   ```env
   ❌ MAIL_ENABLED='true'    # Wrong - no quotes
   ❌ MAIL_ENABLED="true"    # Wrong - no quotes
   ✅ MAIL_ENABLED=true      # Correct
   ```

3. **Check Gmail credentials**
   ```env
   MAIL_USERNAME=yourname@gmail.com          # No spaces
   MAIL_PASSWORD=abcd efgh ijkl mnop         # App password, with spaces is OK
   ```

4. **Verify 2-Step Verification is ON**
   - Go to: https://myaccount.google.com/security
   - Check "2-Step Verification" status

### Problem 2: "Google OAuth disabled" after restart

**Symptoms**:
```
⚠️ Google OAuth disabled (add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET to .env)
```

**Solutions**:

1. **Check credentials format**
   ```env
   # Must look like this (no quotes needed):
   GOOGLE_CLIENT_ID=123456789012-abcdefg.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-AbCdEfGhIjKl
   ```

2. **Check for extra spaces**
   ```env
   ❌ GOOGLE_CLIENT_ID = 123456...    # Wrong - space before =
   ❌ GOOGLE_CLIENT_ID= 123456...     # Wrong - space after =
   ✅ GOOGLE_CLIENT_ID=123456...      # Correct - no spaces
   ```

3. **Verify credentials in Google Cloud Console**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Check if credentials exist
   - Copy again if needed

### Problem 3: "GitHub OAuth disabled" after restart

**Symptoms**:
```
⚠️ GitHub OAuth disabled (add GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET to .env)
```

**Solutions**:

1. **Check credentials format**
   ```env
   GITHUB_CLIENT_ID=Iv1.abc123def456        # Starts with Iv1.
   GITHUB_CLIENT_SECRET=a1b2c3d4e5f6...     # 40 characters
   ```

2. **Regenerate secret if lost**
   - Go to: https://github.com/settings/developers
   - Click your app
   - Click "Generate a new client secret"
   - Copy immediately!

### Problem 4: Email not sending

**Symptoms**:
- Registration successful but no email received
- Console shows SMTP error

**Solutions**:

1. **Check Spam/Junk folder** first!

2. **Verify App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Delete old password
   - Generate new one
   - Update .env

3. **Try alternative SMTP settings**
   ```env
   # Option 1: TLS (port 587) - default
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USE_SSL=false

   # Option 2: SSL (port 465) - alternative
   MAIL_PORT=465
   MAIL_USE_TLS=false
   MAIL_USE_SSL=true
   ```

4. **Check Gmail security**
   - Go to: https://myaccount.google.com/security
   - Look for "Less secure app access" or security alerts
   - Allow CODEX Platform if blocked

### Problem 5: OAuth Error - "redirect_uri_mismatch"

**Symptoms**:
- Error page after clicking OAuth button
- Message: "Error 400: redirect_uri_mismatch"

**Solutions for Google**:

1. **Check exact URL match**
   - Must be EXACT: `http://127.0.0.1:5000/login/google/callback`
   - Not: `http://localhost:5000/...`
   - Not: `https://...`
   - No trailing slash!

2. **Update Google Cloud Console**
   - Go to: https://console.cloud.google.com/apis/credentials
   - Click your OAuth Client ID
   - Under "Authorized redirect URIs", add BOTH:
     ```
     http://localhost:5000/login/google/callback
     http://127.0.0.1:5000/login/google/callback
     ```
   - Click "SAVE"
   - Wait 5 minutes for changes to propagate

**Solutions for GitHub**:

1. **Check callback URL**
   - Go to: https://github.com/settings/developers
   - Click your app
   - "Authorization callback URL" must be:
     ```
     http://localhost:5000/login/github/callback
     ```
   - Update if wrong
   - Click "Update application"

### Problem 6: OAuth buttons not showing

**Symptoms**:
- Login page loads but no Google/GitHub buttons
- Only username/password form visible

**Solutions**:

1. **Hard refresh browser**
   - Press `Ctrl+Shift+R` (Windows)
   - Or `Cmd+Shift+R` (Mac)
   - Clears cached CSS/JS

2. **Check browser console for errors**
   - Press `F12`
   - Go to "Console" tab
   - Look for red errors
   - Most common: "Failed to load resource: 404"

3. **Verify login.html was saved**
   - Open: `e:\codex_1\codex\templates\login.html`
   - Search for: `oauth-buttons`
   - Should exist around line 40-50

4. **Verify login.css was saved**
   - Open: `e:\codex_1\codex\static\style\login.css`
   - Scroll to bottom
   - Should see `.oauth-btn` styles

### Problem 7: "Cannot import name 'init_mail'" error

**Symptoms**:
```
ImportError: cannot import name 'init_mail' from 'email_utils'
```

**Solutions**:

1. **Verify email_utils.py exists**
   ```powershell
   Test-Path e:\codex_1\codex\email_utils.py
   ```
   - Should return: True

2. **Check file permissions**
   - Right-click email_utils.py → Properties
   - Uncheck "Read-only" if checked

3. **Restart VS Code/Editor**
   - Sometimes editors cache imports
   - Close and reopen

### Problem 8: OAuth login works but profile picture not showing

**Symptoms**:
- Google/GitHub login successful
- Logged into dashboard
- No profile picture in top right

**Solutions**:

1. **Check profile picture URL in database**
   ```powershell
   mysql -u root -p150106 -e "USE CODEX; SELECT username, profile_picture FROM users WHERE oauth_provider IS NOT NULL;"
   ```

2. **Verify img tag in main.html**
   - Open: `templates/main.html`
   - Find: `<img src="{{ session.get('profile_picture', ...) }}" ...>`
   - Should exist in navbar

3. **Check if URL is accessible**
   - Copy profile_picture URL from database
   - Paste in browser
   - Should load image

---

## 📊 Configuration Summary Table

| Feature | Status Indicator | Required .env Variables |
|---------|------------------|------------------------|
| **Email System** | ✅ Email system enabled | `MAIL_ENABLED=true`<br>`MAIL_USERNAME=...`<br>`MAIL_PASSWORD=...` |
| **Google OAuth** | ✅ Google OAuth enabled | `GOOGLE_CLIENT_ID=...`<br>`GOOGLE_CLIENT_SECRET=...` |
| **GitHub OAuth** | ✅ GitHub OAuth enabled | `GITHUB_CLIENT_ID=...`<br>`GITHUB_CLIENT_SECRET=...` |

---

## 🎯 Final Checklist

Before considering setup complete, verify:

### Email System
- [ ] `.env` has `MAIL_ENABLED=true`
- [ ] Gmail App Password generated and added
- [ ] Flask console shows: ✅ Email system enabled
- [ ] Test registration sends email (check spam too)
- [ ] Email has correct sender name and formatting

### Google OAuth
- [ ] Google Cloud project created
- [ ] OAuth consent screen configured
- [ ] Credentials created with correct redirect URIs
- [ ] `.env` has both Client ID and Secret
- [ ] Flask console shows: ✅ Google OAuth enabled
- [ ] Login page shows Google button
- [ ] Clicking button redirects to Google
- [ ] After authorization, redirects back and logs in
- [ ] Profile picture appears in navbar
- [ ] Database shows `oauth_provider='google'`

### GitHub OAuth
- [ ] GitHub OAuth App created
- [ ] Callback URL set correctly
- [ ] `.env` has both Client ID and Secret
- [ ] Flask console shows: ✅ GitHub OAuth enabled
- [ ] Login page shows GitHub button
- [ ] Clicking button redirects to GitHub
- [ ] After authorization, redirects back and logs in
- [ ] Profile shows GitHub username/avatar
- [ ] Database shows `oauth_provider='github'`

### Visual/UI
- [ ] OAuth buttons visible on login page
- [ ] "or continue with" divider shows
- [ ] Buttons have hover effect
- [ ] Icons (Google/GitHub logos) display correctly
- [ ] Mobile responsive (test by resizing browser)

---

## 📞 Getting Help

If you're still stuck after trying troubleshooting:

1. **Check Flask console** for detailed error messages
2. **Check browser console** (F12) for JavaScript errors
3. **Check .env file** line by line against examples above
4. **Regenerate credentials** (sometimes they expire or get corrupted)
5. **Start fresh** with a new OAuth app if needed

---

## 🎉 Success!

If all checkboxes are checked, congratulations! You've successfully enabled:
- ✅ Email verification system
- ✅ Google OAuth login
- ✅ GitHub OAuth login

Your CODEX platform now has enterprise-grade authentication! 🚀

---

**Document Version**: 1.0  
**Last Updated**: October 25, 2025  
**Author**: GitHub Copilot  
**License**: MIT
