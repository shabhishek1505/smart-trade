"""Authentication request/response schemas"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class RegisterRequest(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "trader123",
                "email": "trader@example.com",
                "password": "SecurePassword123",
                "full_name": "John Trader"
            }
        }


class LoginRequest(BaseModel):
    """User login request"""
    username: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "username": "trader123",
                "password": "SecurePassword123"
            }
        }


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class UserResponse(BaseModel):
    """User response"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "trader123",
                "email": "trader@example.com",
                "full_name": "John Trader",
                "is_active": True,
                "created_at": "2026-04-10T12:00:00Z",
                "last_login": "2026-04-10T15:30:00Z"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    old_password: str
    new_password: str = Field(..., min_length=8)
