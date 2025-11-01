"""
Database models
"""

from app.models.user import User, UserType, UserStatus, AgeGroup
from app.models.ai_profile import UserAIProfile

# TODO: Import additional models as they are implemented
# from app.models.category import Category
# from app.models.opportunity import Opportunity
# from app.models.mentor import Mentor
# from app.models.booking import Booking
# from app.models.payment import Payment
# from app.models.learning_path import LearningPath
# from app.models.notification import Notification
# from app.models.message import Message
# from app.models.ai_agent import AIAgent

__all__ = [
    "User",
    "UserType",
    "UserStatus",
    "AgeGroup",
    "UserAIProfile",
]
