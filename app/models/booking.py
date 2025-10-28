"""
Booking database model
"""

from sqlalchemy import Column, String, Integer, Text, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class SessionStatus(str, enum.Enum):
    """Session status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class Booking(Base):
    """Booking/session model"""

    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    mentor_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(UUID(as_uuid=True), ForeignKey("opportunities.id", ondelete="SET NULL"), index=True)

    # Session details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    session_date = Column(DateTime(timezone=True), nullable=False, index=True)
    duration_minutes = Column(Integer, default=60)
    timezone = Column(String(50))

    # Meeting info
    meeting_url = Column(String(500))
    meeting_id = Column(String(255))
    meeting_password = Column(String(100))

    # Status
    status = Column(SQLEnum(SessionStatus, name="session_status_enum"), default=SessionStatus.PENDING, index=True)
    cancellation_reason = Column(Text)
    cancelled_by = Column(UUID(as_uuid=True))
    cancelled_at = Column(DateTime(timezone=True))

    # Payment
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="SET NULL"))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Booking {self.id} ({self.status})>"
