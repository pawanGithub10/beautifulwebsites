"""
Configuration for Auth Service
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str = "auth-service"
    SERVICE_PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql://platform_user:platform_pass@localhost:5432/auth_service_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT Configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Password
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_BCRYPT_ROUNDS: int = 12

    # Email
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: str = "noreply@platform.com"
    SMTP_FROM_NAME: str = "Platform Auth"

    # OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None

    # Security
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_ATTEMPT_WINDOW_MINUTES: int = 15
    ACCOUNT_LOCKOUT_DURATION_MINUTES: int = 30

    # URLs
    FRONTEND_URL: str = "http://localhost:3000"
    PASSWORD_RESET_URL_TEMPLATE: str = "{frontend_url}/auth/reset-password?token={token}"
    EMAIL_VERIFICATION_URL_TEMPLATE: str = "{frontend_url}/auth/verify-email?token={token}"

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
