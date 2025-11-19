"""
OpenAI Provider Package

Implements IAIProvider interface for OpenAI's GPT models.

Installation:
    pip install openai tiktoken

Usage:
    from ai_providers.openai import OpenAIProvider

    provider = OpenAIProvider(api_key="sk-...")
    # Use with AIEngine
"""

from .OpenAIProvider import OpenAIProvider
from .config import OpenAIConfig, DEFAULT_MODELS

__version__ = "1.0.0"

__all__ = [
    "OpenAIProvider",
    "OpenAIConfig",
    "DEFAULT_MODELS"
]
