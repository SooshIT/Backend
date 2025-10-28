"""
User schemas
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.user import UserType, UserStatus, AgeGroup


class UserUpdateRequest(BaseModel):
    """Update user profile request"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    display_name: Optional[str] = Field(None, min_length=1, max_length=200)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    preferences: Optional[dict] = None
    notification_settings: Optional[dict] = None


class UserPublicResponse(BaseModel):
    """Public user profile response (limited info)"""
    id: UUID
    display_name: Optional[str]
    avatar_url: Optional[str]
    age_group: AgeGroup
    user_type: UserType
    is_mentor: bool
    bio: Optional[str]
    total_points: int
    level: int
    created_at: datetime

    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    """User statistics response"""
    total_points: int
    level: int
    streak_days: int
    total_bookings: int = 0
    total_sessions_completed: int = 0
    total_learning_hours: float = 0
    achievements_count: int = 0
    mentor_rating: Optional[float] = None


class UserSearchQuery(BaseModel):
    """User search query parameters"""
    query: Optional[str] = None
    user_type: Optional[UserType] = None
    age_group: Optional[AgeGroup] = None
    is_mentor: Optional[bool] = None
    country: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
