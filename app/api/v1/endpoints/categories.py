"""
Categories API Endpoints
Handles categories and subcategories
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.category import Category, Subcategory
from app.schemas.category import (
    CategoryResponse,
    CategoryWithSubcategoriesResponse,
    SubcategoryResponse,
)

router = APIRouter()


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/", response_model=List[CategoryResponse])
async def list_categories(
    db: AsyncSession = Depends(get_db),
):
    """
    List all categories

    Returns all active categories ordered by display_order.
    """
    result = await db.execute(
        select(Category)
        .where(Category.is_active == True)
        .order_by(Category.display_order, Category.name)
    )
    categories = result.scalars().all()

    return [CategoryResponse.model_validate(cat) for cat in categories]


@router.get("/with-subcategories", response_model=List[CategoryWithSubcategoriesResponse])
async def list_categories_with_subcategories(
    db: AsyncSession = Depends(get_db),
):
    """
    List all categories with their subcategories

    Returns categories with nested subcategories.
    """
    # Get all categories
    cat_result = await db.execute(
        select(Category)
        .where(Category.is_active == True)
        .order_by(Category.display_order, Category.name)
    )
    categories = cat_result.scalars().all()

    # Get all subcategories
    subcat_result = await db.execute(
        select(Subcategory)
        .where(Subcategory.is_active == True)
        .order_by(Subcategory.display_order, Subcategory.name)
    )
    all_subcategories = subcat_result.scalars().all()

    # Group subcategories by category
    subcategories_by_category = {}
    for subcat in all_subcategories:
        if subcat.category_id not in subcategories_by_category:
            subcategories_by_category[subcat.category_id] = []
        subcategories_by_category[subcat.category_id].append(subcat)

    # Build response
    response = []
    for cat in categories:
        subcats = subcategories_by_category.get(cat.id, [])
        response.append({
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "description": cat.description,
            "icon_url": cat.icon_url,
            "color": cat.color,
            "display_order": cat.display_order,
            "subcategories": [SubcategoryResponse.model_validate(s) for s in subcats],
        })

    return response


@router.get("/{category_id}", response_model=CategoryWithSubcategoriesResponse)
async def get_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get category by ID with subcategories

    Returns a single category with its subcategories.
    """
    # Get category
    cat_result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    category = cat_result.scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    # Get subcategories
    subcat_result = await db.execute(
        select(Subcategory)
        .where(Subcategory.category_id == category_id)
        .where(Subcategory.is_active == True)
        .order_by(Subcategory.display_order, Subcategory.name)
    )
    subcategories = subcat_result.scalars().all()

    return {
        "id": category.id,
        "name": category.name,
        "slug": category.slug,
        "description": category.description,
        "icon_url": category.icon_url,
        "color": category.color,
        "display_order": category.display_order,
        "subcategories": [SubcategoryResponse.model_validate(s) for s in subcategories],
    }


@router.get("/{category_id}/subcategories", response_model=List[SubcategoryResponse])
async def list_subcategories(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    List subcategories for a category

    Returns all active subcategories for the specified category.
    """
    # Verify category exists
    cat_result = await db.execute(
        select(Category).where(Category.id == category_id)
    )
    if not cat_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    # Get subcategories
    subcat_result = await db.execute(
        select(Subcategory)
        .where(Subcategory.category_id == category_id)
        .where(Subcategory.is_active == True)
        .order_by(Subcategory.display_order, Subcategory.name)
    )
    subcategories = subcat_result.scalars().all()

    return [SubcategoryResponse.model_validate(s) for s in subcategories]
