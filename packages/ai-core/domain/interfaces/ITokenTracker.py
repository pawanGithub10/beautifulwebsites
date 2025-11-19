"""
Token Tracker Interface - For tracking AI usage and costs
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from ..models.TokenUsage import TokenUsage


class ITokenTracker(ABC):
    """
    Abstract token tracking interface.
    Allows for different storage backends (PostgreSQL, MongoDB, etc.)
    """

    @abstractmethod
    async def track_usage(
        self,
        site_id: str,
        feature: str,
        usage: TokenUsage
    ) -> None:
        """
        Track token usage for a site and feature.

        Args:
            site_id: Site identifier
            feature: Feature name (e.g., "product_description")
            usage: TokenUsage object with usage details
        """
        pass

    @abstractmethod
    async def get_usage(
        self,
        site_id: str,
        period: str = "month"
    ) -> Dict[str, Any]:
        """
        Get usage statistics for a site.

        Args:
            site_id: Site identifier
            period: Time period ("day", "week", "month", "year")

        Returns:
            Dict with usage statistics
            Example: {
                "total_tokens": 125000,
                "total_cost": 2.50,
                "by_feature": {...}
            }
        """
        pass

    @abstractmethod
    async def check_quota(
        self,
        site_id: str
    ) -> Dict[str, Any]:
        """
        Check if site is within quota.

        Args:
            site_id: Site identifier

        Returns:
            Dict with quota info
            Example: {
                "within_quota": True,
                "used": 45000,
                "limit": 100000,
                "percentage": 45.0
            }
        """
        pass

    @abstractmethod
    async def calculate_cost(
        self,
        usage: TokenUsage,
        pricing: Dict[str, float]
    ) -> float:
        """
        Calculate cost for given usage.

        Args:
            usage: TokenUsage object
            pricing: Pricing dict from provider

        Returns:
            Estimated cost in USD
        """
        pass
