# Quick MySQL Setup Instructions

## 🔍 Finding Your MySQL Password

### Option 1: Empty Password
Many MySQL installations have no password by default.
- Just press **Enter** when asked for password

### Option 2: Check MySQL Workbench
1. Open MySQL Workbench
2. Look at your existing connections
3. The password might be saved there

### Option 3: Password Set During Installation
- Check your installation notes
- Common passwords: `root`, `admin`, `mysql`

### Option 4: Reset MySQL Root Password

If you forgot your password, reset it:

#### Windows:
1. **Stop MySQL service:**
   ```powershell
   net stop MySQL80
   ```

2. **Start MySQL without password:**
   ```powershell
   mysqld --skip-grant-tables
   ```

3. **Open new terminal and connect:**
   ```powershell
   mysql -u root
   ```

4. **Reset password:**
   ```sql
   USE mysql;
   ALTER USER 'root'@'localhost' IDENTIFIED BY 'NewPassword123';
   FLUSH PRIVILEGES;
   EXIT;
   ```

5. **Stop and restart MySQL normally:**
   ```powershell
   net stop MySQL80
   net start MySQL80
   ```

## 🚀 Manual Setup (Alternative)

If the wizard doesn't work, set up manually:

### Step 1: Update .env File Manually

Open `.env` and add your MySQL password:

```env
# MySQL Database Configuration
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=YOUR_ACTUAL_PASSWORD_HERE
MYSQL_DATABASE=codex_db
```

### Step 2: Create Database in MySQL Workbench

1. Open MySQL Workbench
2. Connect to localhost
3. Click **Create Schema** (cylinder icon)
4. Name it: `codex_db`
5. Click **Apply**

### Step 3: Create Users Table

In MySQL Workbench query tab:

```sql
USE codex_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Click **Execute** ⚡

### Step 4: Start Flask App

```powershell
python app.py
```

### Step 5: Register a User

1. Go to http://localhost:5000/register
2. Create an account
3. Check MySQL Workbench!

In Workbench:
```sql
SELECT * FROM users;
```

You'll see your user! 🎉

## ✅ Verify Setup

Run this to check connection:

```powershell
python view_users.py
```

Should show:
```
📊 CODEX Database (MYSQL: codex_db) - Registered Users
```

---

**Need the wizard again?** Run `python setup_mysql.py`
