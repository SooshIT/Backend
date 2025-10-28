"""
Custom Exceptions for Soosh Platform
"""

from fastapi import status
from typing import Optional, Dict, Any


class SooshException(Exception):
    """Base exception for Soosh platform"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "ERROR",
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


# Authentication Exceptions
class AuthenticationException(SooshException):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTH_ERROR",
            details=details,
        )


class InvalidCredentialsException(AuthenticationException):
    """Raised when login credentials are invalid"""

    def __init__(self):
        super().__init__(message="Invalid email or password")


class TokenExpiredException(AuthenticationException):
    """Raised when JWT token has expired"""

    def __init__(self):
        super().__init__(message="Token has expired")


class InvalidTokenException(AuthenticationException):
    """Raised when JWT token is invalid"""

    def __init__(self):
        super().__init__(message="Invalid token")


# Authorization Exceptions
class AuthorizationException(SooshException):
    """Raised when user lacks permissions"""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN",
        )


class UserTypeNotAllowedException(AuthorizationException):
    """Raised when user type cannot perform action"""

    def __init__(self, required_type: str):
        super().__init__(
            message=f"Only {required_type} users can perform this action"
        )


# User Exceptions
class UserNotFoundException(SooshException):
    """Raised when user is not found"""

    def __init__(self, user_id: str = None):
        message = f"User {user_id} not found" if user_id else "User not found"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="USER_NOT_FOUND",
        )


class UserAlreadyExistsException(SooshException):
    """Raised when user with email/username already exists"""

    def __init__(self, field: str = "email"):
        super().__init__(
            message=f"User with this {field} already exists",
            status_code=status.HTTP_409_CONFLICT,
            error_code="USER_EXISTS",
        )


class EmailNotVerifiedException(SooshException):
    """Raised when action requires verified email"""

    def __init__(self):
        super().__init__(
            message="Email verification required",
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="EMAIL_NOT_VERIFIED",
        )


# Booking Exceptions
class BookingNotFoundException(SooshException):
    """Raised when booking is not found"""

    def __init__(self, booking_id: str):
        super().__init__(
            message=f"Booking {booking_id} not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="BOOKING_NOT_FOUND",
        )


class BookingConflictException(SooshException):
    """Raised when time slot is already booked"""

    def __init__(self):
        super().__init__(
            message="Time slot is already booked",
            status_code=status.HTTP_409_CONFLICT,
            error_code="BOOKING_CONFLICT",
        )


class BookingCancellationException(SooshException):
    """Raised when booking cannot be cancelled"""

    def __init__(self, reason: str):
        super().__init__(
            message=f"Cannot cancel booking: {reason}",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="CANCELLATION_ERROR",
        )


# Payment Exceptions
class PaymentException(SooshException):
    """Base payment exception"""

    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            error_code="PAYMENT_ERROR",
        )


class PaymentFailedException(PaymentException):
    """Raised when payment processing fails"""

    def __init__(self, reason: str = "Payment failed"):
        super().__init__(message=reason)


class InsufficientFundsException(PaymentException):
    """Raised when payment method has insufficient funds"""

    def __init__(self):
        super().__init__(message="Insufficient funds")


# Mentor Exceptions
class MentorNotAvailableException(SooshException):
    """Raised when mentor is not available"""

    def __init__(self):
        super().__init__(
            message="Mentor is not available at this time",
            status_code=status.HTTP_409_CONFLICT,
            error_code="MENTOR_UNAVAILABLE",
        )


class NotAMentorException(SooshException):
    """Raised when user is not a mentor"""

    def __init__(self):
        super().__init__(
            message="User is not a mentor",
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="NOT_A_MENTOR",
        )


# AI Exceptions
class AIProcessingException(SooshException):
    """Raised when AI processing fails"""

    def __init__(self, message: str = "AI processing failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="AI_ERROR",
        )


class EmbeddingGenerationException(AIProcessingException):
    """Raised when vector embedding generation fails"""

    def __init__(self):
        super().__init__(message="Failed to generate embeddings")


# Validation Exceptions
class ValidationException(SooshException):
    """Raised for validation errors"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details,
        )


# Rate Limiting
class RateLimitException(SooshException):
    """Raised when rate limit is exceeded"""

    def __init__(self):
        super().__init__(
            message="Too many requests. Please try again later",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
        )
