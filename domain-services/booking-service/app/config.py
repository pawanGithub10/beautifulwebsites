"""
Configuration settings for Booking Service
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # Service
    SERVICE_NAME: str = "booking-service"
    SERVICE_PORT: int = 8012
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/booking_db"

    # Redis & Events
    REDIS_URL: str = "redis://localhost:6379/0"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    EVENTS_ENABLED: bool = False

    # Booking Settings
    DEFAULT_SLOT_DURATION_MINUTES: int = 30
    BOOKING_ADVANCE_DAYS: int = 90  # How far in advance bookings can be made
    CANCELLATION_HOURS_BEFORE: int = 24  # Minimum hours before appointment to cancel

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001"
    ]

    class Config:
        env_file = ".env"


settings = Settings()
