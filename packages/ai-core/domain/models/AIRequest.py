"""
AI Request Model - Universal request format for all providers
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class AIRequest:
    """
    Universal AI request model that works with any provider.

    This abstraction allows us to switch providers without changing
    application code.
    """

    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 500
    model: str = "gpt-4"
    response_format: str = "text"  # "text" or "json"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "prompt": self.prompt,
            "system_prompt": self.system_prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "model": self.model,
            "response_format": self.response_format,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AIRequest':
        """Create from dictionary"""
        return cls(
            prompt=data["prompt"],
            system_prompt=data.get("system_prompt"),
            temperature=data.get("temperature", 0.7),
            max_tokens=data.get("max_tokens", 500),
            model=data.get("model", "gpt-4"),
            response_format=data.get("response_format", "text"),
            metadata=data.get("metadata", {})
        )
