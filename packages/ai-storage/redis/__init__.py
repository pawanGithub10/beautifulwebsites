"""
Redis Storage Package

Production Redis implementations for caching.

Installation:
    pip install redis

Usage:
    from ai_storage.redis import RedisCache

    cache = RedisCache(url="redis://localhost:6379/0")
"""

from .RedisCache import RedisCache

__version__ = "1.0.0"

__all__ = ["RedisCache"]
