"""
Services Package

Business logic layer:
- product_service: Product catalog and category management
- cart_service: Shopping cart operations
- order_service: Order processing and lifecycle
- event_service: Event publishing for notifications
"""

from .product_service import ProductService
from .cart_service import CartService
from .order_service import OrderService
from .event_service import event_service, EventService

__all__ = [
    "ProductService",
    "CartService",
    "OrderService",
    "event_service",
    "EventService"
]
