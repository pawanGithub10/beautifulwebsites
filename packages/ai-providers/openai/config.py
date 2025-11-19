"""
OpenAI Provider Configuration
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class OpenAIConfig:
    """
    Configuration for OpenAI provider.

    Example:
        config = OpenAIConfig(
            api_key="sk-...",
            default_model="gpt-4",
            organization="org-..."
        )
    """

    api_key: str
    default_model: str = "gpt-4"
    organization: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 60
    max_retries: int = 3


# Default models configuration
DEFAULT_MODELS = {
    "fast": "gpt-3.5-turbo",
    "balanced": "gpt-4-turbo",
    "quality": "gpt-4"
}
