# database.py - Database abstraction layer for MySQL, PostgreSQL and SQLite
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_TYPE = os.getenv('DB_TYPE', 'mysql')
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'codex_db')
}

# PostgreSQL configuration (for Render deployment)
DATABASE_URL = os.getenv('DATABASE_URL', '')

def get_db_connection():
    """Get database connection based on DB_TYPE"""
    try:
        if DB_TYPE == 'postgresql':
            import psycopg2
            return psycopg2.connect(DATABASE_URL)
        elif DB_TYPE == 'mysql':
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            return conn
        else:
            import sqlite3
            # Use persistent disk on Render or local file
            db_path = os.getenv('DATABASE_PATH', 'codex.db')
            if db_path != 'codex.db':
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
            return sqlite3.connect(db_path)
    except Error as e:
        print(f"Error connecting to database: {e}")
        raise

def init_mysql_database():
    """Initialize MySQL database and create tables"""
    try:
        # First connect without database to create it
        temp_config = MYSQL_CONFIG.copy()
        db_name = temp_config.pop('database')
        
        conn = mysql.connector.connect(**temp_config)
        cursor = conn.cursor()
        
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email_verified BOOLEAN DEFAULT FALSE,
                verification_token VARCHAR(100),
                reset_token VARCHAR(100),
                reset_token_expiry TIMESTAMP NULL,
                profile_picture VARCHAR(500),
                is_admin BOOLEAN DEFAULT FALSE,
                oauth_provider VARCHAR(50),
                oauth_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL,
                INDEX idx_username (username),
                INDEX idx_email (email),
                INDEX idx_verification_token (verification_token),
                INDEX idx_reset_token (reset_token)
            )
        ''')
        
        # Create code_history table for tracking all user activities
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                activity_type VARCHAR(50) NOT NULL,
                code_snippet TEXT NOT NULL,
                language VARCHAR(50),
                title VARCHAR(255),
                output TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_created (user_id, created_at),
                INDEX idx_activity (activity_type),
                INDEX idx_user_activity (user_id, activity_type)
            )
        ''')
        
        # Create shared_codes table (separate from history for better organization)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_codes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                code_snippet TEXT NOT NULL,
                language VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                share_token VARCHAR(100) UNIQUE NOT NULL,
                views INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_share_token (share_token),
                INDEX idx_user_shared (user_id, created_at)
            )
        ''')
        
        # Create projects table for saved user projects
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                code_snippet TEXT NOT NULL,
                language VARCHAR(50) NOT NULL,
                is_public BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_projects (user_id, created_at),
                INDEX idx_public (is_public)
            )
        ''')
        
        conn.commit()
        print(f"✅ MySQL database '{db_name}' initialized successfully!")
        print(f"   - users table created")
        print(f"   - code_history table created")
        print(f"   - shared_codes table created")
        print(f"   - projects table created")
        cursor.close()
        conn.close()
        return True
        
    except Error as e:
        print(f"❌ Error initializing MySQL database: {e}")
        return False

def init_postgresql_database():
    """Initialize PostgreSQL database and create tables"""
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email_verified BOOLEAN DEFAULT FALSE,
                verification_token VARCHAR(100),
                reset_token VARCHAR(100),
                reset_token_expiry TIMESTAMP NULL,
                profile_picture VARCHAR(500),
                is_admin BOOLEAN DEFAULT FALSE,
                oauth_provider VARCHAR(50),
                oauth_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON users(email)')
        
        # Create code_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                activity_type VARCHAR(50) NOT NULL,
                code_snippet TEXT NOT NULL,
                language VARCHAR(50),
                title VARCHAR(255),
                output TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_created ON code_history(user_id, created_at)')
        
        # Create shared_codes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_codes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                code_snippet TEXT NOT NULL,
                language VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                share_token VARCHAR(100) UNIQUE NOT NULL,
                views INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_token ON shared_codes(share_token)')
        
        # Create projects table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                title VARCHAR(255) NOT NULL,
                code_snippet TEXT NOT NULL,
                language VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_projects ON projects(user_id, updated_at)')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ PostgreSQL database 'CODEX' initialized successfully!")
        print("   - users table created")
        print("   - code_history table created")
        print("   - shared_codes table created")
        print("   - projects table created")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing PostgreSQL database: {e}")
        return False

def init_db():
    """Initialize database (MySQL, PostgreSQL or SQLite)"""
    if DB_TYPE == 'postgresql':
        return init_postgresql_database()
    elif DB_TYPE == 'mysql':
        return init_mysql_database()
    else:
        # SQLite initialization (fallback)
        import sqlite3
        db_path = os.getenv('DATABASE_PATH', 'codex.db')
        if db_path != 'codex.db':
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email_verified BOOLEAN DEFAULT 0,
                verification_token VARCHAR(100),
                reset_token VARCHAR(100),
                reset_token_expiry TIMESTAMP NULL,
                profile_picture VARCHAR(500),
                is_admin BOOLEAN DEFAULT 0,
                oauth_provider VARCHAR(50),
                oauth_id VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type VARCHAR(50) NOT NULL,
                code_snippet TEXT NOT NULL,
                language VARCHAR(50),
                title VARCHAR(255),
                output TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                code_snippet TEXT NOT NULL,
                language VARCHAR(50) NOT NULL,
                title VARCHAR(255) NOT NULL,
                share_token VARCHAR(100) UNIQUE NOT NULL,
                views INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(255) NOT NULL,
                code_snippet TEXT NOT NULL,
                language VARCHAR(50) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        conn.close()
        print("✅ SQLite database initialized successfully!")
        return True

def execute_query(query, params=None, fetch=False):
    """
    Execute a database query with proper parameter handling for MySQL/SQLite
    
    Args:
        query: SQL query string (use %s for MySQL, ? for SQLite)
        params: Tuple of parameters
        fetch: Whether to fetch results (True for SELECT, False for INSERT/UPDATE)
    
    Returns:
        For SELECT: List of tuples or None
        For INSERT/UPDATE: lastrowid or rowcount
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Convert query placeholders if needed
        if DB_TYPE == 'mysql' and '?' in query:
            query = query.replace('?', '%s')
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            conn.close()
            return result
        else:
            conn.commit()
            last_id = cursor.lastrowid
            cursor.close()
            conn.close()
            return last_id
            
    except Error as e:
        print(f"Database error: {e}")
        conn.rollback()
        cursor.close()
        conn.close()
        raise

def fetch_one(query, params=None):
    """Fetch a single row"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Convert query placeholders if needed
        if DB_TYPE == 'mysql' and '?' in query:
            query = query.replace('?', '%s')
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
        
    except Error as e:
        print(f"Database error: {e}")
        cursor.close()
        conn.close()
        raise

def add_to_history(user_id, activity_type, code_snippet, language, title, output=None):
    """
    Add an activity to user's history
    
    Args:
        user_id: User ID
        activity_type: 'run', 'debug', 'optimize', 'explain'
        code_snippet: The code that was executed
        language: Programming language
        title: Short description/title generated from code
        output: Result/output of the operation
    """
    query = '''
        INSERT INTO code_history (user_id, activity_type, code_snippet, language, title, output)
        VALUES (?, ?, ?, ?, ?, ?)
    '''
    return execute_query(query, (user_id, activity_type, code_snippet, language, title, output))

def get_user_history(user_id, limit=50):
    """
    Get user's activity history
    
    Args:
        user_id: User ID
        limit: Maximum number of records to return
    
    Returns:
        List of history records
    """
    query = '''
        SELECT id, activity_type, code_snippet, language, title, output, created_at
        FROM code_history
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
    '''
    return execute_query(query, (user_id, limit), fetch=True)

def get_history_by_id(history_id, user_id):
    """Get a specific history item (with user verification)"""
    query = '''
        SELECT id, activity_type, code_snippet, language, title, output, created_at
        FROM code_history
        WHERE id = ? AND user_id = ?
    '''
    return fetch_one(query, (history_id, user_id))

def delete_history_item(history_id, user_id):
    """Delete a history item (with user verification)"""
    query = 'DELETE FROM code_history WHERE id = ? AND user_id = ?'
    return execute_query(query, (history_id, user_id))

def generate_code_title(code, max_length=50):
    """
    Generate a short title/description from code
    
    Args:
        code: The code snippet
        max_length: Maximum length of title
    
    Returns:
        A short descriptive title
    """
    # Remove extra whitespace and newlines
    code = ' '.join(code.split())
    
    # If code is short, return as is
    if len(code) <= max_length:
        return code
    
    # Try to find the first meaningful line
    lines = code.split(';')
    if lines:
        first_line = lines[0].strip()
        if len(first_line) <= max_length:
            return first_line + '...'
    
    # Return truncated version
    return code[:max_length] + '...'
