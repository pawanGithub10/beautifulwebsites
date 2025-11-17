"""
Authentication middleware

Validates JWT tokens from Auth Service.
Extracts user_id and org_id from token for use in routes.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
import jwt
import httpx

from app.config import settings

security = HTTPBearer()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """
    Verify JWT token with Auth Service

    Returns:
        Dict with user_id, org_id, roles, etc.

    Raises:
        HTTPException: If token is invalid
    """
    token = credentials.credentials

    try:
        # Option 1: Call Auth Service to validate token (recommended for production)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/v1/auth/validate",
                json={"token": token},
                timeout=5.0
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication token"
                )

            token_data = response.json()
            return token_data

    except httpx.RequestError:
        # If Auth Service is unavailable, fall back to local JWT verification
        # (Only for development - production should fail if Auth Service is down)
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            return payload
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )


async def get_current_user(
    token_data: Dict[str, Any] = Depends(verify_token)
) -> Dict[str, Any]:
    """
    Get current user from validated token

    Returns:
        Dict with user_id, org_id, email, roles
    """
    if not token_data.get('user_id'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    return token_data


async def require_org_access(
    org_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> bool:
    """
    Verify that current user has access to specified org

    Args:
        org_id: Organization ID to check access for

    Returns:
        True if user has access

    Raises:
        HTTPException: If user doesn't have access
    """
    user_org_id = current_user.get('org_id')

    if str(user_org_id) != str(org_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this organization"
        )

    return True
