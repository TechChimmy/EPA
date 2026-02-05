"""
Unit tests for alert system
Tests alert generation and database storage
"""

import unittest
import sys
import os
import sqlite3
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from alert.alert import raise_alert
from shared.db import init_db, get_conn


class TestAlertSystem(unittest.TestCase):
    """Test cases for alert generation and storage"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test database"""
        # Use test database
        cls.test_db = "test_epa.db"
        
        # Patch DB_PATH in shared.db
        import shared.db
        shared.db.DB_PATH = cls.test_db
        
        # Initialize test database
        init_db()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
    
    def setUp(self):
        """Clear alerts table before each test"""
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM alerts")
        conn.commit()
        conn.close()
    
    def test_alert_creation_basic(self):
        """Test basic alert creation"""
        raise_alert(
            file="/test/file.txt",
            entropy=7.5,
            message="Test alert",
            process_info=None
        )
        
        # Verify alert was stored
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM alerts")
        alerts = cur.fetchall()
        conn.close()
        
        self.assertEqual(len(alerts), 1)
        alert = alerts[0]
        self.assertEqual(alert[1], "/test/file.txt")  # file
        self.assertEqual(alert[2], 7.5)  # entropy
        self.assertEqual(alert[3], "Test alert")  # message
    
    def test_alert_with_process_info(self):
        """Test alert with process attribution"""
        process_info = {
            "pid": 1234,
            "name": "test_process",
            "cmdline": "python test.py",
            "parent": "bash"
        }
        
        raise_alert(
            file="/test/encrypted.txt",
            entropy=8.0,
            message="High entropy detected",
            process_info=process_info
        )
        
        # Verify process info was stored
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT process_id, process_name, process_cmdline, process_parent FROM alerts")
        result = cur.fetchone()
        conn.close()
        
        self.assertEqual(result[0], 1234)
        self.assertEqual(result[1], "test_process")
        self.assertEqual(result[2], "python test.py")
        self.assertEqual(result[3], "bash")
    
    def test_multiple_alerts(self):
        """Test multiple alerts are stored correctly"""
        for i in range(5):
            raise_alert(
                file=f"/test/file_{i}.txt",
                entropy=6.0 + i * 0.5,
                message=f"Alert {i}",
                process_info=None
            )
        
        # Verify all alerts were stored
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM alerts")
        count = cur.fetchone()[0]
        conn.close()
        
        self.assertEqual(count, 5)
    
    def test_alert_timestamp(self):
        """Test that alerts have timestamps"""
        raise_alert(
            file="/test/file.txt",
            entropy=7.0,
            message="Test timestamp",
            process_info=None
        )
        
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT timestamp FROM alerts")
        timestamp = cur.fetchone()[0]
        conn.close()
        
        self.assertIsNotNone(timestamp)
        self.assertIsInstance(timestamp, str)
    
    def test_alert_high_entropy(self):
        """Test alert for high entropy detection"""
        raise_alert(
            file="/test/encrypted.bin",
            entropy=7.9,
            message="Critical: High entropy detected on first modification (7.90)",
            process_info={"pid": 5678, "name": "ransomware", "cmdline": "evil.exe", "parent": "explorer"}
        )
        
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT file, entropy, message FROM alerts")
        result = cur.fetchone()
        conn.close()
        
        self.assertIn("Critical", result[2])
        self.assertGreater(result[1], 5.5)
    
    def test_alert_cusum_detection(self):
        """Test alert for CUSUM detection"""
        raise_alert(
            file="/test/slow_encrypt.txt",
            entropy=6.2,
            message="CUSUM threshold exceeded - slow attack detected",
            process_info={"pid": 9999, "name": "slow_ransom", "cmdline": "slow.py", "parent": "python"}
        )
        
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT message FROM alerts")
        message = cur.fetchone()[0]
        conn.close()
        
        self.assertIn("CUSUM", message)
    
    def test_alert_zscore_detection(self):
        """Test alert for Z-score detection"""
        raise_alert(
            file="/test/anomaly.txt",
            entropy=6.5,
            message="Abnormal entropy spike detected (z>3.0)",
            process_info=None
        )
        
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT message FROM alerts")
        message = cur.fetchone()[0]
        conn.close()
        
        self.assertIn("spike", message.lower())


if __name__ == '__main__':
    unittest.main()
