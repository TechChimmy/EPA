"""
Video encoding simulator
Simulates legitimate video compression/encoding software
"""

import sys
from pathlib import Path
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from simulator.core.speed_controller import SpeedController


class VideoSimulator:
    """
    Simulates legitimate video encoding software
    
    Characteristics:
    - Creates compressed video files (.mp4)
    - Very high entropy (compressed video)
    - Slow processing (1 file/minute, realistic for video)
    - Does NOT modify source files
    """
    
    def __init__(self, target_dir: str, video_count: int = 3, speed: int = 1):
        """
        Initialize video simulator
        
        Args:
            target_dir: Directory to create videos in
            video_count: Number of videos to encode
            speed: Videos per minute
        """
        self.target_dir = Path(target_dir)
        self.video_count = video_count
        self.speed = speed
        self.speed_controller = SpeedController(speed, "minute")
        
        # Statistics
        self.videos_encoded = 0
        self.total_bytes_created = 0
    
    def encode_video(self, video_id: int, size_mb: int = 10):
        """
        Simulate video encoding
        
        Args:
            video_id: Video identifier
            size_mb: Size of output video in MB
        """
        video_path = self.target_dir / f"video_{video_id:03d}.mp4"
        
        print(f"[VIDEO] Encoding video {video_id}...")
        print(f"[VIDEO]   Output: {video_path.name}")
        print(f"[VIDEO]   Target size: {size_mb} MB")
        
        try:
            # Simulate video encoding by creating file with random data
            # (compressed video has very high entropy)
            video_data = os.urandom(size_mb * 1024 * 1024)
            
            # Write in chunks to simulate progressive encoding
            chunk_size = 1024 * 1024  # 1 MB chunks
            with open(video_path, 'wb') as f:
                for i in range(0, len(video_data), chunk_size):
                    chunk = video_data[i:i+chunk_size]
                    f.write(chunk)
                    progress = ((i + len(chunk)) / len(video_data)) * 100
                    print(f"[VIDEO]   Progress: {progress:.1f}%")
            
            self.total_bytes_created += len(video_data)
            self.videos_encoded += 1
            
            print(f"[VIDEO] ✓ Encoded: {video_path.name}")
            
        except Exception as e:
            print(f"[VIDEO] ✗ Failed to encode video {video_id}: {e}")
    
    def run(self):
        """Execute video encoding simulation"""
        print("=" * 60)
        print("[VIDEO] Video Encoding Simulation")
        print("=" * 60)
        print(f"[VIDEO] Output directory: {self.target_dir}")
        print(f"[VIDEO] Videos to encode: {self.video_count}")
        print(f"[VIDEO] Speed: {self.speed} video(s)/minute")
        print(f"[VIDEO] Type: MP4 compression (BENIGN)")
        print("=" * 60)
        
        self.speed_controller.start()
        
        for i in range(1, self.video_count + 1):
            print(f"\n[VIDEO] === Encoding video {i}/{self.video_count} ===")
            self.encode_video(i, size_mb=10)
            
            # Rate limiting (except for last video)
            if i < self.video_count:
                print(f"[VIDEO] Waiting before next encode...")
                self.speed_controller.wait()
        
        # Print statistics
        print("\n" + "=" * 60)
        print("[VIDEO] Encoding Complete!")
        print("=" * 60)
        print(f"Videos encoded: {self.videos_encoded}")
        print(f"Total data created: {self.total_bytes_created / (1024 * 1024):.2f} MB")
        print(f"Time elapsed: {self.speed_controller.get_elapsed_time() / 60:.2f} minutes")
        print("=" * 60)
        print("✅ This is BENIGN activity - should NOT trigger EPA alerts")
        print("=" * 60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Video encoding simulator")
    parser.add_argument("target", help="Target directory for encoded videos")
    parser.add_argument("--count", type=int, default=3, help="Number of videos to encode (default: 3)")
    parser.add_argument("--speed", type=int, default=1, help="Videos per minute (default: 1)")
    
    args = parser.parse_args()
    
    # Run simulation
    sim = VideoSimulator(args.target, args.count, args.speed)
    sim.run()


if __name__ == "__main__":
    main()
