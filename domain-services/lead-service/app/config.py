"""Configuration settings for Lead Service"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""
    
    # Service
    SERVICE_NAME: str = "lead-service"
    SERVICE_PORT: int = 8013
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/lead_db"
    
    # Redis & Events
    REDIS_URL: str = "redis://localhost:6379/0"
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    EVENTS_ENABLED: bool = False
    
    # Lead Settings
    DEFAULT_LEAD_SCORE: int = 0
    AUTO_ASSIGN_LEADS: bool = False
    LEAD_RETENTION_DAYS: int = 365
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    class Config:
        env_file = ".env"


settings = Settings()
