# migrate_sqlite_to_mysql.py - Migrate data from SQLite to MySQL
import sqlite3
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

def migrate_data():
    """Migrate users from SQLite to MySQL"""
    print("=" * 60)
    print("📦 Migrating data from SQLite to MySQL")
    print("=" * 60)
    print()
    
    # Check if SQLite database exists
    if not os.path.exists('codex.db'):
        print("❌ SQLite database (codex.db) not found!")
        print("No data to migrate.")
        return
    
    # Connect to SQLite
    print("Connecting to SQLite...")
    sqlite_conn = sqlite3.connect('codex.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Get all users from SQLite
    sqlite_cursor.execute('SELECT id, username, email, password, created_at FROM users')
    users = sqlite_cursor.fetchall()
    
    if not users:
        print("No users found in SQLite database.")
        sqlite_conn.close()
        return
    
    print(f"Found {len(users)} user(s) in SQLite database")
    print()
    
    # Connect to MySQL
    print("Connecting to MySQL...")
    try:
        mysql_conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'codex_db')
        )
        mysql_cursor = mysql_conn.cursor()
        print("✅ Connected to MySQL")
        print()
        
        # Migrate each user
        migrated = 0
        skipped = 0
        
        for user in users:
            user_id, username, email, password, created_at = user
            
            try:
                # Check if user already exists
                mysql_cursor.execute('SELECT id FROM users WHERE username = %s OR email = %s', (username, email))
                existing = mysql_cursor.fetchone()
                
                if existing:
                    print(f"⚠️  Skipping '{username}' (already exists)")
                    skipped += 1
                    continue
                
                # Insert user
                mysql_cursor.execute(
                    'INSERT INTO users (username, email, password, created_at) VALUES (%s, %s, %s, %s)',
                    (username, email, password, created_at)
                )
                mysql_conn.commit()
                print(f"✅ Migrated user: {username}")
                migrated += 1
                
            except mysql.connector.Error as e:
                print(f"❌ Error migrating '{username}': {e}")
                skipped += 1
        
        print()
        print("=" * 60)
        print("Migration Complete!")
        print("=" * 60)
        print(f"✅ Migrated: {migrated} user(s)")
        print(f"⚠️  Skipped: {skipped} user(s)")
        print()
        
        # Close connections
        mysql_cursor.close()
        mysql_conn.close()
        sqlite_conn.close()
        
        print("You can now delete codex.db if you want (backup recommended)")
        print()
        
    except mysql.connector.Error as e:
        print(f"❌ MySQL Error: {e}")
        print()
        print("Make sure you've run setup_mysql.py first!")
        sqlite_conn.close()

if __name__ == "__main__":
    migrate_data()
