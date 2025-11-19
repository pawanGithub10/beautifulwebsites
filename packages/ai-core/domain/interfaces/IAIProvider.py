"""
AI Provider Interface - Core abstraction for any LLM provider

This interface defines the contract that any AI provider (OpenAI, Claude, local models)
must implement. This allows complete provider independence and easy swapping.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..models.AIRequest import AIRequest
from ..models.AIResponse import AIResponse


class IAIProvider(ABC):
    """
    Abstract AI provider interface.
    Any LLM provider (OpenAI, Claude, local LLMs, etc.) must implement this interface.

    Benefits:
    - Provider agnostic code
    - Easy to swap providers
    - Mockable for testing
    - Support multiple providers simultaneously
    """

    @abstractmethod
    async def generate_completion(
        self,
        request: AIRequest
    ) -> AIResponse:
        """
        Generate AI completion from request.

        Args:
            request: AIRequest with prompt, parameters, etc.

        Returns:
            AIResponse with generated content

        Raises:
            ProviderException: If generation fails
        """
        pass

    @abstractmethod
    async def estimate_tokens(
        self,
        text: str
    ) -> int:
        """
        Estimate token count for given text.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """
        Check if provider is healthy and accessible.

        Returns:
            True if healthy, False otherwise
        """
        pass

    @abstractmethod
    def get_pricing(self) -> Dict[str, float]:
        """
        Get current pricing per 1K tokens for each model.

        Returns:
            Dict mapping model names to price per 1K tokens
            Example: {"gpt-4": 0.03, "gpt-3.5-turbo": 0.001}
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """
        Get provider capabilities and supported features.

        Returns:
            Dict with provider capabilities
            Example: {
                "models": ["gpt-4", "gpt-3.5-turbo"],
                "max_tokens": 8192,
                "supports_functions": True,
                "supports_vision": True,
                "supports_streaming": True
            }
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Get provider name.

        Returns:
            Provider name (e.g., "openai", "anthropic", "ollama")
        """
        pass
