"""
Payments API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.user import User
from app.models.payment import Payment, PaymentStatus
from app.api.v1.endpoints.auth import get_current_user

router = APIRouter()

@router.post("/create-intent", status_code=status.HTTP_201_CREATED)
async def create_payment_intent(
    amount: float,
    booking_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create Stripe payment intent"""
    # TODO: Integrate with Stripe
    platform_fee = amount * 0.15  # 15% platform fee
    net_amount = amount - platform_fee
    
    payment = Payment(
        payer_id=current_user.id,
        payee_id=current_user.id,  # TODO: Get from booking
        booking_id=booking_id,
        amount=amount,
        platform_fee=platform_fee,
        net_amount=net_amount,
        status=PaymentStatus.PENDING
    )
    db.add(payment)
    await db.commit()
    return {"payment_id": str(payment.id), "amount": amount, "client_secret": "mock_secret"}

@router.get("/my")
async def get_my_payments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's payments"""
    result = await db.execute(
        select(Payment).where(
            (Payment.payer_id == current_user.id) | (Payment.payee_id == current_user.id)
        )
    )
    payments = result.scalars().all()
    return [{"id": str(p.id), "amount": p.amount, "status": p.status} for p in payments]

@router.get("/{payment_id}")
async def get_payment(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get payment by ID"""
    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none()
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return {"id": str(payment.id), "amount": payment.amount, "status": payment.status}
