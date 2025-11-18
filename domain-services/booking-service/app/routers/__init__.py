"""
API Routers Package

Exposes all domain services through REST endpoints:
- services: Service catalog and category management
- providers: Provider, schedule, and blocked slot management
- availability: Availability checking
- bookings: Booking lifecycle management
"""

from . import services, providers, availability, bookings

__all__ = ["services", "providers", "availability", "bookings"]
