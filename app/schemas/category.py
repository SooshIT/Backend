"""
Category schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


class SubcategoryResponse(BaseModel):
    """Subcategory response"""
    id: UUID
    category_id: UUID
    name: str
    slug: str
    description: Optional[str]
    icon_url: Optional[str]
    display_order: int
    is_active: bool

    class Config:
        from_attributes = True


class CategoryResponse(BaseModel):
    """Category response"""
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    icon_url: Optional[str]
    color: Optional[str]
    display_order: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryWithSubcategoriesResponse(BaseModel):
    """Category with subcategories"""
    id: UUID
    name: str
    slug: str
    description: Optional[str]
    icon_url: Optional[str]
    color: Optional[str]
    display_order: int
    subcategories: List[SubcategoryResponse] = []

    class Config:
        from_attributes = True
