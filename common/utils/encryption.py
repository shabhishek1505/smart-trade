"""Encryption utilities for sensitive data"""

from cryptography.fernet import Fernet
import os
import base64


def generate_encryption_key() -> str:
    """Generate a new encryption key for credentials

    Returns:
        Base64-encoded encryption key
    """
    key = Fernet.generate_key()
    return key.decode()


def get_encryption_key() -> str:
    """Get encryption key from environment or config

    Returns:
        Encryption key string

    Raises:
        ValueError: If encryption key is not configured
    """
    key = os.getenv("ENCRYPTION_KEY")
    if not key:
        raise ValueError(
            "ENCRYPTION_KEY environment variable not set. "
            "Generate one using: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
        )
    return key


def encrypt_value(value: str, encryption_key: str = None) -> str:
    """Encrypt a value

    Args:
        value: String to encrypt
        encryption_key: Encryption key (uses env var if not provided)

    Returns:
        Encrypted value
    """
    if not encryption_key:
        encryption_key = get_encryption_key()

    cipher_suite = Fernet(encryption_key.encode())
    encrypted = cipher_suite.encrypt(value.encode())
    return encrypted.decode()


def decrypt_value(encrypted_value: str, encryption_key: str = None) -> str:
    """Decrypt a value

    Args:
        encrypted_value: Encrypted string
        encryption_key: Encryption key (uses env var if not provided)

    Returns:
        Decrypted value
    """
    if not encryption_key:
        encryption_key = get_encryption_key()

    cipher_suite = Fernet(encryption_key.encode())
    decrypted = cipher_suite.decrypt(encrypted_value.encode())
    return decrypted.decode()
