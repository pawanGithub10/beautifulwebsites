"""
FastAPI routers for AI features

Ready-to-use routers for each AI plugin.
"""

from .product_description import router as product_description_router
from .review_response import router as review_response_router
from .social_calendar import router as social_calendar_router

__all__ = [
    "product_description_router",
    "review_response_router",
    "social_calendar_router"
]
