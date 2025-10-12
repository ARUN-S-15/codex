# setup_mysql.py - Interactive MySQL setup script
import os
import getpass
from dotenv import load_dotenv, set_key
import mysql.connector

def test_mysql_connection(host, port, user, password):
    """Test MySQL connection"""
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        conn.close()
        return True
    except mysql.connector.Error as e:
        print(f"❌ Connection failed: {e}")
        return False

def setup_mysql():
    """Interactive MySQL setup"""
    print("=" * 60)
    print("🔧 CODEX MySQL Setup Wizard")
    print("=" * 60)
    print()
    
    # Get MySQL credentials
    print("Please enter your MySQL credentials:")
    print("(Press Enter to use default values shown in brackets)")
    print()
    
    host = input("MySQL Host [localhost]: ").strip() or "localhost"
    port = input("MySQL Port [3306]: ").strip() or "3306"
    user = input("MySQL Username [root]: ").strip() or "root"
    password = getpass.getpass("MySQL Password: ")
    db_name = input("Database Name [codex_db]: ").strip() or "codex_db"
    
    print()
    print("Testing MySQL connection...")
    
    if not test_mysql_connection(host, int(port), user, password):
        print()
        print("❌ Failed to connect to MySQL!")
        print("Please check your credentials and make sure MySQL is running.")
        print()
        print("To start MySQL (Windows):")
        print("  - Open Services (Win+R → services.msc)")
        print("  - Find 'MySQL' or 'MySQL80' service")
        print("  - Right-click → Start")
        return False
    
    print("✅ Connection successful!")
    print()
    
    # Update .env file
    print("Updating .env file...")
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    
    set_key(env_path, 'DB_TYPE', 'mysql')
    set_key(env_path, 'MYSQL_HOST', host)
    set_key(env_path, 'MYSQL_PORT', port)
    set_key(env_path, 'MYSQL_USER', user)
    set_key(env_path, 'MYSQL_PASSWORD', password)
    set_key(env_path, 'MYSQL_DATABASE', db_name)
    
    print("✅ .env file updated!")
    print()
    
    # Initialize database
    print("Creating database and tables...")
    try:
        conn = mysql.connector.connect(
            host=host,
            port=int(port),
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"✅ Database '{db_name}' created!")
        
        # Use the database
        cursor.execute(f"USE {db_name}")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Table 'users' created!")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        print("🎉 MySQL Setup Complete!")
        print("=" * 60)
        print()
        print("You can now:")
        print("1. Run your Flask app: python app.py")
        print("2. View data in MySQL Workbench:")
        print(f"   - Host: {host}")
        print(f"   - Port: {port}")
        print(f"   - Username: {user}")
        print(f"   - Database: {db_name}")
        print()
        print("To migrate existing SQLite data, run: python migrate_sqlite_to_mysql.py")
        print()
        
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ Error setting up database: {e}")
        return False

if __name__ == "__main__":
    setup_mysql()
