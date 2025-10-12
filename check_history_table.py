from database import execute_query, DB_TYPE

print("=" * 60)
print("Checking CODEX Database Tables")
print("=" * 60)
print()

try:
    # Check tables
    if DB_TYPE == 'mysql':
        tables = execute_query('SHOW TABLES', fetch=True)
    else:
        tables = execute_query("SELECT name FROM sqlite_master WHERE type='table'", fetch=True)
    
    print(f"Database Type: {DB_TYPE.upper()}")
    print(f"\nTables found:")
    for table in tables:
        print(f"  ✅ {table[0]}")
    
    print()
    
    # Check code_history structure
    print("code_history table structure:")
    if DB_TYPE == 'mysql':
        columns = execute_query('DESCRIBE code_history', fetch=True)
        for col in columns:
            print(f"  - {col[0]}: {col[1]}")
    
    print()
    
    # Check if any history exists
    count = execute_query('SELECT COUNT(*) FROM code_history', fetch=True)
    print(f"Current history items: {count[0][0]}")
    
    print()
    print("=" * 60)
    print("✅ Database is ready for history tracking!")
    print("=" * 60)
    
except Exception as e:
    print(f"Error: {e}")
