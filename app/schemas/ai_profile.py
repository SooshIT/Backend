"""
AI Profile schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class AIProfileCreateRequest(BaseModel):
    """Create AI profile request"""
    interests: List[str] = Field(..., min_items=1, max_items=20)
    skills: List[str] = Field(default=[], max_items=30)
    goals: List[str] = Field(..., min_items=1, max_items=10)
    learning_style: Optional[str] = Field(None, pattern="^(visual|auditory|kinesthetic|reading)$")
    experience_level: Optional[str] = None
    available_time_per_week: Optional[int] = Field(None, ge=1, le=168)


class AIProfileUpdateRequest(BaseModel):
    """Update AI profile request"""
    interests: Optional[List[str]] = Field(None, max_items=20)
    skills: Optional[List[str]] = Field(None, max_items=30)
    goals: Optional[List[str]] = Field(None, max_items=10)
    learning_style: Optional[str] = Field(None, pattern="^(visual|auditory|kinesthetic|reading)$")
    experience_level: Optional[str] = None
    available_time_per_week: Optional[int] = Field(None, ge=1, le=168)


class AIProfileResponse(BaseModel):
    """AI profile response"""
    id: UUID
    user_id: UUID
    interests: List[str]
    skills: List[str]
    goals: List[str]
    learning_style: Optional[str]
    experience_level: Optional[str]
    available_time_per_week: Optional[int]
    strengths: List[str]
    areas_to_improve: List[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AIRecommendationsResponse(BaseModel):
    """AI recommendations response"""
    recommended_categories: List[dict]
    recommended_opportunities: List[dict]
    recommended_mentors: List[dict]
    learning_path_suggestions: List[dict]
    personalized_message: str


class VoiceProfilingRequest(BaseModel):
    """Voice-based profiling request"""
    # Audio will be handled as UploadFile in the endpoint
    pass


class VoiceProfilingResponse(BaseModel):
    """Voice profiling response"""
    transcript: str
    extracted_interests: List[str]
    extracted_skills: List[str]
    extracted_goals: List[str]
    suggested_user_type: str
    confidence_score: float
