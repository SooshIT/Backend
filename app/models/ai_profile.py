"""
AI Profile database model
"""

from sqlalchemy import Column, String, Integer, Text, Float, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class UserAIProfile(Base):
    """User AI profile with vector embeddings"""

    __tablename__ = "user_ai_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)

    # Profiling data
    interests = Column(ARRAY(String), default=[])
    skills = Column(ARRAY(String), default=[])
    goals = Column(ARRAY(String), default=[])
    learning_style = Column(String(50))  # visual, auditory, kinesthetic, reading
    experience_level = Column(String(50))
    available_time_per_week = Column(Integer)  # hours

    # AI-generated insights
    personality_traits = Column(Text)  # JSON string
    recommended_paths = Column(Text)  # JSON string
    strengths = Column(ARRAY(String), default=[])
    areas_to_improve = Column(ARRAY(String), default=[])

    # Vector embedding (1536 dimensions for OpenAI embeddings)
    # profile_embedding = Column(Vector(1536))  # Requires pgvector
    profile_text = Column(Text)  # Combined text for embedding generation

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<UserAIProfile user_id={self.user_id}>"
