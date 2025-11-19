"""
Dependency Injection Container for AI Components

Makes it easy to wire up all components and swap implementations.
"""

from typing import Optional, Dict, Any
from ..application.AIEngine import AIEngine, AIEngineBuilder
from ..domain.interfaces import IAIProvider, ICache, ITokenTracker


class AIContainer:
    """
    Dependency injection container for AI components.

    This makes it easy to configure all components in one place
    and swap implementations without changing application code.

    Example:
        # Setup container
        container = AIContainer()
        container.register_provider(OpenAIProvider(api_key="..."))
        container.register_cache(RedisCache(url="..."))

        # Get configured engine anywhere in your app
        engine = container.get_engine()
    """

    _instance: Optional['AIContainer'] = None

    def __init__(self):
        self._provider: Optional[IAIProvider] = None
        self._cache: Optional[ICache] = None
        self._token_tracker: Optional[ITokenTracker] = None
        self._engine: Optional[AIEngine] = None
        self._config: Dict[str, Any] = {
            "cache_enabled": True,
            "cache_ttl_days": 7
        }

    @classmethod
    def get_instance(cls) -> 'AIContainer':
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_provider(self, provider: IAIProvider) -> 'AIContainer':
        """
        Register AI provider.

        Args:
            provider: IAIProvider implementation

        Returns:
            Self for chaining
        """
        self._provider = provider
        self._engine = None  # Reset engine
        return self

    def register_cache(self, cache: ICache) -> 'AIContainer':
        """
        Register cache.

        Args:
            cache: ICache implementation

        Returns:
            Self for chaining
        """
        self._cache = cache
        self._engine = None  # Reset engine
        return self

    def register_token_tracker(self, tracker: ITokenTracker) -> 'AIContainer':
        """
        Register token tracker.

        Args:
            tracker: ITokenTracker implementation

        Returns:
            Self for chaining
        """
        self._token_tracker = tracker
        self._engine = None  # Reset engine
        return self

    def configure(self, config: Dict[str, Any]) -> 'AIContainer':
        """
        Configure container.

        Args:
            config: Configuration dict

        Returns:
            Self for chaining
        """
        self._config.update(config)
        self._engine = None  # Reset engine
        return self

    def get_engine(self) -> AIEngine:
        """
        Get configured AI engine.

        Returns:
            Configured AIEngine instance

        Raises:
            ValueError: If provider not registered
        """
        if self._engine is None:
            if self._provider is None:
                raise ValueError("Provider must be registered before getting engine")

            builder = AIEngineBuilder()
            builder.with_provider(self._provider)

            if self._cache:
                builder.with_cache(self._cache)

            if self._token_tracker:
                builder.with_token_tracker(self._token_tracker)

            builder.with_cache_enabled(self._config.get("cache_enabled", True))
            builder.with_cache_ttl_days(self._config.get("cache_ttl_days", 7))

            self._engine = builder.build()

        return self._engine

    def reset(self) -> None:
        """Reset container (mainly for testing)"""
        self._provider = None
        self._cache = None
        self._token_tracker = None
        self._engine = None
        self._config = {
            "cache_enabled": True,
            "cache_ttl_days": 7
        }


# Global container instance
container = AIContainer.get_instance()
