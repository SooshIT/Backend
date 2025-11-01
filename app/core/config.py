"""
Application Configuration
Loads environment variables and provides settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )

    # Application
    APP_NAME: str = "Soosh"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4

    # Database
    DATABASE_URL: str
    DATABASE_SYNC_URL: str
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OAuth2
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None

    APPLE_CLIENT_ID: Optional[str] = None
    APPLE_TEAM_ID: Optional[str] = None
    APPLE_KEY_ID: Optional[str] = None
    APPLE_PRIVATE_KEY_PATH: Optional[str] = None

    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_REDIRECT_URI: Optional[str] = None

    # OpenAI
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIMENSION: int = 1536

    # Whisper API
    WHISPER_API_URL: str
    WHISPER_API_KEY: Optional[str] = None

    # TTS
    TTS_PROVIDER: str = "openai"
    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_VOICE_ID: Optional[str] = None

    # Stripe
    STRIPE_PUBLIC_KEY: str
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_CURRENCY: str = "USD"

    # AWS S3
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str
    AWS_CLOUDFRONT_URL: Optional[str] = None

    # Email
    EMAIL_PROVIDER: str = "sendgrid"
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: str
    FROM_NAME: str = "Soosh Platform"

    # SMS
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # Video
    VIDEO_PROVIDER: str = "daily"
    DAILY_API_KEY: Optional[str] = None
    DAILY_DOMAIN: Optional[str] = None

    # Sentry
    SENTRY_DSN: Optional[str] = None
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8081",
        "http://localhost:8082",
        "https://zcvvkhqk-8081.uks1.devtunnels.ms",
        "https://renita-peopleless-cleo.ngrok-free.dev",
        "https://*.devtunnels.ms",
        "https://*.ngrok-free.dev",
        "exp://192.168.0.176:8082",
        "*"
    ]
    CORS_ALLOW_CREDENTIALS: bool = True

    # WebSocket
    WS_PING_INTERVAL: int = 25
    WS_PING_TIMEOUT: int = 10

    # AI Configuration
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 1000
    AI_RECOMMENDATION_BATCH_SIZE: int = 10

    # Caching
    CACHE_TTL_SECONDS: int = 3600
    CACHE_RECOMMENDATIONS_TTL: int = 1800

    # Background Tasks
    CELERY_TASK_ALWAYS_EAGER: bool = False

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Feature Flags
    ENABLE_AI_AGENT: bool = True
    ENABLE_PROXIMITY_SEARCH: bool = True
    ENABLE_VIDEO_CALLS: bool = True
    ENABLE_PAYMENTS: bool = True

    # Platform Settings
    PLATFORM_FEE_PERCENTAGE: float = 15.0
    MIN_BOOKING_ADVANCE_HOURS: int = 2
    MAX_CANCELLATION_HOURS: int = 24


@lru_cache()
def get_settings() -> Settings:
    """
    Create cached settings instance
    Use this function to get settings throughout the app
    """
    return Settings()


# Global settings instance
settings = get_settings()
