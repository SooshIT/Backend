"""
User Management API Endpoints
Handles user profile operations
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.user import User, UserType, AgeGroup
from app.schemas.auth import UserResponse
from app.schemas.user import (
    UserUpdateRequest,
    UserPublicResponse,
    UserStatsResponse,
    UserSearchQuery,
)
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/me", response_model=UserResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    """
    Get current user's full profile

    Returns complete profile information for the authenticated user.
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user's profile

    Update profile information for the authenticated user.
    """
    # Update fields if provided
    update_fields = update_data.dict(exclude_unset=True)

    for field, value in update_fields.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.delete("/me")
async def delete_my_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete current user's account

    Soft deletes the account by setting deleted_at timestamp.
    """
    from datetime import datetime

    current_user.deleted_at = datetime.utcnow()
    current_user.status = "inactive"

    await db.commit()

    return {"message": "Account deleted successfully"}


@router.get("/{user_id}", response_model=UserPublicResponse)
async def get_user_profile(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get public user profile by ID

    Returns limited public information about a user.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserPublicResponse.model_validate(user)


@router.get("/{user_id}/stats", response_model=UserStatsResponse)
async def get_user_stats(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get user statistics

    Returns gamification stats, learning progress, and activity metrics.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # TODO: Get actual stats from related tables
    # For now, return basic user stats
    return UserStatsResponse(
        total_points=user.total_points,
        level=user.level,
        streak_days=user.streak_days,
        total_bookings=0,  # TODO: Count from bookings table
        total_sessions_completed=0,  # TODO: Count from bookings table
        total_learning_hours=0.0,  # TODO: Calculate from learning_paths
        achievements_count=0,  # TODO: Count from user_achievements
    )


@router.post("/search", response_model=List[UserPublicResponse])
async def search_users(
    search_query: UserSearchQuery,
    db: AsyncSession = Depends(get_db),
):
    """
    Search users

    Search for users by various criteria.
    """
    query = select(User).where(User.deleted_at.is_(None))

    # Apply filters
    if search_query.query:
        search_term = f"%{search_query.query}%"
        query = query.where(
            (User.display_name.ilike(search_term)) |
            (User.first_name.ilike(search_term)) |
            (User.last_name.ilike(search_term))
        )

    if search_query.user_type:
        query = query.where(User.user_type == search_query.user_type)

    if search_query.age_group:
        query = query.where(User.age_group == search_query.age_group)

    if search_query.is_mentor is not None:
        query = query.where(User.is_mentor == search_query.is_mentor)

    if search_query.country:
        query = query.where(User.country == search_query.country)

    # Apply pagination
    query = query.limit(search_query.limit).offset(search_query.offset)

    result = await db.execute(query)
    users = result.scalars().all()

    return [UserPublicResponse.model_validate(user) for user in users]


@router.post("/me/become-mentor")
async def become_mentor(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Enable mentor features for current user

    Allows user to start offering mentorship services.
    Requires user to be at least 'mid_level' type.
    """
    if current_user.user_type == UserType.BEGINNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Beginners cannot become mentors. Please gain more experience first.",
        )

    if current_user.is_mentor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already a mentor",
        )

    current_user.is_mentor = True
    await db.commit()
    await db.refresh(current_user)

    return {
        "message": "You are now a mentor!",
        "user": UserResponse.model_validate(current_user)
    }
