"""
User database model
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum as SQLEnum, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class UserType(str, enum.Enum):
    """User type enumeration"""
    BEGINNER = "beginner"
    MID_LEVEL = "mid_level"
    EXPERIENCED = "experienced"
    STAY_AT_HOME = "stay_at_home"
    DISABLED = "disabled"


class UserStatus(str, enum.Enum):
    """User status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class AgeGroup(str, enum.Enum):
    """Age group enumeration"""
    KIDS = "kids"              # 5-12
    TEENS = "teens"            # 13-17
    YOUNG_ADULT = "young_adult"  # 18-24
    ADULT = "adult"            # 25-44
    MIDDLE_AGE = "middle_age"  # 45-60
    SENIOR = "senior"          # 60+


class User(Base):
    """User database model"""

    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users

    # Profile
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    display_name = Column(String(200))
    bio = Column(Text)
    avatar_url = Column(String(500))
    age = Column(Integer)
    age_group = Column(SQLEnum(AgeGroup, name="age_group_enum"), nullable=False)

    # User classification
    user_type = Column(SQLEnum(UserType, name="user_type_enum"), nullable=False, default=UserType.BEGINNER)
    status = Column(SQLEnum(UserStatus, name="user_status_enum"), nullable=False, default=UserStatus.PENDING_VERIFICATION)

    # Location
    country = Column(String(100))
    city = Column(String(100))
    timezone = Column(String(50))

    # OAuth
    google_id = Column(String(255), unique=True, nullable=True, index=True)
    apple_id = Column(String(255), unique=True, nullable=True, index=True)
    linkedin_id = Column(String(255), unique=True, nullable=True, index=True)

    # Verification
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)

    # Settings
    is_mentor = Column(Boolean, default=False)
    preferences = Column(Text)  # JSON string
    notification_settings = Column(Text)  # JSON string

    # Gamification
    total_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login_at = Column(DateTime(timezone=True))
    deleted_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<User {self.email} ({self.user_type})>"
