"""
Cache Interface - For caching AI responses
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
from datetime import timedelta


class ICache(ABC):
    """
    Abstract caching interface.
    Allows for different cache backends (Redis, Memcached, in-memory, etc.)
    """

    @abstractmethod
    async def get(
        self,
        key: str
    ) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None
    ) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live (optional)
        """
        pass

    @abstractmethod
    async def delete(
        self,
        key: str
    ) -> None:
        """
        Delete value from cache.

        Args:
            key: Cache key
        """
        pass

    @abstractmethod
    async def exists(
        self,
        key: str
    ) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if exists, False otherwise
        """
        pass

    @abstractmethod
    async def clear(
        self,
        pattern: Optional[str] = None
    ) -> None:
        """
        Clear cache (optionally by pattern).

        Args:
            pattern: Optional key pattern (e.g., "ai:*")
        """
        pass
