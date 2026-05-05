"""Authentication utilities - JWT tokens and password hashing"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from api.config import settings
from common.utils.logger import init_logger

logger = init_logger("auth")

# Password hashing context - using argon2 instead of bcrypt for better compatibility
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class TokenData(BaseModel):
    """Token payload data"""
    user_id: int
    username: str


def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, username: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = {
        "user_id": user_id,
        "username": username,
    }

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(user_id: int, username: str) -> str:
    """Create JWT refresh token"""
    expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return create_access_token(user_id, username, expires_delta)


def verify_token(token: str) -> Optional[TokenData]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("user_id")
        username: str = payload.get("username")

        if user_id is None or username is None:
            return None

        return TokenData(user_id=user_id, username=username)

    except JWTError as e:
        logger.debug(f"JWT verification failed: {str(e)}")
        return None
