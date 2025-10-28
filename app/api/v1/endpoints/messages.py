"""
Messages API Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.get("/conversations")
async def get_conversations(
    current_user: User = Depends(get_current_user),
):
    """Get user conversations"""
    return []

@router.get("/conversations/{user_id}")
async def get_conversation_with_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Get conversation with specific user"""
    return []

@router.post("/send")
async def send_message(
    recipient_id: UUID,
    message: str,
    current_user: User = Depends(get_current_user),
):
    """Send message"""
    return {"message": "Message sent"}
