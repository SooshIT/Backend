"""
Mentors API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.models.mentor import MentorProfile
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.post("/profile", status_code=status.HTTP_201_CREATED)
async def create_mentor_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create mentor profile"""
    if not current_user.is_mentor:
        raise HTTPException(status_code=400, detail="User is not a mentor")
    
    profile = MentorProfile(user_id=current_user.id, hourly_rate=50.0)
    db.add(profile)
    await db.commit()
    return {"message": "Mentor profile created"}

@router.get("/profile")
async def get_my_mentor_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's mentor profile"""
    result = await db.execute(select(MentorProfile).where(MentorProfile.user_id == current_user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Mentor profile not found")
    return {"id": str(profile.id), "user_id": str(profile.user_id), "hourly_rate": profile.hourly_rate}

@router.get("/search")
async def search_mentors(
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Search mentors"""
    result = await db.execute(select(MentorProfile).limit(limit).offset(offset))
    mentors = result.scalars().all()
    return [{"id": str(m.id), "user_id": str(m.user_id)} for m in mentors]

@router.get("/{mentor_id}")
async def get_mentor_profile(
    mentor_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get mentor profile by ID"""
    result = await db.execute(select(MentorProfile).where(MentorProfile.id == mentor_id))
    mentor = result.scalar_one_or_none()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found")
    return {"id": str(mentor.id), "hourly_rate": mentor.hourly_rate}
