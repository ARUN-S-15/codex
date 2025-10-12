from database import get_db_connection, execute_query
import os
from dotenv import load_dotenv

load_dotenv()

# Get all users (excluding passwords for security)
users = execute_query('SELECT id, username, email, created_at FROM users', fetch=True)

db_type = os.getenv('DB_TYPE', 'mysql').upper()
db_name = os.getenv('MYSQL_DATABASE', 'codex_db') if db_type == 'MYSQL' else 'codex.db'

print("=" * 80)
print(f"📊 CODEX Database ({db_type}: {db_name}) - Registered Users")
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
print(f"📈 Total Users: {len(users) if users else 0}")
print("=" * 80)
