from sqlalchemy import Column, Integer, String, Boolean, DateTime, Index
from datetime import datetime
from common.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(120), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)

    # Profile
    full_name = Column(String(120), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Index for lookups
    __table_args__ = (
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
    )

    def to_dict(self, include_password=False):
        """Convert to dictionary"""
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }
        if include_password:
            data["password_hash"] = self.password_hash
        return data
