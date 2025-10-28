"""
Mentor Profile database model
"""

from sqlalchemy import Column, String, Integer, Text, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class MentorTier(str, enum.Enum):
    """Mentor tier enumeration"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"


class MentorProfile(Base):
    """Mentor profile model"""

    __tablename__ = "mentor_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Professional info
    title = Column(String(255))  # e.g., "Senior Software Engineer"
    company = Column(String(255))
    years_of_experience = Column(Integer)
    expertise_areas = Column(ARRAY(String), default=[])
    certifications = Column(ARRAY(String), default=[])

    # Mentorship details
    hourly_rate = Column(Float)
    session_duration_minutes = Column(Integer, default=60)
    max_students = Column(Integer, default=10)
    current_students = Column(Integer, default=0)
    mentor_tier = Column(String(20), default="bronze")

    # Availability
    available_slots = Column(Text)  # JSON string
    timezone = Column(String(50))
    is_accepting_students = Column(Boolean, default=True)

    # Stats
    total_sessions = Column(Integer, default=0)
    avg_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    response_time_hours = Column(Float)

    # Verification
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True))

    # Social links
    linkedin_url = Column(String(500))
    github_url = Column(String(500))
    portfolio_url = Column(String(500))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<MentorProfile user_id={self.user_id}>"
