"""
Backup compression simulator (7-Zip, WinRAR style)
Simulates legitimate backup software creating compressed archives
"""

import sys
from pathlib import Path
import zipfile
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from simulator.core.speed_controller import SpeedController


class BackupSimulator:
    """
    Simulates legitimate backup compression software
    
    Characteristics:
    - Creates compressed .zip archive
    - Does NOT modify original files
    - Moderate speed (50 files/second)
    - High entropy output (compressed data)
    """
    
    def __init__(self, target_dir: str, speed: int = 50):
        """
        Initialize backup simulator
        
        Args:
            target_dir: Directory to backup
            speed: Files per second to compress
        """
        self.target_dir = Path(target_dir)
        self.speed = speed
        self.speed_controller = SpeedController(speed, "second")
        
        # Statistics
        self.files_compressed = 0
        self.files_failed = 0
        self.total_bytes_compressed = 0
    
    def run(self):
        """Execute backup compression"""
        print("=" * 60)
        print("[BACKUP] Backup Compression Simulation")
        print("=" * 60)
        print(f"[BACKUP] Source: {self.target_dir}")
        print(f"[BACKUP] Speed: {self.speed} files/second")
        print(f"[BACKUP] Type: ZIP compression (BENIGN)")
        print("=" * 60)
        
        # Find all files
        print("[BACKUP] Scanning files...")
        all_files = list(self.target_dir.rglob('*.*'))
        all_files = [f for f in all_files if f.is_file()]
        
        print(f"[BACKUP] Found {len(all_files)} files to backup")
        
        if not all_files:
            print("[BACKUP] No files to backup. Exiting.")
            return
        
        # Create backup archive
        backup_path = self.target_dir / f"backup_{int(time.time())}.zip"
        print(f"[BACKUP] Creating archive: {backup_path.name}")
        
        self.speed_controller.start()
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in all_files:
                    try:
                        # Add to archive
                        arcname = file_path.relative_to(self.target_dir)
                        zipf.write(file_path, arcname)
                        
                        # Track statistics
                        self.total_bytes_compressed += file_path.stat().st_size
                        self.files_compressed += 1
                        
                        print(f"[BACKUP] ✓ Compressed: {file_path.name}")
                        
                        # Rate limiting
                        self.speed_controller.wait()
                        
                    except Exception as e:
                        print(f"[BACKUP] ✗ Failed: {file_path} - {e}")
                        self.files_failed += 1
            
            print(f"[BACKUP] Archive created successfully: {backup_path}")
            
        except Exception as e:
            print(f"[BACKUP] Failed to create archive: {e}")
            return
        
        # Print statistics
        print("=" * 60)
        print("[BACKUP] Backup Complete!")
        print("=" * 60)
        print(f"Files compressed: {self.files_compressed}")
        print(f"Files failed: {self.files_failed}")
        print(f"Total data: {self.total_bytes_compressed / 1024:.2f} KB")
        print(f"Archive size: {backup_path.stat().st_size / 1024:.2f} KB")
        print(f"Compression ratio: {(1 - backup_path.stat().st_size / max(self.total_bytes_compressed, 1)) * 100:.1f}%")
        print(f"Time elapsed: {self.speed_controller.get_elapsed_time():.2f} seconds")
        print("=" * 60)
        print("✅ This is BENIGN activity - should NOT trigger EPA alerts")
        print("=" * 60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Backup compression simulator")
    parser.add_argument("target", help="Target directory to backup")
    parser.add_argument("--speed", type=int, default=50, help="Files per second (default: 50)")
    
    args = parser.parse_args()
    
    # Run simulation
    sim = BackupSimulator(args.target, args.speed)
    sim.run()


if __name__ == "__main__":
    main()
