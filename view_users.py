import sqlite3

# Connect to database
conn = sqlite3.connect('codex.db')
cursor = conn.cursor()

# Get all users (excluding passwords for security)
cursor.execute('SELECT id, username, email, created_at FROM users')
users = cursor.fetchall()

print("=" * 80)
print("📊 CODEX Database - Registered Users")
print("=" * 80)

if users:
    for user in users:
        print(f"\n👤 User ID: {user[0]}")
        print(f"   Username: {user[1]}")
        print(f"   Email: {user[2]}")
        print(f"   Created: {user[3]}")
else:
    print("\n⚠️  No users registered yet!")
    print("\n💡 Go to http://127.0.0.1:5000/register to create your first account!")

print("\n" + "=" * 80)
print(f"📈 Total Users: {len(users)}")
print("=" * 80)

conn.close()
