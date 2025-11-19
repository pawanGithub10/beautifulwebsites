"""
Anthropic Claude Provider Configuration
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ClaudeConfig:
    """
    Configuration for Claude provider.

    Example:
        config = ClaudeConfig(
            api_key="sk-ant-...",
            default_model="claude-3-sonnet-20240229"
        )
    """

    api_key: str
    default_model: str = "claude-3-sonnet-20240229"
    base_url: Optional[str] = None
    timeout: int = 60
    max_retries: int = 3


# Default models configuration
DEFAULT_MODELS = {
    "fast": "claude-3-haiku-20240307",
    "balanced": "claude-3-sonnet-20240229",
    "quality": "claude-3-opus-20240229"
}

# Model aliases for convenience
MODEL_ALIASES = {
    "opus": "claude-3-opus-20240229",
    "sonnet": "claude-3-sonnet-20240229",
    "haiku": "claude-3-haiku-20240307"
}
