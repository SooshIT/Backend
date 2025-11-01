"""
Opportunity schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from app.models.opportunity import OpportunityType, DifficultyLevel


class OpportunityCreateRequest(BaseModel):
    """Create opportunity request"""
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    opportunity_type: OpportunityType
    category_id: UUID
    subcategory_id: Optional[UUID] = None
    difficulty_level: Optional[DifficultyLevel] = None
    duration_hours: Optional[int] = Field(None, ge=1)
    duration_weeks: Optional[int] = Field(None, ge=1)
    language: str = "English"
    thumbnail_url: Optional[str] = None
    price: float = Field(default=0.0, ge=0)
    is_free: bool = False
    prerequisites: List[str] = []
    skills_required: List[str] = []
    skills_gained: List[str] = []
    location: Optional[str] = None
    is_remote: bool = False
    is_onsite: bool = False
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class OpportunityUpdateRequest(BaseModel):
    """Update opportunity request"""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    difficulty_level: Optional[DifficultyLevel] = None
    duration_hours: Optional[int] = Field(None, ge=1)
    duration_weeks: Optional[int] = Field(None, ge=1)
    thumbnail_url: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    is_free: Optional[bool] = None
    prerequisites: Optional[List[str]] = None
    skills_required: Optional[List[str]] = None
    skills_gained: Optional[List[str]] = None
    is_remote: Optional[bool] = None
    is_onsite: Optional[bool] = None


class OpportunityResponse(BaseModel):
    """Opportunity response"""
    id: UUID
    creator_id: UUID
    category_id: Optional[UUID]
    subcategory_id: Optional[UUID]
    title: str
    slug: str
    description: str
    opportunity_type: OpportunityType
    difficulty_level: Optional[DifficultyLevel]
    duration_hours: Optional[int]
    duration_weeks: Optional[int]
    language: str
    thumbnail_url: Optional[str]
    price: float
    currency: str
    is_free: bool
    prerequisites: List[str]
    skills_required: List[str]
    skills_gained: List[str]
    location: Optional[str]
    is_remote: bool
    is_onsite: bool
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    is_active: bool
    is_featured: bool
    views_count: int
    enrollments_count: int
    avg_rating: float
    reviews_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class OpportunitySearchRequest(BaseModel):
    """Search opportunities request"""
    query: Optional[str] = None
    opportunity_type: Optional[OpportunityType] = None
    category_id: Optional[UUID] = None
    difficulty_level: Optional[DifficultyLevel] = None
    is_free: Optional[bool] = None
    is_remote: Optional[bool] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
