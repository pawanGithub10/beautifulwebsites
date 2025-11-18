"""
Configuration for Notification Service
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str = "notification-service"
    SERVICE_PORT: int = 8003

    # Database
    DATABASE_URL: str = "postgresql://platform_user:platform_pass@localhost:5432/notification_service_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Email (SMTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@platform.com"
    SMTP_FROM_NAME: str = "Platform"
    SMTP_USE_TLS: bool = True

    # SMS (Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_FROM_NUMBER: Optional[str] = None

    # Push Notifications (Firebase)
    FIREBASE_CREDENTIALS_PATH: Optional[str] = None
    FIREBASE_PROJECT_ID: Optional[str] = None

    # SendGrid (alternative email provider)
    SENDGRID_API_KEY: Optional[str] = None

    # Retry settings
    MAX_RETRIES: int = 3
    RETRY_DELAY_SECONDS: int = 300  # 5 minutes

    # Rate limiting
    RATE_LIMIT_EMAIL_PER_HOUR: int = 1000
    RATE_LIMIT_SMS_PER_HOUR: int = 100
    RATE_LIMIT_PUSH_PER_HOUR: int = 5000

    # Batch processing
    BATCH_SIZE: int = 100
    BATCH_PROCESSING_INTERVAL_SECONDS: int = 60

    # Template paths
    TEMPLATE_DIR: str = "app/templates"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Celery (Task Queue)
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
