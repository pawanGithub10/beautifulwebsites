"""
Middleware Package

Provides authentication and other cross-cutting concerns:
- auth: JWT token validation and user context
"""

from .auth import (
    get_current_user_optional,
    get_current_user_required,
    extract_user_id,
    extract_org_id,
    has_role,
    require_role
)

__all__ = [
    "get_current_user_optional",
    "get_current_user_required",
    "extract_user_id",
    "extract_org_id",
    "has_role",
    "require_role"
]
