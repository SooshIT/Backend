"""
Bookings API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.booking import Booking, SessionStatus
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_booking(
    mentor_id: UUID,
    session_date: datetime,
    amount: float,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create new booking"""
    booking = Booking(
        student_id=current_user.id,
        mentor_id=mentor_id,
        title="Mentorship Session",
        session_date=session_date,
        amount=amount,
        status=SessionStatus.PENDING
    )
    db.add(booking)
    await db.commit()
    return {"message": "Booking created", "booking_id": str(booking.id)}

@router.get("/my")
async def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's bookings"""
    result = await db.execute(
        select(Booking).where(
            (Booking.student_id == current_user.id) | (Booking.mentor_id == current_user.id)
        )
    )
    bookings = result.scalars().all()
    return [{"id": str(b.id), "status": b.status, "amount": b.amount} for b in bookings]

@router.get("/{booking_id}")
async def get_booking(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get booking by ID"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return {"id": str(booking.id), "status": booking.status}

@router.put("/{booking_id}/cancel")
async def cancel_booking(
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Cancel booking"""
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = SessionStatus.CANCELLED
    booking.cancelled_by = current_user.id
    booking.cancelled_at = datetime.utcnow()
    await db.commit()
    return {"message": "Booking cancelled"}
