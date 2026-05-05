"""FastAPI dependencies"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from common.db.session import get_session
from common.db.models.user import User
from api.auth import verify_token
from common.utils.logger import init_logger

logger = init_logger("dependencies")

security = HTTPBearer()


def get_db_session():
    """Get database session - synchronous to work with FastAPI"""
    session = get_session()
    try:
        yield session
    finally:
        session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session = Depends(get_db_session)
) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials

    token_data = verify_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = session.query(User).filter(
        User.id == token_data.user_id,
        User.is_active == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current user if they are admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user
