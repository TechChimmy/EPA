"""
Speed controller for rate-limiting file encryption operations
"""

import time


class SpeedController:
    """Controls the rate of file encryption to simulate different attack speeds"""
    
    def __init__(self, speed: int, unit: str = "second"):
        """
        Initialize speed controller
        
        Args:
            speed: Number of files to process per unit
            unit: Time unit ('second' or 'minute')
        """
        self.speed = speed
        self.unit = unit.lower()
        self.delay = self._calculate_delay()
        self.files_processed = 0
        self.start_time = None
    
    def _calculate_delay(self) -> float:
        """
        Calculate delay between file operations
        
        Returns:
            Delay in seconds
        """
        if self.unit == "second":
            return 1.0 / self.speed if self.speed > 0 else 0
        elif self.unit == "minute":
            return 60.0 / self.speed if self.speed > 0 else 0
        else:
            raise ValueError(f"Unknown unit: {self.unit}. Use 'second' or 'minute'")
    
    def start(self):
        """Start the speed controller timer"""
        self.start_time = time.time()
        self.files_processed = 0
    
    def wait(self):
        """Wait for the calculated delay before next operation"""
        if self.delay > 0:
            time.sleep(self.delay)
        self.files_processed += 1
    
    def get_elapsed_time(self) -> float:
        """
        Get elapsed time since start
        
        Returns:
            Elapsed time in seconds
        """
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time
    
    def get_actual_rate(self) -> float:
        """
        Get actual processing rate
        
        Returns:
            Files per second
        """
        elapsed = self.get_elapsed_time()
        if elapsed == 0:
            return 0.0
        return self.files_processed / elapsed
    
    def get_stats(self) -> dict:
        """
        Get statistics about processing speed
        
        Returns:
            Dictionary with speed statistics
        """
        return {
            'files_processed': self.files_processed,
            'elapsed_seconds': self.get_elapsed_time(),
            'target_rate': f"{self.speed} files/{self.unit}",
            'actual_rate': f"{self.get_actual_rate():.2f} files/second"
        }


class BurstController(SpeedController):
    """
    Speed controller with burst mode for intermittent attacks
    """
    
    def __init__(self, burst_size: int, burst_delay: float, files_per_burst: int):
        """
        Initialize burst controller
        
        Args:
            burst_size: Number of files to encrypt in each burst
            burst_delay: Delay between bursts (seconds)
            files_per_burst: Speed within a burst (files per second)
        """
        super().__init__(files_per_burst, "second")
        self.burst_size = burst_size
        self.burst_delay = burst_delay
        self.files_in_current_burst = 0
    
    def wait(self):
        """Wait with burst logic"""
        self.files_in_current_burst += 1
        
        # If burst is complete, wait for burst delay
        if self.files_in_current_burst >= self.burst_size:
            time.sleep(self.burst_delay)
            self.files_in_current_burst = 0
        else:
            # Normal delay within burst
            super().wait()
