"""
Analytics API Endpoints
"""

from fastapi import APIRouter, Depends
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
):
    """Get dashboard analytics"""
    return {
        "total_sessions": 0,
        "total_earnings": 0,
        "total_students": 0,
        "avg_rating": 0
    }

@router.get("/earnings")
async def get_earnings_stats(
    current_user: User = Depends(get_current_user),
):
    """Get earnings analytics"""
    return {"total": 0, "this_month": 0, "last_month": 0}

@router.get("/activity")
async def get_activity_stats(
    current_user: User = Depends(get_current_user),
):
    """Get activity analytics"""
    return {"sessions_completed": 0, "hours_mentored": 0}
