"""
Encryption utilities for secure wallet storage
"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os


class Encryptor:
    """Handle encryption and decryption of sensitive data"""

    def __init__(self, master_password: str):
        """
        Initialize encryptor with master password

        Args:
            master_password: Master password for encryption
        """
        self.master_password = master_password.encode()
        self.salt = b'airdrop_farmer_salt_v1'  # In production, use random salt per user

    def _get_key(self) -> bytes:
        """Derive encryption key from master password"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_password))
        return key

    def encrypt(self, data: str) -> str:
        """
        Encrypt data

        Args:
            data: String to encrypt

        Returns:
            Encrypted string
        """
        f = Fernet(self._get_key())
        encrypted = f.encrypt(data.encode())
        return encrypted.decode()

    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt data

        Args:
            encrypted_data: Encrypted string

        Returns:
            Decrypted string
        """
        f = Fernet(self._get_key())
        decrypted = f.decrypt(encrypted_data.encode())
        return decrypted.decode()

    @staticmethod
    def generate_salt() -> str:
        """Generate a random salt for encryption"""
        return base64.urlsafe_b64encode(os.urandom(16)).decode()
