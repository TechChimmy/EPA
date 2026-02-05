"""
Unit tests for entropy calculation module
Tests Shannon entropy calculation accuracy
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from entropy.entropy import shannon_entropy


class TestEntropyCalculation(unittest.TestCase):
    """Test cases for Shannon entropy calculation"""
    
    def test_zero_entropy(self):
        """Test that uniform data has zero entropy"""
        # All zeros should have entropy close to 0
        data = b'\x00' * 1000
        entropy = shannon_entropy(data)
        self.assertAlmostEqual(entropy, 0.0, places=2)
    
    def test_max_entropy(self):
        """Test that random data has high entropy"""
        # Random bytes should have entropy close to 8.0
        import os
        data = os.urandom(1000)
        entropy = shannon_entropy(data)
        self.assertGreater(entropy, 7.5)
        self.assertLessEqual(entropy, 8.0)
    
    def test_low_entropy_text(self):
        """Test that plain text has low entropy"""
        # Plain text should have entropy < 5.0
        data = b"Hello World! This is a test message. " * 50
        entropy = shannon_entropy(data)
        self.assertLess(entropy, 5.0)
    
    def test_high_entropy_encrypted(self):
        """Test that encrypted data has high entropy"""
        from cryptography.fernet import Fernet
        
        # Encrypt some data
        key = Fernet.generate_key()
        f = Fernet(key)
        plaintext = b"This is secret data that will be encrypted"
        encrypted = f.encrypt(plaintext)
        
        # Encrypted data should have high entropy
        entropy = shannon_entropy(encrypted)
        self.assertGreater(entropy, 5.4)
    
    def test_empty_data(self):
        """Test handling of empty data"""
        data = b""
        entropy = shannon_entropy(data)
        self.assertEqual(entropy, 0.0)
    
    def test_single_byte(self):
        """Test handling of single byte"""
        data = b"A"
        entropy = shannon_entropy(data)
        self.assertEqual(entropy, 0.0)
    
    def test_two_values(self):
        """Test entropy with two different values"""
        # 50/50 distribution should have entropy close to 1.0
        data = b'\x00\xFF' * 500
        entropy = shannon_entropy(data)
        self.assertAlmostEqual(entropy, 1.0, places=1)
    
    def test_base64_encoded(self):
        """Test that base64 encoded data has moderate entropy"""
        import base64
        plaintext = b"This is some data to encode"
        encoded = base64.b64encode(plaintext)
        
        entropy = shannon_entropy(encoded)
        # Base64 has entropy around 4-6 range
        self.assertGreater(entropy, 4.0)
        self.assertLess(entropy, 7.0)
    
    def test_consistency(self):
        """Test that same data produces same entropy"""
        data = b"Test data for consistency check"
        entropy1 = shannon_entropy(data)
        entropy2 = shannon_entropy(data)
        self.assertEqual(entropy1, entropy2)
    
    def test_different_data_different_entropy(self):
        """Test that different data produces different entropy"""
        data1 = b"A" * 1000
        data2 = b"AB" * 500
        
        entropy1 = shannon_entropy(data1)
        entropy2 = shannon_entropy(data2)
        
        self.assertNotEqual(entropy1, entropy2)


if __name__ == '__main__':
    unittest.main()
