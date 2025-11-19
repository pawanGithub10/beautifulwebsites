"""
Token Usage Model - For tracking AI usage
"""

from dataclasses import dataclass
from typing import Dict, Any
from datetime import datetime


@dataclass
class TokenUsage:
    """
    Token usage tracking model.

    Used for billing, quotas, and analytics.
    """

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    estimated_cost: float
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "model": self.model,
            "estimated_cost": self.estimated_cost,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

    @classmethod
    def from_response(
        cls,
        response: 'AIResponse',
        pricing: Dict[str, float]
    ) -> 'TokenUsage':
        """Create from AIResponse and pricing info"""
        # Estimate token split (this is approximate)
        prompt_tokens = response.tokens_used // 2
        completion_tokens = response.tokens_used - prompt_tokens

        # Calculate cost
        model_pricing = pricing.get(response.model, 0.03)  # Default to GPT-4 pricing
        cost = (response.tokens_used / 1000) * model_pricing

        return cls(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=response.tokens_used,
            model=response.model,
            estimated_cost=cost
        )
