"""
Authentication schemas
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.user import UserType, UserStatus, AgeGroup


class SignupRequest(BaseModel):
    """Signup request schema"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=5, le=120)
    age_group: AgeGroup
    user_type: UserType = UserType.BEGINNER
    phone: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: "UserResponse"


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""
    refresh_token: str


class UserResponse(BaseModel):
    """User response schema"""
    id: UUID
    email: str
    first_name: str
    last_name: str
    display_name: Optional[str]
    avatar_url: Optional[str]
    age: Optional[int]
    age_group: AgeGroup
    user_type: UserType
    status: UserStatus
    is_mentor: bool
    email_verified: bool
    phone_verified: bool
    total_points: int
    level: int
    streak_days: int
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class PasswordResetRequest(BaseModel):
    """Password reset request schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


class ChangePasswordRequest(BaseModel):
    """Change password request schema"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
