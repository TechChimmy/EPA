"""
Encryption engine providing multiple encryption algorithms for ransomware simulation
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os


class EncryptionEngine:
    """Provides various encryption methods for realistic ransomware simulation"""
    
    def __init__(self, algorithm="fernet"):
        """
        Initialize encryption engine
        
        Args:
            algorithm: Encryption algorithm to use ('fernet', 'aes256', 'chacha20')
        """
        self.algorithm = algorithm.lower()
        self.key = None
        self._initialize_key()
    
    def _initialize_key(self):
        """Initialize encryption key based on algorithm"""
        if self.algorithm == "fernet":
            self.key = Fernet.generate_key()
            self.cipher = Fernet(self.key)
        elif self.algorithm == "aes256":
            self.key = os.urandom(32)  # 256-bit key
        elif self.algorithm == "chacha20":
            self.key = os.urandom(32)  # 256-bit key
        else:
            raise ValueError(f"Unknown algorithm: {self.algorithm}")
    
    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt data using the configured algorithm
        
        Args:
            data: Raw bytes to encrypt
            
        Returns:
            Encrypted bytes
        """
        if self.algorithm == "fernet":
            return self._fernet_encrypt(data)
        elif self.algorithm == "aes256":
            return self._aes256_encrypt(data)
        elif self.algorithm == "chacha20":
            return self._chacha20_encrypt(data)
    
    def _fernet_encrypt(self, data: bytes) -> bytes:
        """Fernet encryption (AES-128 in CBC mode)"""
        return self.cipher.encrypt(data)
    
    def _aes256_encrypt(self, data: bytes) -> bytes:
        """AES-256 encryption in CBC mode"""
        iv = os.urandom(16)  # Initialization vector
        cipher = Cipher(
            algorithms.AES(self.key),
            modes.CBC(iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        # Pad data to block size (16 bytes for AES)
        padding_length = 16 - (len(data) % 16)
        padded_data = data + bytes([padding_length] * padding_length)
        
        encrypted = encryptor.update(padded_data) + encryptor.finalize()
        
        # Prepend IV for decryption (in real ransomware, this would be stored)
        return iv + encrypted
    
    def _chacha20_encrypt(self, data: bytes) -> bytes:
        """ChaCha20 encryption (modern stream cipher)"""
        nonce = os.urandom(16)
        cipher = Cipher(
            algorithms.ChaCha20(self.key, nonce),
            mode=None,
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(data) + encryptor.finalize()
        
        # Prepend nonce
        return nonce + encrypted


def quick_encrypt(data: bytes, algorithm="fernet") -> bytes:
    """
    Quick encryption helper function
    
    Args:
        data: Bytes to encrypt
        algorithm: Algorithm to use
        
    Returns:
        Encrypted bytes
    """
    engine = EncryptionEngine(algorithm)
    return engine.encrypt(data)
