"""
Database operations simulator
Simulates legitimate database writes with high-entropy data
"""

import sys
from pathlib import Path
import sqlite3
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from simulator.core.speed_controller import SpeedController


class DatabaseSimulator:
    """
    Simulates legitimate database operations
    
    Characteristics:
    - Writes to SQLite database
    - High entropy data (binary blobs, encrypted fields)
    - Variable speed (10-100 operations/second)
    - Does NOT modify user files
    """
    
    def __init__(self, target_dir: str, operations: int = 100, speed: int = 50):
        """
        Initialize database simulator
        
        Args:
            target_dir: Directory to create database in
            operations: Number of database operations
            speed: Operations per second
        """
        self.target_dir = Path(target_dir)
        self.operations = operations
        self.speed = speed
        self.speed_controller = SpeedController(speed, "second")
        
        # Database path
        self.db_path = self.target_dir / f"application_{int(time.time())}.db"
        
        # Statistics
        self.records_written = 0
        self.total_bytes_written = 0
    
    def setup_database(self, conn):
        """Create database schema"""
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password_hash BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                session_token BLOB,
                data BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                level TEXT,
                message TEXT,
                binary_data BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        print("[DATABASE] Schema created")
    
    def write_user_record(self, conn, user_id):
        """Write a user record with encrypted password"""
        cursor = conn.cursor()
        
        # Simulate password hash (high entropy)
        password_hash = os.urandom(64)
        
        cursor.execute(
            "INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
            (user_id, f"user_{user_id}", password_hash)
        )
        
        self.total_bytes_written += len(password_hash)
        self.records_written += 1
    
    def write_session_record(self, conn, session_id):
        """Write a session record with encrypted data"""
        cursor = conn.cursor()
        
        # Simulate session token and encrypted session data (high entropy)
        session_token = os.urandom(32)
        session_data = os.urandom(256)
        
        cursor.execute(
            "INSERT INTO sessions (id, user_id, session_token, data) VALUES (?, ?, ?, ?)",
            (session_id, session_id % 100, session_token, session_data)
        )
        
        self.total_bytes_written += len(session_token) + len(session_data)
        self.records_written += 1
    
    def write_log_record(self, conn, log_id):
        """Write a log record with binary data"""
        cursor = conn.cursor()
        
        # Simulate log with binary payload
        binary_data = os.urandom(128)
        
        cursor.execute(
            "INSERT INTO logs (id, level, message, binary_data) VALUES (?, ?, ?, ?)",
            (log_id, "INFO", f"Log entry {log_id}", binary_data)
        )
        
        self.total_bytes_written += len(binary_data)
        self.records_written += 1
    
    def run(self):
        """Execute database operations"""
        print("=" * 60)
        print("[DATABASE] Database Operations Simulation")
        print("=" * 60)
        print(f"[DATABASE] Location: {self.db_path}")
        print(f"[DATABASE] Operations: {self.operations}")
        print(f"[DATABASE] Speed: {self.speed} ops/second")
        print(f"[DATABASE] Type: SQLite with encrypted data (BENIGN)")
        print("=" * 60)
        
        # Create database
        print("[DATABASE] Creating database...")
        conn = sqlite3.connect(self.db_path)
        self.setup_database(conn)
        
        # Start operations
        print("[DATABASE] Writing records...")
        self.speed_controller.start()
        
        for i in range(self.operations):
            # Mix of different record types
            if i % 3 == 0:
                self.write_user_record(conn, i)
                print(f"[DATABASE] ✓ User record {i}")
            elif i % 3 == 1:
                self.write_session_record(conn, i)
                print(f"[DATABASE] ✓ Session record {i}")
            else:
                self.write_log_record(conn, i)
                print(f"[DATABASE] ✓ Log record {i}")
            
            # Commit every 10 records
            if i % 10 == 0:
                conn.commit()
            
            # Rate limiting
            self.speed_controller.wait()
        
        # Final commit
        conn.commit()
        conn.close()
        
        # Print statistics
        print("=" * 60)
        print("[DATABASE] Operations Complete!")
        print("=" * 60)
        print(f"Records written: {self.records_written}")
        print(f"Total data written: {self.total_bytes_written / 1024:.2f} KB")
        print(f"Database size: {self.db_path.stat().st_size / 1024:.2f} KB")
        print(f"Time elapsed: {self.speed_controller.get_elapsed_time():.2f} seconds")
        print("=" * 60)
        print("✅ This is BENIGN activity - should NOT trigger EPA alerts")
        print("=" * 60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database operations simulator")
    parser.add_argument("target", help="Target directory for database")
    parser.add_argument("--operations", type=int, default=100, help="Number of operations (default: 100)")
    parser.add_argument("--speed", type=int, default=50, help="Operations per second (default: 50)")
    
    args = parser.parse_args()
    
    # Run simulation
    sim = DatabaseSimulator(args.target, args.operations, args.speed)
    sim.run()


if __name__ == "__main__":
    main()
