"""
Authentication API Endpoints
Handles signup, login, token refresh, password reset
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta
from jose import JWTError

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.config import settings
from app.models.user import User, UserStatus
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    PasswordResetRequest,
    ChangePasswordRequest,
)

router = APIRouter()
security = HTTPBearer()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    """
    token = credentials.credentials

    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if user.status == UserStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account suspended",
        )

    return user


def create_tokens(user_id: str) -> dict:
    """Create access and refresh tokens for a user"""
    access_token = create_access_token(data={"sub": str(user_id)})
    refresh_token = create_refresh_token(data={"sub": str(user_id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_data: SignupRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create new user account

    Creates a new user with email and password authentication.
    Returns access and refresh tokens upon successful registration.
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == signup_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Check if phone already exists (if provided)
    if signup_data.phone:
        result = await db.execute(select(User).where(User.phone == signup_data.phone))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered",
            )

    # Create new user
    user = User(
        email=signup_data.email,
        password_hash=get_password_hash(signup_data.password),
        first_name=signup_data.first_name,
        last_name=signup_data.last_name,
        display_name=f"{signup_data.first_name} {signup_data.last_name}",
        age=signup_data.age,
        age_group=signup_data.age_group,
        user_type=signup_data.user_type,
        phone=signup_data.phone,
        status=UserStatus.PENDING_VERIFICATION,
        last_login_at=datetime.utcnow(),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Create tokens
    tokens = create_tokens(user.id)

    return TokenResponse(
        **tokens,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Login with email and password

    Authenticates user and returns access and refresh tokens.
    """
    # Get user by email
    result = await db.execute(select(User).where(User.email == login_data.email))
    user = result.scalar_one_or_none()

    # Verify user exists and password is correct
    if not user or not user.password_hash or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # Check if account is suspended
    if user.status == UserStatus.SUSPENDED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account suspended",
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    await db.commit()
    await db.refresh(user)

    # Create tokens
    tokens = create_tokens(user.id)

    return TokenResponse(
        **tokens,
        user=UserResponse.model_validate(user),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token

    Uses refresh token to generate a new access token.
    """
    try:
        payload = decode_token(refresh_data.refresh_token)
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate refresh token",
        )

    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Create new tokens
    tokens = create_tokens(user.id)

    return TokenResponse(
        **tokens,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user information

    Returns profile information for the authenticated user.
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
):
    """
    Logout current user

    Note: JWT tokens cannot be invalidated server-side.
    Client should discard the tokens.
    """
    return {"message": "Logged out successfully"}


@router.post("/password-reset")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset

    Sends password reset email to user.
    Always returns success even if email doesn't exist (security best practice).
    """
    # TODO: Implement email sending
    # For now, just return success
    return {"message": "If email exists, password reset link has been sent"}


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change password for authenticated user

    Requires old password for verification.
    """
    # Verify old password
    if not current_user.password_hash or not verify_password(
        password_data.old_password, current_user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password",
        )

    # Update password
    current_user.password_hash = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()

    await db.commit()

    return {"message": "Password changed successfully"}
