"""
API V1 Router
Aggregates all endpoint routers
"""

from fastapi import APIRouter

# Import all routers
from app.api.v1.endpoints import (
    voice_chat,
    auth,
    users,
    ai_profiling,
    categories,
    opportunities,
    mentors,
    bookings,
    payments,
    notifications,
    messages,
    analytics,
)

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(voice_chat.router, prefix="/voice", tags=["Voice AI"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(ai_profiling.router, prefix="/ai-profiling", tags=["AI Profiling"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(opportunities.router, prefix="/opportunities", tags=["Opportunities"])
api_router.include_router(mentors.router, prefix="/mentors", tags=["Mentors"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(messages.router, prefix="/messages", tags=["Messages"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
