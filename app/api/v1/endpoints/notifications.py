"""
Notifications API Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_notifications(
    current_user: User = Depends(get_current_user),
):
    """Get user notifications"""
    return []

@router.post("/mark-read")
async def mark_notifications_read(
    current_user: User = Depends(get_current_user),
):
    """Mark notifications as read"""
    return {"message": "Notifications marked as read"}

@router.get("/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_user),
):
    """Get unread notifications count"""
    return {"count": 0}
