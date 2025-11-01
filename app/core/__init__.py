"""
Core configuration and utilities
"""

from app.core.config import settings
from app.core.database import get_db, Base, engine
from app.core.ai_config import ai_config, get_current_provider

__all__ = [
    "settings",
    "get_db",
    "Base",
    "engine",
    "ai_config",
    "get_current_provider",
]
