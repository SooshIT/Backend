"""
Opportunities API Endpoints
Handles courses, jobs, mentorships, workshops
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import re

from app.core.database import get_db
from app.models.user import User
from app.models.opportunity import Opportunity, OpportunityType
from app.schemas.opportunity import (
    OpportunityCreateRequest,
    OpportunityUpdateRequest,
    OpportunityResponse,
    OpportunitySearchRequest,
)
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()


def create_slug(title: str) -> str:
    """Create URL-friendly slug from title"""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    slug = slug.strip('-')
    return slug


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    opportunity_data: OpportunityCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new opportunity

    Create a course, job, mentorship, or workshop opportunity.
    """
    # Create slug
    slug = create_slug(opportunity_data.title)

    # Check if slug exists
    result = await db.execute(select(Opportunity).where(Opportunity.slug == slug))
    if result.scalar_one_or_none():
        slug = f"{slug}-{datetime.utcnow().timestamp()}"

    # Create embedding text
    embedding_text = f"""
    {opportunity_data.title}
    {opportunity_data.description}
    Type: {opportunity_data.opportunity_type}
    Skills: {', '.join(opportunity_data.skills_gained)}
    """

    opportunity = Opportunity(
        creator_id=current_user.id,
        slug=slug,
        embedding_text=embedding_text,
        **opportunity_data.dict(),
    )

    db.add(opportunity)
    await db.commit()
    await db.refresh(opportunity)

    return OpportunityResponse.model_validate(opportunity)


@router.get("/", response_model=List[OpportunityResponse])
async def list_opportunities(
    opportunity_type: Optional[OpportunityType] = None,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """
    List opportunities

    Get a paginated list of active opportunities.
    """
    query = select(Opportunity).where(
        Opportunity.is_active == True,
        Opportunity.is_published == True,
        Opportunity.deleted_at.is_(None)
    )

    if opportunity_type:
        query = query.where(Opportunity.opportunity_type == opportunity_type)

    query = query.order_by(Opportunity.created_at.desc()).limit(limit).offset(offset)

    result = await db.execute(query)
    opportunities = result.scalars().all()

    return [OpportunityResponse.model_validate(opp) for opp in opportunities]


@router.post("/search", response_model=List[OpportunityResponse])
async def search_opportunities(
    search_data: OpportunitySearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Search opportunities

    Advanced search with filters for type, category, price, location, etc.
    """
    query = select(Opportunity).where(
        Opportunity.is_active == True,
        Opportunity.is_published == True,
        Opportunity.deleted_at.is_(None)
    )

    # Text search
    if search_data.query:
        search_term = f"%{search_data.query}%"
        query = query.where(
            or_(
                Opportunity.title.ilike(search_term),
                Opportunity.description.ilike(search_term)
            )
        )

    # Filters
    if search_data.opportunity_type:
        query = query.where(Opportunity.opportunity_type == search_data.opportunity_type)

    if search_data.category_id:
        query = query.where(Opportunity.category_id == search_data.category_id)

    if search_data.difficulty_level:
        query = query.where(Opportunity.difficulty_level == search_data.difficulty_level)

    if search_data.is_free is not None:
        query = query.where(Opportunity.is_free == search_data.is_free)

    if search_data.is_remote is not None:
        query = query.where(Opportunity.is_remote == search_data.is_remote)

    if search_data.min_price is not None:
        query = query.where(Opportunity.price >= search_data.min_price)

    if search_data.max_price is not None:
        query = query.where(Opportunity.price <= search_data.max_price)

    # Pagination
    query = query.order_by(Opportunity.created_at.desc()).limit(search_data.limit).offset(search_data.offset)

    result = await db.execute(query)
    opportunities = result.scalars().all()

    return [OpportunityResponse.model_validate(opp) for opp in opportunities]


@router.get("/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get opportunity by ID

    Returns detailed information about a specific opportunity.
    """
    result = await db.execute(
        select(Opportunity).where(Opportunity.id == opportunity_id)
    )
    opportunity = result.scalar_one_or_none()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found",
        )

    # Increment views count
    opportunity.views_count += 1
    await db.commit()

    return OpportunityResponse.model_validate(opportunity)


@router.put("/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: UUID,
    update_data: OpportunityUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update opportunity

    Update an existing opportunity. Only creator can update.
    """
    result = await db.execute(
        select(Opportunity).where(Opportunity.id == opportunity_id)
    )
    opportunity = result.scalar_one_or_none()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found",
        )

    # Check if user is creator
    if opportunity.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only creator can update this opportunity",
        )

    # Update fields
    update_fields = update_data.dict(exclude_unset=True)
    for field, value in update_fields.items():
        if hasattr(opportunity, field):
            setattr(opportunity, field, value)

    opportunity.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(opportunity)

    return OpportunityResponse.model_validate(opportunity)


@router.delete("/{opportunity_id}")
async def delete_opportunity(
    opportunity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete opportunity

    Soft delete an opportunity. Only creator can delete.
    """
    result = await db.execute(
        select(Opportunity).where(Opportunity.id == opportunity_id)
    )
    opportunity = result.scalar_one_or_none()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found",
        )

    # Check if user is creator
    if opportunity.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only creator can delete this opportunity",
        )

    # Soft delete
    opportunity.deleted_at = datetime.utcnow()
    opportunity.is_active = False
    await db.commit()

    return {"message": "Opportunity deleted successfully"}


@router.get("/my/opportunities", response_model=List[OpportunityResponse])
async def get_my_opportunities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get current user's opportunities

    Returns all opportunities created by the current user.
    """
    result = await db.execute(
        select(Opportunity)
        .where(Opportunity.creator_id == current_user.id)
        .where(Opportunity.deleted_at.is_(None))
        .order_by(Opportunity.created_at.desc())
    )
    opportunities = result.scalars().all()

    return [OpportunityResponse.model_validate(opp) for opp in opportunities]


@router.post("/{opportunity_id}/enroll")
async def enroll_in_opportunity(
    opportunity_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Enroll in opportunity

    Enroll current user in a course, workshop, or mentorship.
    """
    result = await db.execute(
        select(Opportunity).where(Opportunity.id == opportunity_id)
    )
    opportunity = result.scalar_one_or_none()

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found",
        )

    # TODO: Create enrollment record in database
    # For now, just increment enrollment count
    opportunity.enrollments_count += 1
    await db.commit()

    return {
        "message": "Enrolled successfully",
        "opportunity_id": opportunity_id,
        "opportunity_title": opportunity.title,
    }
