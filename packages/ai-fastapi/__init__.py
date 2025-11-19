"""
FastAPI Integration for AI Platform

Provides ready-to-use FastAPI routers, Pydantic models, and middleware
for integrating AI features into FastAPI applications.
"""

from .models import (
    ProductDescriptionRequest,
    ProductDescriptionResponse,
    ReviewResponseRequest,
    ReviewResponseResponse,
    SocialCalendarRequest,
    SocialCalendarResponse,
    SinglePostRequest,
    SinglePostResponse,
    ErrorResponse,
    HealthResponse
)

from .routers import (
    product_description_router,
    review_response_router,
    social_calendar_router
)

from .middleware import AIErrorHandler, add_ai_middleware
from .dependencies import get_ai_engine, get_product_plugin, get_review_plugin, get_calendar_plugin

__version__ = "1.0.0"

__all__ = [
    # Models
    "ProductDescriptionRequest",
    "ProductDescriptionResponse",
    "ReviewResponseRequest",
    "ReviewResponseResponse",
    "SocialCalendarRequest",
    "SocialCalendarResponse",
    "SinglePostRequest",
    "SinglePostResponse",
    "ErrorResponse",
    "HealthResponse",

    # Routers
    "product_description_router",
    "review_response_router",
    "social_calendar_router",

    # Middleware
    "AIErrorHandler",
    "add_ai_middleware",

    # Dependencies
    "get_ai_engine",
    "get_product_plugin",
    "get_review_plugin",
    "get_calendar_plugin"
]
