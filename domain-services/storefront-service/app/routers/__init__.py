"""
API Routers Package

Exposes all domain services through REST endpoints:
- products: Product catalog and category management
- cart: Shopping cart operations
- orders: Order processing and lifecycle
"""

from . import products, cart, orders

__all__ = ["products", "cart", "orders"]
