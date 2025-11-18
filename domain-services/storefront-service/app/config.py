"""
Configuration module for Storefront Service
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Service Configuration
    SERVICE_NAME: str = "storefront-service"
    SERVICE_PORT: int = 8011
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    EVENT_BUS_URL: str = "redis://localhost:6379/1"
    EVENT_BUS_BACKEND: str = "redis"

    # Core Services
    AUTH_SERVICE_URL: str = "http://localhost:8000"
    USER_SERVICE_URL: str = "http://localhost:8001"
    BILLING_SERVICE_URL: str = "http://localhost:8002"
    LLM_GATEWAY_URL: str = "http://localhost:8003"
    NOTIFICATION_SERVICE_URL: str = "http://localhost:8004"
    LOGGING_SERVICE_URL: str = "http://localhost:8005"
    SITE_SERVICE_URL: str = "http://localhost:8010"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    SERVICE_AUTH_TOKEN: str = ""

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Business Rules
    DEFAULT_CART_EXPIRY_HOURS: int = 24
    LOW_STOCK_THRESHOLD: int = 10
    MAX_CART_ITEMS: int = 50

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
