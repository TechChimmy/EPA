"""
Unit tests for detection algorithms
Tests CUSUM and Z-score detection methods
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from detection.cusum import CUSUM
from detection.zscore import is_anomaly


class TestCUSUMDetection(unittest.TestCase):
    """Test cases for CUSUM algorithm"""
    
    def test_cusum_initialization(self):
        """Test CUSUM initializes correctly"""
        cusum = CUSUM(drift=0.1, threshold=1.5)
        self.assertEqual(cusum.drift, 0.1)
        self.assertEqual(cusum.threshold, 1.5)
        self.assertEqual(cusum.cumsum, 0.0)
    
    def test_cusum_no_drift(self):
        """Test CUSUM with no significant drift"""
        cusum = CUSUM(drift=0.1, threshold=1.5)
        
        # Small deviations should not trigger
        for _ in range(10):
            result = cusum.update(0.05)
            self.assertFalse(result)
    
    def test_cusum_slow_attack(self):
        """Test CUSUM detects slow drift"""
        cusum = CUSUM(drift=0.1, threshold=1.5)
        
        # Gradual increase should eventually trigger
        triggered = False
        for i in range(20):
            result = cusum.update(0.3)  # Consistent positive deviation
            if result:
                triggered = True
                break
        
        self.assertTrue(triggered, "CUSUM should detect slow drift")
    
    def test_cusum_threshold(self):
        """Test CUSUM threshold behavior"""
        cusum = CUSUM(drift=0.1, threshold=1.0)
        
        # Large deviation should trigger quickly
        result = cusum.update(2.0)
        self.assertTrue(result)
    
    def test_cusum_reset_after_detection(self):
        """Test CUSUM resets after detection"""
        cusum = CUSUM(drift=0.1, threshold=1.0)
        
        # Trigger detection
        cusum.update(2.0)
        
        # Cumsum should be reset
        self.assertEqual(cusum.cumsum, 0.0)
    
    def test_cusum_negative_values(self):
        """Test CUSUM with negative deviations"""
        cusum = CUSUM(drift=0.1, threshold=1.5)
        
        # Negative values should not accumulate (max with 0)
        for _ in range(10):
            result = cusum.update(-0.5)
            self.assertFalse(result)
        
        # Cumsum should not go negative
        self.assertGreaterEqual(cusum.cumsum, 0.0)


class TestZScoreDetection(unittest.TestCase):
    """Test cases for Z-score anomaly detection"""
    
    def test_zscore_no_anomaly(self):
        """Test Z-score with value within normal range"""
        mean = 5.0
        std = 1.0
        value = 5.5  # 0.5 std deviations from mean
        threshold = 3.0
        
        result = is_anomaly(value, mean, std, threshold)
        self.assertFalse(result)
    
    def test_zscore_anomaly_positive(self):
        """Test Z-score detects positive anomaly"""
        mean = 5.0
        std = 1.0
        value = 8.5  # 3.5 std deviations from mean
        threshold = 3.0
        
        result = is_anomaly(value, mean, std, threshold)
        self.assertTrue(result)
    
    def test_zscore_anomaly_negative(self):
        """Test Z-score detects negative anomaly"""
        mean = 5.0
        std = 1.0
        value = 1.5  # -3.5 std deviations from mean
        threshold = 3.0
        
        result = is_anomaly(value, mean, std, threshold)
        self.assertTrue(result)
    
    def test_zscore_exact_threshold(self):
        """Test Z-score at exact threshold"""
        mean = 5.0
        std = 1.0
        value = 8.0  # Exactly 3.0 std deviations
        threshold = 3.0
        
        result = is_anomaly(value, mean, std, threshold)
        self.assertFalse(result)  # Should be > threshold, not >=
    
    def test_zscore_zero_std(self):
        """Test Z-score with zero standard deviation"""
        mean = 5.0
        std = 0.0
        value = 5.0
        threshold = 3.0
        
        # Should handle division by zero gracefully
        result = is_anomaly(value, mean, std, threshold)
        self.assertFalse(result)
    
    def test_zscore_different_thresholds(self):
        """Test Z-score with different threshold values"""
        mean = 5.0
        std = 1.0
        value = 7.5  # 2.5 std deviations
        
        # Should not trigger with threshold 3.0
        self.assertFalse(is_anomaly(value, mean, std, 3.0))
        
        # Should trigger with threshold 2.0
        self.assertTrue(is_anomaly(value, mean, std, 2.0))
    
    def test_zscore_realistic_entropy(self):
        """Test Z-score with realistic entropy values"""
        # Normal file entropy
        mean = 4.5
        std = 0.5
        
        # Normal variation
        self.assertFalse(is_anomaly(4.8, mean, std, 3.0))
        
        # Encrypted file (high entropy)
        self.assertTrue(is_anomaly(7.5, mean, std, 3.0))


class TestDetectionIntegration(unittest.TestCase):
    """Integration tests for detection algorithms"""
    
    def test_combined_detection(self):
        """Test CUSUM and Z-score working together"""
        cusum = CUSUM(drift=0.1, threshold=1.5)
        
        # Simulate gradual entropy increase
        baseline_mean = 4.0
        baseline_std = 0.5
        
        # Normal values
        for entropy in [4.0, 4.1, 4.2, 4.0, 4.1]:
            deviation = (entropy - baseline_mean) / baseline_std
            cusum_triggered = cusum.update(deviation)
            zscore_triggered = is_anomaly(entropy, baseline_mean, baseline_std, 3.0)
            
            self.assertFalse(cusum_triggered)
            self.assertFalse(zscore_triggered)
        
        # Sudden spike (should trigger Z-score)
        high_entropy = 7.0
        zscore_triggered = is_anomaly(high_entropy, baseline_mean, baseline_std, 3.0)
        self.assertTrue(zscore_triggered)


if __name__ == '__main__':
    unittest.main()
