"""
Anthropic Claude Provider Package

Implements IAIProvider interface for Anthropic's Claude models.

Installation:
    pip install anthropic

Usage:
    from ai_providers.anthropic import ClaudeProvider

    provider = ClaudeProvider(api_key="sk-ant-...")
    # Use with AIEngine
"""

from .ClaudeProvider import ClaudeProvider
from .config import ClaudeConfig, DEFAULT_MODELS, MODEL_ALIASES

__version__ = "1.0.0"

__all__ = [
    "ClaudeProvider",
    "ClaudeConfig",
    "DEFAULT_MODELS",
    "MODEL_ALIASES"
]
