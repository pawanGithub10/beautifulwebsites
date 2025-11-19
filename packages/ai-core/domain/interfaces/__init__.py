"""
Core domain interfaces (ports) for AI platform.

These interfaces define contracts that external implementations must follow.
This enables dependency inversion and makes the system highly modular.
"""

from .IAIProvider import IAIProvider
from .IPromptTemplate import IPromptTemplate
from .ITokenTracker import ITokenTracker
from .ICache import ICache

__all__ = [
    "IAIProvider",
    "IPromptTemplate",
    "ITokenTracker",
    "ICache"
]
