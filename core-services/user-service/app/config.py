"""
User Service Configuration
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings
    """
    # Service
    SERVICE_NAME: str = "user-service"
    SERVICE_PORT: int = 8001
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://redis:6379/2"

    # AWS S3 (for profile pictures)
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_S3_REGION: str = "us-east-1"

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_EXTENSIONS: list = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

    # Auth Service
    AUTH_SERVICE_URL: str = "http://auth-service:8000"
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    # Notification Service
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8003"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Cache TTL (seconds)
    CACHE_TTL_PROFILE: int = 300  # 5 minutes
    CACHE_TTL_PREFERENCES: int = 600  # 10 minutes

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
