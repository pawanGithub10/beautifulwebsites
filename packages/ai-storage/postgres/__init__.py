"""
PostgreSQL Storage Package

Production PostgreSQL implementations for token tracking.

Installation:
    pip install asyncpg sqlalchemy[asyncio]

Usage:
    from ai_storage.postgres import PostgresTokenTracker

    tracker = PostgresTokenTracker(
        db_url="postgresql+asyncpg://user:pass@localhost/db"
    )
"""

from .PostgresTokenTracker import PostgresTokenTracker
from .models import AITokenUsage, SiteQuota, Base

__version__ = "1.0.0"

__all__ = [
    "PostgresTokenTracker",
    "AITokenUsage",
    "SiteQuota",
    "Base"
]
