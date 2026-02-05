"""
Unit tests for database operations
Tests database initialization, queries, and data integrity
"""

import unittest
import sys
import os
import sqlite3
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.db import init_db, get_conn


class TestDatabaseOperations(unittest.TestCase):
    """Test cases for database operations"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database"""
        cls.test_db = "test_db_operations.db"
        
        # Patch DB_PATH
        import shared.db
        shared.db.DB_PATH = cls.test_db
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
    
    def setUp(self):
        """Initialize fresh database for each test"""
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        init_db()
    
    def test_database_initialization(self):
        """Test database initializes correctly"""
        self.assertTrue(os.path.exists(self.test_db))
        
        # Check tables exist
        conn = get_conn()
        cur = conn.cursor()
        
        # Check entropy table
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entropy'")
        self.assertIsNotNone(cur.fetchone())
        
        # Check alerts table
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alerts'")
        self.assertIsNotNone(cur.fetchone())
        
        conn.close()
    
    def test_entropy_table_schema(self):
        """Test entropy table has correct schema"""
        conn = get_conn()
        cur = conn.cursor()
        
        cur.execute("PRAGMA table_info(entropy)")
        columns = {row[1]: row[2] for row in cur.fetchall()}
        
        self.assertIn('id', columns)
        self.assertIn('file', columns)
        self.assertIn('entropy', columns)
        self.assertIn('timestamp', columns)
        
        conn.close()
    
    def test_alerts_table_schema(self):
        """Test alerts table has correct schema"""
        conn = get_conn()
        cur = conn.cursor()
        
        cur.execute("PRAGMA table_info(alerts)")
        columns = {row[1]: row[2] for row in cur.fetchall()}
        
        self.assertIn('id', columns)
        self.assertIn('file', columns)
        self.assertIn('entropy', columns)
        self.assertIn('message', columns)
        self.assertIn('process_id', columns)
        self.assertIn('process_name', columns)
        self.assertIn('process_cmdline', columns)
        self.assertIn('process_parent', columns)
        self.assertIn('timestamp', columns)
        
        conn.close()
    
    def test_insert_entropy(self):
        """Test inserting entropy data"""
        conn = get_conn()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO entropy (file, entropy) VALUES (?, ?)",
            ("/test/file.txt", 4.5)
        )
        conn.commit()
        
        cur.execute("SELECT file, entropy FROM entropy")
        result = cur.fetchone()
        
        self.assertEqual(result[0], "/test/file.txt")
        self.assertEqual(result[1], 4.5)
        
        conn.close()
    
    def test_insert_alert(self):
        """Test inserting alert data"""
        conn = get_conn()
        cur = conn.cursor()
        
        cur.execute(
            """INSERT INTO alerts 
               (file, entropy, message, process_id, process_name, process_cmdline, process_parent) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            ("/test/alert.txt", 7.5, "Test alert", 1234, "test", "test.py", "bash")
        )
        conn.commit()
        
        cur.execute("SELECT * FROM alerts")
        result = cur.fetchone()
        
        self.assertEqual(result[1], "/test/alert.txt")
        self.assertEqual(result[2], 7.5)
        self.assertEqual(result[3], "Test alert")
        self.assertEqual(result[4], 1234)
        
        conn.close()
    
    def test_multiple_entropy_entries(self):
        """Test storing multiple entropy measurements for same file"""
        conn = get_conn()
        cur = conn.cursor()
        
        # Insert multiple measurements
        for i in range(5):
            cur.execute(
                "INSERT INTO entropy (file, entropy) VALUES (?, ?)",
                ("/test/file.txt", 4.0 + i * 0.5)
            )
        conn.commit()
        
        # Query all measurements
        cur.execute("SELECT entropy FROM entropy WHERE file = ?", ("/test/file.txt",))
        results = cur.fetchall()
        
        self.assertEqual(len(results), 5)
        
        conn.close()
    
    def test_timestamp_auto_generation(self):
        """Test that timestamps are automatically generated"""
        conn = get_conn()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO entropy (file, entropy) VALUES (?, ?)",
            ("/test/file.txt", 5.0)
        )
        conn.commit()
        
        cur.execute("SELECT timestamp FROM entropy")
        timestamp = cur.fetchone()[0]
        
        self.assertIsNotNone(timestamp)
        
        conn.close()
    
    def test_query_recent_alerts(self):
        """Test querying recent alerts"""
        conn = get_conn()
        cur = conn.cursor()
        
        # Insert multiple alerts
        for i in range(10):
            cur.execute(
                "INSERT INTO alerts (file, entropy, message) VALUES (?, ?, ?)",
                (f"/test/file_{i}.txt", 6.0 + i, f"Alert {i}")
            )
        conn.commit()
        
        # Query recent alerts
        cur.execute("SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 5")
        results = cur.fetchall()
        
        self.assertEqual(len(results), 5)
        
        conn.close()
    
    def test_query_entropy_statistics(self):
        """Test querying entropy statistics"""
        conn = get_conn()
        cur = conn.cursor()
        
        # Insert entropy data
        entropies = [3.5, 4.0, 4.5, 5.0, 7.5]
        for e in entropies:
            cur.execute(
                "INSERT INTO entropy (file, entropy) VALUES (?, ?)",
                ("/test/file.txt", e)
            )
        conn.commit()
        
        # Query statistics
        cur.execute("SELECT MIN(entropy), MAX(entropy), AVG(entropy) FROM entropy")
        min_e, max_e, avg_e = cur.fetchone()
        
        self.assertEqual(min_e, 3.5)
        self.assertEqual(max_e, 7.5)
        self.assertAlmostEqual(avg_e, 4.9, places=1)
        
        conn.close()
    
    def test_connection_reuse(self):
        """Test that get_conn() returns working connections"""
        conn1 = get_conn()
        conn2 = get_conn()
        
        # Both should be valid connections
        self.assertIsNotNone(conn1)
        self.assertIsNotNone(conn2)
        
        # Both should be able to execute queries
        cur1 = conn1.cursor()
        cur1.execute("SELECT 1")
        self.assertEqual(cur1.fetchone()[0], 1)
        
        cur2 = conn2.cursor()
        cur2.execute("SELECT 1")
        self.assertEqual(cur2.fetchone()[0], 1)
        
        conn1.close()
        conn2.close()


if __name__ == '__main__':
    unittest.main()
