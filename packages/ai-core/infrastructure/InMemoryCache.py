"""
In-Memory Cache Implementation

Simple cache for testing and standalone use.
For production, use Redis or similar.
"""

from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from ..domain.interfaces import ICache


class InMemoryCache(ICache):
    """
    Simple in-memory cache implementation.

    Good for:
    - Testing
    - Development
    - Standalone scripts
    - Low-traffic applications

    For production with multiple instances, use Redis instead.
    """

    def __init__(self):
        self._cache: Dict[str, tuple[Any, Optional[datetime]]] = {}

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key not in self._cache:
            return None

        value, expires_at = self._cache[key]

        # Check expiration
        if expires_at and datetime.utcnow() > expires_at:
            del self._cache[key]
            return None

        return value

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None
    ) -> None:
        """Set value in cache"""
        expires_at = None
        if ttl:
            expires_at = datetime.utcnow() + ttl

        self._cache[key] = (value, expires_at)

    async def delete(self, key: str) -> None:
        """Delete value from cache"""
        if key in self._cache:
            del self._cache[key]

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        return key in self._cache

    async def clear(self, pattern: Optional[str] = None) -> None:
        """Clear cache"""
        if pattern is None:
            self._cache.clear()
        else:
            # Simple pattern matching (only supports ending with *)
            if pattern.endswith("*"):
                prefix = pattern[:-1]
                keys_to_delete = [
                    k for k in self._cache.keys()
                    if k.startswith(prefix)
                ]
                for key in keys_to_delete:
                    del self._cache[key]

    def size(self) -> int:
        """Get cache size"""
        return len(self._cache)
