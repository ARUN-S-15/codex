# database.py - Database abstraction layer for MySQL and SQLite
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

def get_db_connection():
    """Get database connection based on DB_TYPE"""
    try:
        if DB_TYPE == 'mysql':
            conn = mysql.connector.connect(**MYSQL_CONFIG)
            return conn
        else:
            import sqlite3
            return sqlite3.connect('codex.db')
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create history table for tracking user activities
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
                INDEX idx_user_created (user_id, created_at)
            )
        ''')
        
        conn.commit()
        print(f"✅ MySQL database '{db_name}' initialized successfully!")
        cursor.close()
        conn.close()
        return True
        
    except Error as e:
        print(f"❌ Error initializing MySQL database: {e}")
        return False

def init_db():
    """Initialize database (MySQL or SQLite)"""
    if DB_TYPE == 'mysql':
        return init_mysql_database()
    else:
        # SQLite initialization (fallback)
        import sqlite3
        conn = sqlite3.connect('codex.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
