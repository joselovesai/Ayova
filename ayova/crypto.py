"""Encryption utilities using Fernet (AES-128-CBC + HMAC)"""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os


class CryptoVault:
    """Handles encryption/decryption with password-derived keys"""
    
    def __init__(self, password: str, salt: bytes = None):
        self.salt = salt or os.urandom(16)
        self.key = self._derive_key(password, self.salt)
        self.fernet = Fernet(self.key)
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,  # OWASP recommended
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, message: str) -> tuple[bytes, bytes]:
        """Encrypt message, return (encrypted_data, salt)"""
        encrypted = self.fernet.encrypt(message.encode())
        return encrypted, self.salt
    
    def decrypt(self, encrypted_data: bytes, salt: bytes) -> str:
        """Decrypt message using stored salt"""
        # Re-derive key with stored salt
        key = self._derive_key(self._password, salt)
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data).decode()
    
    @property
    def _password(self) -> str:
        # Store password reference for re-derivation
        return self._pwd
    
    @_password.setter
    def _password(self, value):
        self._pwd = value
    
    def set_password(self, password: str):
        self._password = password


def encrypt_with_password(message: str, password: str) -> tuple[bytes, bytes]:
    """One-shot encryption"""
    vault = CryptoVault(password)
    vault.set_password(password)
    return vault.encrypt(message)


def decrypt_with_password(encrypted_data: bytes, salt: bytes, password: str) -> str:
    """One-shot decryption"""
    vault = CryptoVault(password, salt)
    vault.set_password(password)
    return vault.decrypt(encrypted_data, salt)
