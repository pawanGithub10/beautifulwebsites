from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    SERVICE_NAME: str = "widget-service"
    SERVICE_PORT: int = 8015
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/widget_db"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    class Config:
        env_file = ".env"

settings = Settings()
