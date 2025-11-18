"""
Authentication Middleware

Provides JWT token validation and user context extraction.
Integrates with Core Auth Service for token verification.
"""

from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict
from uuid import UUID
import httpx
import logging
from functools import wraps

from app.config import settings

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


class AuthMiddleware:
    """Authentication middleware for JWT validation"""

    def __init__(self):
        self.auth_service_url = settings.AUTH_SERVICE_URL if hasattr(settings, 'AUTH_SERVICE_URL') else "http://auth-service:8001"

    async def verify_token(self, token: str) -> Optional[Dict]:
        """
        Verify JWT token with Auth Service

        Returns user context if valid, None otherwise
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.auth_service_url}/api/v1/auth/verify",
                    json={"token": token},
                    timeout=5.0
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Token verification failed: {response.status_code}")
                    return None

        except httpx.TimeoutException:
            logger.error("Auth service timeout")
            return None
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    async def get_current_user(self, credentials: Optional[HTTPAuthorizationCredentials]) -> Optional[Dict]:
        """
        Extract current user from bearer token

        Returns:
            Dict with user_id, org_id, email, roles
        """
        if not credentials:
            return None

        token = credentials.credentials
        user_context = await self.verify_token(token)

        return user_context


# Global auth middleware instance
auth_middleware = AuthMiddleware()


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = security
) -> Optional[Dict]:
    """
    Dependency for optional authentication

    Returns user context if authenticated, None otherwise
    Use for endpoints that work for both guest and authenticated users
    """
    if not credentials:
        return None

    return await auth_middleware.get_current_user(credentials)


async def get_current_user_required(
    credentials: Optional[HTTPAuthorizationCredentials] = security
) -> Dict:
    """
    Dependency for required authentication

    Raises 401 if not authenticated
    Use for endpoints that require authentication
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_context = await auth_middleware.get_current_user(credentials)

    if not user_context:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_context


def extract_user_id(user_context: Optional[Dict]) -> Optional[UUID]:
    """
    Extract user_id from user context

    Returns:
        UUID or None if not authenticated
    """
    if not user_context:
        return None

    user_id_str = user_context.get("user_id")
    if user_id_str:
        try:
            return UUID(user_id_str)
        except ValueError:
            logger.error(f"Invalid user_id format: {user_id_str}")
            return None

    return None


def extract_org_id(user_context: Optional[Dict]) -> Optional[UUID]:
    """
    Extract org_id from user context

    Returns:
        UUID or None if not authenticated
    """
    if not user_context:
        return None

    org_id_str = user_context.get("org_id")
    if org_id_str:
        try:
            return UUID(org_id_str)
        except ValueError:
            logger.error(f"Invalid org_id format: {org_id_str}")
            return None

    return None


def has_role(user_context: Optional[Dict], required_role: str) -> bool:
    """
    Check if user has required role

    Args:
        user_context: User context from auth
        required_role: Role to check (e.g., 'admin', 'site_owner')

    Returns:
        True if user has the role
    """
    if not user_context:
        return False

    roles = user_context.get("roles", [])
    return required_role in roles


async def require_role(
    required_role: str,
    user_context: Dict = None
):
    """
    Dependency for role-based access control

    Raises:
        403 if user doesn't have required role
    """
    if not has_role(user_context, required_role):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{required_role}' required"
        )


# Mock implementation for development (when Auth Service is not available)
class MockAuthMiddleware:
    """
    Mock auth middleware for development/testing

    Returns a test user context without calling Auth Service
    """

    async def verify_token(self, token: str) -> Optional[Dict]:
        """Mock token verification"""
        if token == "test-token":
            return {
                "user_id": "00000000-0000-0000-0000-000000000001",
                "org_id": "00000000-0000-0000-0000-000000000010",
                "email": "test@example.com",
                "roles": ["user", "site_owner"]
            }
        return None

    async def get_current_user(self, credentials: Optional[HTTPAuthorizationCredentials]) -> Optional[Dict]:
        """Mock get current user"""
        if not credentials:
            return None

        return await self.verify_token(credentials.credentials)


# Switch between real and mock auth based on environment
if settings.DEBUG:
    logger.warning("Using mock authentication middleware (DEBUG mode)")
    # Uncomment to use mock auth in development
    # auth_middleware = MockAuthMiddleware()
