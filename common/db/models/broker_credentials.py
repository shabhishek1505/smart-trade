from sqlalchemy import Column, Integer, String, Boolean, DateTime, LargeBinary
from datetime import datetime
from common.db.base import Base
from cryptography.fernet import Fernet
import os
import json


class BrokerCredentials(Base):
    __tablename__ = "broker_credentials"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    broker_type = Column(String(50), nullable=False)  # "angel_one", "zerodha", etc.

    # Encrypted fields - stored as binary
    encrypted_api_key = Column(LargeBinary, nullable=False)
    encrypted_api_secret = Column(LargeBinary, nullable=False)
    encrypted_client_code = Column(LargeBinary, nullable=True)
    encrypted_pin = Column(LargeBinary, nullable=True)
    encrypted_totp_key = Column(LargeBinary, nullable=True)

    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    _cipher_suite = None

    @classmethod
    def _get_cipher_suite(cls):
        """Get cipher suite for encryption/decryption"""
        if cls._cipher_suite is None:
            encryption_key = os.getenv("ENCRYPTION_KEY")
            if not encryption_key:
                raise ValueError("ENCRYPTION_KEY environment variable not set")
            cls._cipher_suite = Fernet(encryption_key.encode())
        return cls._cipher_suite

    def _encrypt_value(self, value: str) -> bytes:
        """Encrypt a string value"""
        if not value:
            return None
        cipher = self._get_cipher_suite()
        return cipher.encrypt(value.encode())

    def _decrypt_value(self, encrypted_value: bytes) -> str:
        """Decrypt a binary value"""
        if not encrypted_value:
            return None
        cipher = self._get_cipher_suite()
        return cipher.decrypt(encrypted_value).decode()

    def set_credentials(self, api_key: str, api_secret: str, client_code: str = None,
                       pin: str = None, totp_key: str = None):
        """Set and encrypt credentials"""
        self.encrypted_api_key = self._encrypt_value(api_key)
        self.encrypted_api_secret = self._encrypt_value(api_secret)
        self.encrypted_client_code = self._encrypt_value(client_code) if client_code else None
        self.encrypted_pin = self._encrypt_value(pin) if pin else None
        self.encrypted_totp_key = self._encrypt_value(totp_key) if totp_key else None

    def get_api_key(self) -> str:
        """Get decrypted API key"""
        return self._decrypt_value(self.encrypted_api_key)

    def get_api_secret(self) -> str:
        """Get decrypted API secret"""
        return self._decrypt_value(self.encrypted_api_secret)

    def get_client_code(self) -> str:
        """Get decrypted client code"""
        return self._decrypt_value(self.encrypted_client_code)

    def get_pin(self) -> str:
        """Get decrypted PIN"""
        return self._decrypt_value(self.encrypted_pin)

    def get_totp_key(self) -> str:
        """Get decrypted TOTP key"""
        return self._decrypt_value(self.encrypted_totp_key)

    def to_dict(self):
        """Convert to dictionary (without sensitive data)"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "broker_type": self.broker_type,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
