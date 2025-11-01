"""
Opportunity database model (courses, jobs, mentorships, workshops)
"""

from sqlalchemy import Column, String, Integer, Text, Boolean, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class OpportunityType(str, enum.Enum):
    """Opportunity type enumeration"""
    COURSE = "course"
    JOB = "job"
    MENTORSHIP = "mentorship"
    WORKSHOP = "workshop"


class DifficultyLevel(str, enum.Enum):
    """Difficulty level enumeration"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Opportunity(Base):
    """Opportunity model for courses, jobs, mentorships, workshops"""

    __tablename__ = "opportunities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), index=True)
    subcategory_id = Column(UUID(as_uuid=True), ForeignKey("subcategories.id", ondelete="SET NULL"), index=True)

    # Basic info
    title = Column(String(255), nullable=False, index=True)
    slug = Column(String(255), unique=True, index=True)
    description = Column(Text, nullable=False)
    opportunity_type = Column(SQLEnum(OpportunityType, name="opportunity_type_enum"), nullable=False, index=True)

    # Details
    difficulty_level = Column(SQLEnum(DifficultyLevel, name="difficulty_level_enum"))
    duration_hours = Column(Integer)  # Total hours
    duration_weeks = Column(Integer)  # Total weeks
    language = Column(String(50), default="English")

    # Media
    thumbnail_url = Column(String(500))
    video_url = Column(String(500))
    images = Column(ARRAY(String), default=[])

    # Pricing
    price = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    is_free = Column(Boolean, default=False)

    # Requirements
    prerequisites = Column(ARRAY(String), default=[])
    skills_required = Column(ARRAY(String), default=[])
    skills_gained = Column(ARRAY(String), default=[])

    # Location (for jobs/workshops)
    location = Column(String(255))
    is_remote = Column(Boolean, default=False)
    is_onsite = Column(Boolean, default=False)

    # Dates
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    application_deadline = Column(DateTime(timezone=True))

    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    is_published = Column(Boolean, default=True)

    # Stats
    views_count = Column(Integer, default=0)
    enrollments_count = Column(Integer, default=0)
    avg_rating = Column(Float, default=0.0)
    reviews_count = Column(Integer, default=0)

    # Vector embedding for recommendations
    # embedding = Column(Vector(1536))
    embedding_text = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True))

    def __repr__(self):
        return f"<Opportunity {self.title} ({self.opportunity_type})>"
