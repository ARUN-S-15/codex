# 🔄 MySQL Migration Guide

## Overview
CODEX now supports MySQL database! Your data will be stored in MySQL and viewable in MySQL Workbench.

## ✅ What Was Done

### 1. Installed Dependencies
- `mysql-connector-python` - MySQL driver for Python

### 2. Created New Files
- **`database.py`** - Database abstraction layer (handles MySQL and SQLite)
- **`setup_mysql.py`** - Interactive setup wizard for MySQL
- **`migrate_sqlite_to_mysql.py`** - Migrate existing data from SQLite to MySQL

### 3. Updated Files
- **`app.py`** - Now uses database.py functions instead of direct SQLite calls
- **`.env`** - Added MySQL configuration variables
- **`.env.example`** - Updated with MySQL template
- **`requirements.txt`** - Added mysql-connector-python
- **`view_users.py`** - Now works with both MySQL and SQLite

## 🚀 Setup Instructions (Step by Step)

### Step 1: Make Sure MySQL is Running

#### Windows:
1. Press `Win + R`
2. Type `services.msc` and press Enter
3. Look for **MySQL** or **MySQL80** service
4. Right-click → **Start** (if not running)

Or using Command Prompt (as Administrator):
```powershell
net start MySQL
# or
net start MySQL80
```

### Step 2: Find Your MySQL Root Password

If you forgot your MySQL root password, you'll need to reset it. 

**Common default passwords:**
- Empty (just press Enter)
- `root`
- `admin`
- Password you set during MySQL installation

### Step 3: Run the Setup Wizard

```powershell
python setup_mysql.py
```

**The wizard will ask for:**
- MySQL Host (default: localhost) - just press Enter
- MySQL Port (default: 3306) - just press Enter
- MySQL Username (default: root) - just press Enter
- MySQL Password - **Type your MySQL root password**
- Database Name (default: codex_db) - just press Enter

**Example output:**
```
============================================================
🔧 CODEX MySQL Setup Wizard
============================================================

Please enter your MySQL credentials:
(Press Enter to use default values shown in brackets)

MySQL Host [localhost]: 
MySQL Port [3306]: 
MySQL Username [root]: 
MySQL Password: ********
Database Name [codex_db]: 

Testing MySQL connection...
✅ Connection successful!

Updating .env file...
✅ .env file updated!

Creating database and tables...
✅ Database 'codex_db' created!
✅ Table 'users' created!

============================================================
🎉 MySQL Setup Complete!
============================================================
```

### Step 4: Migrate Existing Data (Optional)

If you have users in your old SQLite database:

```powershell
python migrate_sqlite_to_mysql.py
```

This will copy all users from `codex.db` (SQLite) to your new MySQL database.

### Step 5: Start Your Flask App

```powershell
python app.py
```

Your app now uses MySQL! 🎉

## 🔍 Viewing Data in MySQL Workbench

### 1. Open MySQL Workbench

### 2. Create a New Connection
- Click **"+"** next to "MySQL Connections"
- **Connection Name:** CODEX Database
- **Hostname:** localhost
- **Port:** 3306
- **Username:** root
- **Password:** Click "Store in Vault" and enter your password

### 3. Connect and Browse
- Click on your new connection
- In the left sidebar, expand **Schemas**
- Find **codex_db**
- Expand **Tables** → **users**
- Right-click **users** → **Select Rows - Limit 1000**

You'll see all your registered users! 📊

### 4. Run Custom Queries
In the query tab, you can run:

```sql
-- View all users
SELECT * FROM users;

-- Count total users
SELECT COUNT(*) as total_users FROM users;

-- Find users by email domain
SELECT * FROM users WHERE email LIKE '%@gmail.com';

-- Recent registrations
SELECT * FROM users ORDER BY created_at DESC LIMIT 10;
```

## 📁 Database Schema

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,  -- Hashed with Werkzeug
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🛠️ Utilities

### View Users (Terminal)
```powershell
python view_users.py
```

Shows all registered users in a nice format.

### Check Current Database
Check your `.env` file:
```env
DB_TYPE=mysql
```

## 🔧 Configuration (.env)

Your `.env` file should now look like:

```env
SECRET_KEY=a7f9d8e6c4b2a1f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1

# MySQL Database Configuration
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_actual_password
MYSQL_DATABASE=codex_db

FLASK_ENV=development
FLASK_DEBUG=True
```

## 🔄 Switching Back to SQLite

If you want to switch back to SQLite:

1. Edit `.env`:
   ```env
   DB_TYPE=sqlite
   ```

2. Restart Flask:
   ```powershell
   python app.py
   ```

The `database.py` module automatically handles both!

## 🐛 Troubleshooting

### Error: "Can't connect to MySQL server"
**Solution:**
1. Make sure MySQL service is running (see Step 1)
2. Check if port 3306 is not blocked by firewall
3. Try `mysql -u root -p` in Command Prompt to test connection

### Error: "Access denied for user 'root'@'localhost'"
**Solution:**
- Wrong password! 
- Try resetting MySQL root password
- Or use MySQL Workbench to change password

### Error: "Database error: 1045"
**Solution:**
- Authentication failed
- Run `setup_mysql.py` again with correct password

### Error: "Module 'mysql.connector' not found"
**Solution:**
```powershell
pip install mysql-connector-python
```

### Can't find MySQL service
**Solution:**
- MySQL might not be installed
- Or service name might be different: `MySQL80`, `MySQL57`, etc.
- Check in Services: `Win+R` → `services.msc`

## 📊 Advantages of MySQL

### Before (SQLite):
- ❌ Single file, harder to manage
- ❌ No GUI tools
- ❌ Limited concurrent access
- ❌ No user management

### After (MySQL):
- ✅ Professional database management
- ✅ MySQL Workbench for visual editing
- ✅ Better performance with many users
- ✅ Proper user roles and permissions
- ✅ Industry-standard for production apps
- ✅ Easy backup and restore

## 🎯 Next Steps

1. ✅ MySQL setup complete
2. ✅ Data viewable in Workbench
3. **Recommended:** Set up automatic backups
4. **Recommended:** Create a separate MySQL user (not root) for the app
5. **Optional:** Set up remote access if deploying to server

## 📚 Useful MySQL Commands

```sql
-- Show all databases
SHOW DATABASES;

-- Use codex_db
USE codex_db;

-- Show all tables
SHOW TABLES;

-- Describe users table structure
DESCRIBE users;

-- Backup (in Command Prompt)
mysqldump -u root -p codex_db > backup.sql

-- Restore (in Command Prompt)
mysql -u root -p codex_db < backup.sql
```

## 🔒 Security Notes

1. **Never commit `.env` file** - It contains your MySQL password!
2. **Use strong MySQL passwords** in production
3. **Create separate MySQL user** for the app (not root)
4. **Limit MySQL user permissions** to only codex_db database

Example creating app user:
```sql
CREATE USER 'codex_app'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON codex_db.* TO 'codex_app'@'localhost';
FLUSH PRIVILEGES;
```

Then update `.env`:
```env
MYSQL_USER=codex_app
MYSQL_PASSWORD=strong_password
```

---

**Need Help?** Run `python setup_mysql.py` again to reconfigure!

**Everything Working?** You should see your data in MySQL Workbench now! 🎉
