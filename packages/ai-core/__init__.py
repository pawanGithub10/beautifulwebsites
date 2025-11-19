"""
AI Platform Core - Universal AI Engine

A modular, framework-agnostic AI engine that can be used anywhere.
"""

__version__ = "1.0.0"

from .application.AIEngine import AIEngine, AIEngineBuilder
from .domain.models import AIRequest, AIResponse, PromptContext, TokenUsage
from .domain.interfaces import IAIProvider, ICache, ITokenTracker, IPromptTemplate
from .di.container import AIContainer, container
from .infrastructure.InMemoryCache import InMemoryCache

__all__ = [
    # Main engine
    "AIEngine",
    "AIEngineBuilder",

    # Models
    "AIRequest",
    "AIResponse",
    "PromptContext",
    "TokenUsage",

    # Interfaces
    "IAIProvider",
    "ICache",
    "ITokenTracker",
    "IPromptTemplate",

    # DI Container
    "AIContainer",
    "container",

    # Simple implementations
    "InMemoryCache",
]
