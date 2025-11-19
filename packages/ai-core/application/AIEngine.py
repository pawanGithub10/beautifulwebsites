"""
AI Engine - Core orchestrator for all AI operations

This is the heart of the modular AI system. It's completely framework-agnostic
and can be used anywhere - FastAPI, Flask, Django, standalone scripts, etc.
"""

from typing import Optional, Dict, Any
from datetime import timedelta
import hashlib
import json
import logging

from ..domain.interfaces import IAIProvider, ICache, ITokenTracker
from ..domain.models import AIRequest, AIResponse, PromptContext, TokenUsage

logger = logging.getLogger(__name__)


class AIEngine:
    """
    Core AI Engine - Framework Agnostic.

    This class orchestrates all AI operations:
    - Calls providers (OpenAI, Claude, etc.)
    - Manages caching
    - Tracks token usage
    - Handles errors

    Can be used in ANY Python framework or standalone.

    Example:
        engine = AIEngine(provider=OpenAIProvider())
        response = await engine.generate(request)
    """

    def __init__(
        self,
        provider: IAIProvider,
        cache: Optional[ICache] = None,
        token_tracker: Optional[ITokenTracker] = None,
        enable_cache: bool = True,
        cache_ttl_days: int = 7
    ):
        """
        Initialize AI Engine.

        Args:
            provider: AI provider implementation (required)
            cache: Cache implementation (optional)
            token_tracker: Token tracker implementation (optional)
            enable_cache: Whether to use caching
            cache_ttl_days: Cache TTL in days
        """
        self.provider = provider
        self.cache = cache
        self.token_tracker = token_tracker
        self.enable_cache = enable_cache
        self.cache_ttl = timedelta(days=cache_ttl_days)

        logger.info(f"AIEngine initialized with provider: {provider.get_name()}")

    async def generate(
        self,
        request: AIRequest,
        context: Optional[PromptContext] = None,
        use_cache: bool = True
    ) -> AIResponse:
        """
        Generate AI completion.

        This is the main entry point for all AI generation.
        Handles caching, provider calls, and token tracking.

        Args:
            request: AIRequest with prompt and parameters
            context: Optional context for tracking
            use_cache: Whether to use cache for this request

        Returns:
            AIResponse with generated content

        Raises:
            Exception: If generation fails
        """

        # Try cache first
        if use_cache and self.enable_cache and self.cache:
            cache_key = self._generate_cache_key(request)

            try:
                cached = await self.cache.get(cache_key)
                if cached:
                    logger.debug(f"Cache hit for key: {cache_key}")
                    return AIResponse.from_dict(cached)
            except Exception as e:
                logger.warning(f"Cache get failed: {e}")

        # Generate from provider
        logger.info(f"Generating completion with {self.provider.get_name()}")
        try:
            response = await self.provider.generate_completion(request)
        except Exception as e:
            logger.error(f"Provider generation failed: {e}")
            raise

        # Track token usage
        if self.token_tracker and context:
            try:
                await self._track_usage(response, context)
            except Exception as e:
                logger.warning(f"Token tracking failed: {e}")

        # Cache response
        if use_cache and self.enable_cache and self.cache:
            try:
                await self.cache.set(
                    cache_key,
                    response.to_dict(),
                    ttl=self.cache_ttl
                )
                logger.debug(f"Cached response for key: {cache_key}")
            except Exception as e:
                logger.warning(f"Cache set failed: {e}")

        return response

    async def generate_batch(
        self,
        requests: list[AIRequest],
        context: Optional[PromptContext] = None
    ) -> list[AIResponse]:
        """
        Generate multiple completions in batch.

        Args:
            requests: List of AIRequests
            context: Optional context for tracking

        Returns:
            List of AIResponses
        """
        responses = []
        for request in requests:
            response = await self.generate(request, context)
            responses.append(response)

        return responses

    async def estimate_cost(
        self,
        text: str,
        model: str = "gpt-4"
    ) -> float:
        """
        Estimate cost for generating completion for given text.

        Args:
            text: Input text
            model: Model to use

        Returns:
            Estimated cost in USD
        """
        tokens = await self.provider.estimate_tokens(text)
        pricing = self.provider.get_pricing()
        model_price = pricing.get(model, 0.03)

        return (tokens / 1000) * model_price

    async def check_quota(
        self,
        site_id: str
    ) -> Dict[str, Any]:
        """
        Check quota for a site.

        Args:
            site_id: Site identifier

        Returns:
            Quota information
        """
        if not self.token_tracker:
            return {"within_quota": True, "message": "No quota tracking enabled"}

        return await self.token_tracker.check_quota(site_id)

    async def get_usage_stats(
        self,
        site_id: str,
        period: str = "month"
    ) -> Dict[str, Any]:
        """
        Get usage statistics for a site.

        Args:
            site_id: Site identifier
            period: Time period

        Returns:
            Usage statistics
        """
        if not self.token_tracker:
            return {"message": "No usage tracking enabled"}

        return await self.token_tracker.get_usage(site_id, period)

    async def health_check(self) -> Dict[str, Any]:
        """
        Check system health.

        Returns:
            Health status dict
        """
        provider_health = await self.provider.check_health()

        cache_health = None
        if self.cache:
            try:
                cache_health = await self.cache.exists("_health_check")
            except:
                cache_health = False

        return {
            "provider": {
                "name": self.provider.get_name(),
                "healthy": provider_health,
                "capabilities": self.provider.get_capabilities()
            },
            "cache": {
                "enabled": self.enable_cache,
                "healthy": cache_health
            },
            "tracking": {
                "enabled": self.token_tracker is not None
            }
        }

    def _generate_cache_key(self, request: AIRequest) -> str:
        """
        Generate deterministic cache key from request.

        Args:
            request: AIRequest

        Returns:
            Cache key string
        """
        key_data = {
            "prompt": request.prompt,
            "system_prompt": request.system_prompt,
            "model": request.model,
            "temperature": request.temperature,
            "response_format": request.response_format
        }

        key_string = json.dumps(key_data, sort_keys=True)
        hash_value = hashlib.sha256(key_string.encode()).hexdigest()

        return f"ai:cache:{hash_value}"

    async def _track_usage(
        self,
        response: AIResponse,
        context: PromptContext
    ) -> None:
        """
        Track token usage.

        Args:
            response: AI response
            context: Prompt context
        """
        if not self.token_tracker:
            return

        # Get pricing
        pricing = self.provider.get_pricing()

        # Create usage record
        usage = TokenUsage.from_response(response, pricing)

        # Track
        await self.token_tracker.track_usage(
            site_id=context.site_id or "unknown",
            feature=context.feature or "unknown",
            usage=usage
        )

        logger.info(
            f"Tracked usage: {usage.total_tokens} tokens, "
            f"${usage.estimated_cost:.4f} for {context.feature}"
        )


class AIEngineBuilder:
    """
    Builder pattern for constructing AIEngine with various configurations.

    Makes it easy to create AIEngine instances with different setups.

    Example:
        engine = (AIEngineBuilder()
            .with_provider(OpenAIProvider())
            .with_cache(RedisCache())
            .with_token_tracker(PostgresTracker())
            .build())
    """

    def __init__(self):
        self._provider: Optional[IAIProvider] = None
        self._cache: Optional[ICache] = None
        self._token_tracker: Optional[ITokenTracker] = None
        self._enable_cache: bool = True
        self._cache_ttl_days: int = 7

    def with_provider(self, provider: IAIProvider) -> 'AIEngineBuilder':
        """Set AI provider"""
        self._provider = provider
        return self

    def with_cache(self, cache: ICache) -> 'AIEngineBuilder':
        """Set cache"""
        self._cache = cache
        return self

    def with_token_tracker(self, tracker: ITokenTracker) -> 'AIEngineBuilder':
        """Set token tracker"""
        self._token_tracker = tracker
        return self

    def with_cache_enabled(self, enabled: bool) -> 'AIEngineBuilder':
        """Enable/disable cache"""
        self._enable_cache = enabled
        return self

    def with_cache_ttl_days(self, days: int) -> 'AIEngineBuilder':
        """Set cache TTL"""
        self._cache_ttl_days = days
        return self

    def build(self) -> AIEngine:
        """Build AIEngine instance"""
        if not self._provider:
            raise ValueError("Provider is required")

        return AIEngine(
            provider=self._provider,
            cache=self._cache,
            token_tracker=self._token_tracker,
            enable_cache=self._enable_cache,
            cache_ttl_days=self._cache_ttl_days
        )
