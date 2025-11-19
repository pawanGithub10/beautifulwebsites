"""
FastAPI dependencies for AI engine and plugins

Provides dependency injection for AI components in FastAPI routes.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from ai_core.application.AIEngine import AIEngine, AIEngineBuilder
from ai_core.di.container import AIContainer
from ai_providers.openai.OpenAIProvider import OpenAIProvider
from ai_providers.anthropic.ClaudeProvider import ClaudeProvider
from ai_storage.redis.RedisCache import RedisCache
from ai_storage.postgres.PostgresTokenTracker import PostgresTokenTracker
from ai_features.product_description.plugin import ProductDescriptionPlugin
from ai_features.review_response.plugin import ReviewResponsePlugin
from ai_features.social_calendar.plugin import SocialCalendarPlugin
import os
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# GLOBAL STATE (Configure once at startup)
# ============================================================================

_container: Optional[AIContainer] = None
_ai_engine: Optional[AIEngine] = None
_product_plugin: Optional[ProductDescriptionPlugin] = None
_review_plugin: Optional[ReviewResponsePlugin] = None
_calendar_plugin: Optional[SocialCalendarPlugin] = None


def configure_ai_platform(
    provider_type: str = "openai",
    api_key: Optional[str] = None,
    enable_cache: bool = True,
    enable_tracking: bool = True,
    redis_url: Optional[str] = None,
    postgres_url: Optional[str] = None
) -> AIContainer:
    """
    Configure the AI platform at application startup.

    Call this once in your FastAPI startup event handler.

    Args:
        provider_type: "openai" or "claude"
        api_key: API key for the provider (or set via env var)
        enable_cache: Enable Redis caching
        enable_tracking: Enable PostgreSQL token tracking
        redis_url: Redis connection URL (or set via REDIS_URL env var)
        postgres_url: PostgreSQL connection URL (or set via DATABASE_URL env var)

    Returns:
        Configured AIContainer instance

    Example:
        ```python
        from fastapi import FastAPI
        from ai_fastapi.dependencies import configure_ai_platform

        app = FastAPI()

        @app.on_event("startup")
        async def startup():
            configure_ai_platform(
                provider_type="openai",
                api_key=os.getenv("OPENAI_API_KEY"),
                enable_cache=True,
                enable_tracking=True
            )
        ```
    """
    global _container, _ai_engine, _product_plugin, _review_plugin, _calendar_plugin

    logger.info("Configuring AI Platform...")

    # Create container
    _container = AIContainer()

    # Configure provider
    if provider_type == "openai":
        key = api_key or os.getenv("OPENAI_API_KEY")
        if not key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY env var or pass api_key.")
        provider = OpenAIProvider(api_key=key)
        _container.register_provider(provider)
        logger.info("Configured OpenAI provider")

    elif provider_type == "claude":
        key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY env var or pass api_key.")
        provider = ClaudeProvider(api_key=key)
        _container.register_provider(provider)
        logger.info("Configured Claude provider")

    else:
        raise ValueError(f"Unknown provider type: {provider_type}. Use 'openai' or 'claude'.")

    # Configure cache
    if enable_cache:
        redis_conn = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        cache = RedisCache(redis_url=redis_conn)
        _container.register_cache(cache)
        logger.info(f"Configured Redis cache: {redis_conn}")

    # Configure token tracker
    if enable_tracking:
        db_url = postgres_url or os.getenv("DATABASE_URL")
        if db_url:
            tracker = PostgresTokenTracker(database_url=db_url)
            _container.register_token_tracker(tracker)
            logger.info(f"Configured PostgreSQL token tracker")
        else:
            logger.warning("PostgreSQL URL not provided. Token tracking disabled.")

    # Build AI engine
    _ai_engine = _container.get_engine()
    logger.info("AI Engine configured successfully")

    # Initialize plugins
    _product_plugin = ProductDescriptionPlugin(ai_engine=_ai_engine)
    _review_plugin = ReviewResponsePlugin(ai_engine=_ai_engine)
    _calendar_plugin = SocialCalendarPlugin(ai_engine=_ai_engine)
    logger.info("All plugins initialized")

    return _container


def get_container() -> AIContainer:
    """Get the global AI container (must call configure_ai_platform first)"""
    if _container is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI Platform not configured. Call configure_ai_platform() at startup."
        )
    return _container


def get_ai_engine() -> AIEngine:
    """
    FastAPI dependency to get the AI engine.

    Usage:
        ```python
        @app.get("/health")
        async def health(engine: AIEngine = Depends(get_ai_engine)):
            healthy = await engine.provider.check_health()
            return {"healthy": healthy}
        ```
    """
    if _ai_engine is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI Engine not configured. Call configure_ai_platform() at startup."
        )
    return _ai_engine


def get_product_plugin() -> ProductDescriptionPlugin:
    """
    FastAPI dependency to get the Product Description plugin.

    Usage:
        ```python
        @app.post("/product/description")
        async def generate(
            request: ProductDescriptionRequest,
            plugin: ProductDescriptionPlugin = Depends(get_product_plugin)
        ):
            result = await plugin.generate_description(...)
            return result
        ```
    """
    if _product_plugin is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Product Description plugin not initialized"
        )
    return _product_plugin


def get_review_plugin() -> ReviewResponsePlugin:
    """
    FastAPI dependency to get the Review Response plugin.

    Usage:
        ```python
        @app.post("/review/respond")
        async def respond(
            request: ReviewResponseRequest,
            plugin: ReviewResponsePlugin = Depends(get_review_plugin)
        ):
            result = await plugin.generate_response(...)
            return result
        ```
    """
    if _review_plugin is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Review Response plugin not initialized"
        )
    return _review_plugin


def get_calendar_plugin() -> SocialCalendarPlugin:
    """
    FastAPI dependency to get the Social Calendar plugin.

    Usage:
        ```python
        @app.post("/social/calendar")
        async def generate_calendar(
            request: SocialCalendarRequest,
            plugin: SocialCalendarPlugin = Depends(get_calendar_plugin)
        ):
            result = await plugin.generate_calendar(...)
            return result
        ```
    """
    if _calendar_plugin is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Social Calendar plugin not initialized"
        )
    return _calendar_plugin


# ============================================================================
# UTILITY DEPENDENCIES
# ============================================================================

async def verify_api_key(api_key: Optional[str] = None) -> bool:
    """
    Optional dependency for API key verification.

    Usage:
        ```python
        from fastapi import Header

        @app.post("/product/description")
        async def generate(
            request: ProductDescriptionRequest,
            x_api_key: str = Header(...),
            verified: bool = Depends(verify_api_key)
        ):
            # Your secured endpoint
            pass
        ```
    """
    # Implement your API key verification logic here
    # For now, just a placeholder
    return True


async def get_site_id_from_token(authorization: Optional[str] = None) -> Optional[str]:
    """
    Extract site_id from JWT token or API key.

    Usage:
        ```python
        from fastapi import Header

        @app.post("/product/description")
        async def generate(
            request: ProductDescriptionRequest,
            site_id: str = Depends(get_site_id_from_token)
        ):
            # site_id extracted from auth token
            pass
        ```
    """
    # Implement JWT parsing or API key lookup here
    # For now, just a placeholder
    return None
