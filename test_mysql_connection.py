# test_mysql_connection.py - Test your MySQL connection
import mysql.connector
import getpass

print("=" * 60)
print("🔍 MySQL Connection Tester")
print("=" * 60)
print()

# Get credentials
host = input("MySQL Host [localhost]: ").strip() or "localhost"
port = input("MySQL Port [3306]: ").strip() or "3306"
user = input("MySQL Username [root]: ").strip() or "root"
password = getpass.getpass("MySQL Password (or press Enter for no password): ")

print()
print("Testing connection...")
print()

try:
    # Try to connect
    conn = mysql.connector.connect(
        host=host,
        port=int(port),
        user=user,
        password=password
    )
    
    cursor = conn.cursor()
    
    # Get MySQL version
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    
    # Get list of databases
    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    
    print("✅ CONNECTION SUCCESSFUL!")
    print()
    print(f"MySQL Version: {version[0]}")
    print()
    print("Available Databases:")
    for db in databases:
        print(f"  📁 {db[0]}")
    
    # Check if codex_db exists
    db_names = [db[0] for db in databases]
    if 'codex_db' in db_names:
        print()
        print("✅ 'codex_db' database found!")
        
        # Check for users table
        cursor.execute("USE codex_db")
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        if tables:
            print("   Tables:")
            for table in tables:
                print(f"     📊 {table[0]}")
        else:
            print("   ⚠️  No tables yet (need to run setup)")
    else:
        print()
        print("⚠️  'codex_db' database not found")
        print("   Run setup_mysql.py to create it")
    
    print()
    print("=" * 60)
    print("🎉 Your MySQL is working! You can update .env file now.")
    print("=" * 60)
    print()
    print("Add to your .env file:")
    print(f"MYSQL_HOST={host}")
    print(f"MYSQL_PORT={port}")
    print(f"MYSQL_USER={user}")
    print(f"MYSQL_PASSWORD={password}")
    print()
    
    cursor.close()
    conn.close()
    
except mysql.connector.Error as e:
    print("❌ CONNECTION FAILED!")
    print()
    print(f"Error Code: {e.errno}")
    print(f"Error Message: {e.msg}")
    print()
    
    if e.errno == 1045:
        print("💡 This is an authentication error.")
        print("   Possible solutions:")
        print("   1. Wrong password - try again")
        print("   2. Use empty password (just press Enter)")
        print("   3. Reset MySQL root password (see QUICK_MYSQL_SETUP.md)")
    elif e.errno == 2003:
        print("💡 Cannot connect to MySQL server.")
        print("   Possible solutions:")
        print("   1. Make sure MySQL service is running")
        print("   2. Check the hostname and port")
        print("   3. Start MySQL: net start MySQL80")
    else:
        print("💡 Check QUICK_MYSQL_SETUP.md for help")
    print()

print()
input("Press Enter to exit...")
