"""Authentication routes"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from common.db.models.user import User
from common.db.models.user_settings import UserSettings
from api.schemas.auth import (
    RegisterRequest, LoginRequest, TokenResponse, UserResponse,
    RefreshTokenRequest, ChangePasswordRequest
)
from api.schemas.response import ApiResponse
from api.auth import (
    hash_password, verify_password, create_access_token,
    create_refresh_token, verify_token
)
from api.dependencies import get_current_user, get_db_session
from api.config import settings
from common.utils.logger import init_logger

logger = init_logger("auth-routes")
router = APIRouter()


@router.post("/register", status_code=201)
async def register(request: RegisterRequest, session = Depends(get_db_session)):
    """Register a new user"""
    try:
        # Check if user already exists
        existing_user = session.query(User).filter(
            (User.username == request.username) | (User.email == request.email)
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )

        # Create new user
        user = User(
            username=request.username,
            email=request.email,
            password_hash=hash_password(request.password),
            full_name=request.full_name or request.username
        )
        session.add(user)
        session.flush()  # Get the user ID

        # Create default user settings
        settings_obj = UserSettings(user_id=user.id)
        session.add(settings_obj)
        session.commit()

        logger.info(f"New user registered: {user.username}")

        # Generate tokens
        access_token = create_access_token(user.id, user.username)
        refresh_token = create_refresh_token(user.id, user.username)

        return ApiResponse(
            status="success",
            data=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            ),
            message="User registered successfully",
            timestamp=datetime.utcnow()
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login")
async def login(request: LoginRequest, session = Depends(get_db_session)):
    """Login user"""

    user = session.query(User).filter(User.username == request.username).first()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Update last login
    user.last_login = datetime.utcnow()
    session.commit()

    logger.info(f"User logged in: {user.username}")

    # Generate tokens
    access_token = create_access_token(user.id, user.username)
    refresh_token = create_refresh_token(user.id, user.username)

    return ApiResponse(
        status="success",
        data=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
        message="Login successful",
        timestamp=datetime.utcnow()
    )


@router.post("/refresh")
async def refresh(request: RefreshTokenRequest):
    """Refresh access token"""

    token_data = verify_token(request.refresh_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    access_token = create_access_token(token_data.user_id, token_data.username)

    return ApiResponse(
        status="success",
        data=TokenResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        ),
        message="Token refreshed successfully",
        timestamp=datetime.utcnow()
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user"""
    logger.info(f"User logged out: {current_user.username}")
    return {"status": "success", "message": "Logged out successfully"}


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session = Depends(get_db_session)
):
    """Change user password"""

    if not verify_password(request.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )

    current_user.password_hash = hash_password(request.new_password)
    session.commit()

    logger.info(f"Password changed for user: {current_user.username}")

    return {"status": "success", "message": "Password changed successfully"}
