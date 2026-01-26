import sqlite3
import os

DB_PATH = "epa.db"

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    """Initialize database with entropy and alerts tables"""
    try:
        conn = get_conn()
        cur = conn.cursor()

        # Create entropy table
        cur.execute("""
        CREATE TABLE IF NOT EXISTS entropy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file TEXT,
            entropy REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Create alerts table with process monitoring columns
        cur.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file TEXT,
            entropy REAL,
            message TEXT,
            process_id INTEGER,
            process_name TEXT,
            process_cmdline TEXT,
            process_parent TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        conn.commit()
        conn.close()
        
        print(f"✅ Database initialized successfully: {os.path.abspath(DB_PATH)}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False
