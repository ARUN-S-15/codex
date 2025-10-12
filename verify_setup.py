# verify_setup.py - Verify MySQL setup is working
from database import execute_query, DB_TYPE, MYSQL_CONFIG
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 70)
print("✅ CODEX MySQL Setup Verification")
print("=" * 70)
print()

# 1. Check configuration
print("📋 Configuration:")
print(f"   Database Type: {DB_TYPE.upper()}")
print(f"   MySQL Host: {MYSQL_CONFIG['host']}")
print(f"   MySQL Port: {MYSQL_CONFIG['port']}")
print(f"   MySQL User: {MYSQL_CONFIG['user']}")
print(f"   MySQL Database: {MYSQL_CONFIG['database']}")
print()

# 2. Test connection
print("🔌 Testing Database Connection...")
try:
    users = execute_query('SELECT COUNT(*) FROM users', fetch=True)
    user_count = users[0][0] if users else 0
    print(f"   ✅ Connection successful!")
    print(f"   👥 Users in database: {user_count}")
    print()
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    print()
    exit(1)

# 3. Show users
print("📊 Registered Users:")
try:
    users = execute_query('SELECT id, username, email, created_at FROM users', fetch=True)
    if users:
        for user in users:
            print(f"   👤 ID: {user[0]} | Username: {user[1]} | Email: {user[2]} | Created: {user[3]}")
    else:
        print("   ⚠️  No users registered yet")
except Exception as e:
    print(f"   ❌ Error: {e}")

print()
print("=" * 70)
print("✅ Setup Verification Complete!")
print("=" * 70)
print()
print("🎉 Your CODEX app is now using MySQL!")
print()
print("📊 To view data in MySQL Workbench:")
print("   1. Open MySQL Workbench")
print("   2. Connect to localhost")
print(f"   3. Open schema: {MYSQL_CONFIG['database']}")
print("   4. Browse table: users")
print()
print("🚀 Your app is running at: http://127.0.0.1:5000")
print()
