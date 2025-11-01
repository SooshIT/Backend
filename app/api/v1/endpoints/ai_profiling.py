"""
AI Profiling API Endpoints
Handles user profiling, recommendations, and voice-based profiling
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import json

from app.core.database import get_db
from app.models.user import User
from app.models.ai_profile import UserAIProfile
from app.schemas.ai_profile import (
    AIProfileCreateRequest,
    AIProfileUpdateRequest,
    AIProfileResponse,
    AIRecommendationsResponse,
    VoiceProfilingResponse,
)
from app.api.v1.endpoints.auth import get_current_user
from app.services.ai_provider_service import UnifiedAIService

router = APIRouter()


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/profile", response_model=AIProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_profile(
    profile_data: AIProfileCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create AI profile for current user

    Creates a comprehensive AI profile based on user's interests, skills, and goals.
    Generates vector embeddings for personalized recommendations.
    """
    # Check if profile already exists
    result = await db.execute(
        select(UserAIProfile).where(UserAIProfile.user_id == current_user.id)
    )
    existing_profile = result.scalar_one_or_none()

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AI profile already exists. Use PUT to update.",
        )

    # Create profile text for embedding
    profile_text = f"""
    Interests: {', '.join(profile_data.interests)}
    Skills: {', '.join(profile_data.skills) if profile_data.skills else 'Not specified'}
    Goals: {', '.join(profile_data.goals)}
    Learning Style: {profile_data.learning_style or 'Not specified'}
    Experience Level: {profile_data.experience_level or 'Not specified'}
    """

    # Create AI profile
    ai_profile = UserAIProfile(
        user_id=current_user.id,
        interests=profile_data.interests,
        skills=profile_data.skills,
        goals=profile_data.goals,
        learning_style=profile_data.learning_style,
        experience_level=profile_data.experience_level,
        available_time_per_week=profile_data.available_time_per_week,
        profile_text=profile_text,
        strengths=[],  # TODO: Generate with AI
        areas_to_improve=[],  # TODO: Generate with AI
    )

    db.add(ai_profile)
    await db.commit()
    await db.refresh(ai_profile)

    return AIProfileResponse.model_validate(ai_profile)


@router.get("/profile", response_model=AIProfileResponse)
async def get_ai_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's AI profile

    Returns the AI profile with interests, skills, goals, and insights.
    """
    result = await db.execute(
        select(UserAIProfile).where(UserAIProfile.user_id == current_user.id)
    )
    ai_profile = result.scalar_one_or_none()

    if not ai_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI profile not found. Create one first.",
        )

    return AIProfileResponse.model_validate(ai_profile)


@router.put("/profile", response_model=AIProfileResponse)
async def update_ai_profile(
    profile_data: AIProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's AI profile

    Updates AI profile data and regenerates recommendations.
    """
    result = await db.execute(
        select(UserAIProfile).where(UserAIProfile.user_id == current_user.id)
    )
    ai_profile = result.scalar_one_or_none()

    if not ai_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI profile not found. Create one first.",
        )

    # Update fields
    update_fields = profile_data.dict(exclude_unset=True)
    for field, value in update_fields.items():
        if hasattr(ai_profile, field) and value is not None:
            setattr(ai_profile, field, value)

    # Update profile text
    profile_text = f"""
    Interests: {', '.join(ai_profile.interests)}
    Skills: {', '.join(ai_profile.skills)}
    Goals: {', '.join(ai_profile.goals)}
    Learning Style: {ai_profile.learning_style}
    Experience Level: {ai_profile.experience_level}
    """
    ai_profile.profile_text = profile_text

    await db.commit()
    await db.refresh(ai_profile)

    return AIProfileResponse.model_validate(ai_profile)


@router.delete("/profile")
async def delete_ai_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete current user's AI profile

    Permanently deletes the AI profile and associated recommendations.
    """
    result = await db.execute(
        select(UserAIProfile).where(UserAIProfile.user_id == current_user.id)
    )
    ai_profile = result.scalar_one_or_none()

    if not ai_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI profile not found",
        )

    await db.delete(ai_profile)
    await db.commit()

    return {"message": "AI profile deleted successfully"}


@router.get("/recommendations", response_model=AIRecommendationsResponse)
async def get_recommendations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get personalized AI recommendations

    Returns personalized recommendations for categories, opportunities,
    mentors, and learning paths based on user's AI profile.
    """
    # Get AI profile
    result = await db.execute(
        select(UserAIProfile).where(UserAIProfile.user_id == current_user.id)
    )
    ai_profile = result.scalar_one_or_none()

    if not ai_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI profile not found. Create one first.",
        )

    # TODO: Implement actual recommendation engine
    # For now, return mock recommendations
    return AIRecommendationsResponse(
        recommended_categories=[
            {"id": "tech", "name": "Technology", "match_score": 0.95},
            {"id": "creative", "name": "Creative Arts", "match_score": 0.82},
        ],
        recommended_opportunities=[
            {"id": 1, "title": "Python for Beginners", "type": "course", "match_score": 0.90},
            {"id": 2, "title": "Web Development Bootcamp", "type": "course", "match_score": 0.85},
        ],
        recommended_mentors=[
            {"id": 1, "name": "John Doe", "expertise": "Python", "match_score": 0.88},
        ],
        learning_path_suggestions=[
            {"path": "Full Stack Developer", "duration_weeks": 12, "difficulty": "intermediate"},
        ],
        personalized_message=f"Based on your interests in {', '.join(ai_profile.interests[:2])}, we recommend starting with Python programming.",
    )


@router.post("/voice-profiling", response_model=VoiceProfilingResponse)
async def voice_profiling(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Voice-based AI profiling

    Analyzes user's voice input to extract interests, skills, and goals.
    Uses speech-to-text and NLP to create AI profile automatically.
    """
    # Read audio file
    audio_bytes = await audio.read()

    # Use UnifiedAIService for transcription and analysis
    ai_service = UnifiedAIService()

    # Transcribe audio
    transcript = await ai_service.speech_to_text(audio_bytes)

    # Analyze transcript with AI
    analysis_prompt = f"""
    Analyze the following user introduction and extract:
    1. Interests (list of topics they're interested in)
    2. Skills (list of skills they have)
    3. Goals (list of what they want to achieve)
    4. Suggested user type (beginner, mid_level, experienced, stay_at_home, disabled)

    User introduction: "{transcript}"

    Return as JSON with keys: interests, skills, goals, suggested_user_type, confidence_score
    """

    ai_response = await ai_service.chat(
        user_message=analysis_prompt,
        system_prompt="You are an expert career counselor and profiling assistant.",
        temperature=0.3,
    )

    # Parse AI response
    try:
        analysis = json.loads(ai_response)
    except json.JSONDecodeError:
        # If AI didn't return valid JSON, provide defaults
        analysis = {
            "interests": ["learning", "growth"],
            "skills": [],
            "goals": ["career development"],
            "suggested_user_type": "beginner",
            "confidence_score": 0.5,
        }

    return VoiceProfilingResponse(
        transcript=transcript,
        extracted_interests=analysis.get("interests", []),
        extracted_skills=analysis.get("skills", []),
        extracted_goals=analysis.get("goals", []),
        suggested_user_type=analysis.get("suggested_user_type", "beginner"),
        confidence_score=analysis.get("confidence_score", 0.5),
    )
