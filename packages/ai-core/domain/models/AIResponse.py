"""
AI Response Model - Universal response format from all providers
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class AIResponse:
    """
    Universal AI response model from any provider.

    All providers return this standardized format.
    """

    content: str
    tokens_used: int
    model: str
    finish_reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "content": self.content,
            "tokens_used": self.tokens_used,
            "model": self.model,
            "finish_reason": self.finish_reason,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIResponse':
        """Create from dictionary"""
        return cls(
            content=data["content"],
            tokens_used=data["tokens_used"],
            model=data["model"],
            finish_reason=data["finish_reason"],
            metadata=data.get("metadata", {})
        )
