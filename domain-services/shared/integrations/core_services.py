"""
Core Services Client - Shared library for calling core platform services

This library provides a unified interface for domain services to interact with:
- Auth Service (8000)
- User Service (8001)
- Billing Service (8002)
- LLM Gateway (8003)
- Notification Service (8004)
- Logging & Audit Service (8005)

Key features:
- Automatic service discovery
- Circuit breaker pattern
- Retry with exponential backoff
- Request/response logging
- Token management
- Caching for frequently accessed data
"""

import os
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging
from enum import Enum

import httpx
from pydantic import BaseModel
import redis.asyncio as redis

logger = logging.getLogger(__name__)


# ======================
# CONFIGURATION
# ======================

class ServiceEndpoint(str, Enum):
    """Core service endpoints"""
    AUTH = "AUTH_SERVICE_URL"
    USER = "USER_SERVICE_URL"
    BILLING = "BILLING_SERVICE_URL"
    LLM_GATEWAY = "LLM_GATEWAY_URL"
    NOTIFICATION = "NOTIFICATION_SERVICE_URL"
    LOGGING = "LOGGING_SERVICE_URL"


# Default URLs (can be overridden by environment variables)
DEFAULT_SERVICE_URLS = {
    ServiceEndpoint.AUTH: "http://localhost:8000",
    ServiceEndpoint.USER: "http://localhost:8001",
    ServiceEndpoint.BILLING: "http://localhost:8002",
    ServiceEndpoint.LLM_GATEWAY: "http://localhost:8003",
    ServiceEndpoint.NOTIFICATION: "http://localhost:8004",
    ServiceEndpoint.LOGGING: "http://localhost:8005",
}


# ======================
# BASE CLIENT
# ======================

class CoreServicesClient:
    """
    Singleton client for accessing core platform services
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CoreServicesClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.http_client: Optional[httpx.AsyncClient] = None
            self.redis_client: Optional[redis.Redis] = None
            self.service_urls: Dict[ServiceEndpoint, str] = {}
            self.service_token: Optional[str] = None  # Service-to-service auth token

    @classmethod
    async def initialize(cls):
        """Initialize the core services client"""
        instance = cls()

        # Initialize HTTP client
        instance.http_client = httpx.AsyncClient(
            timeout=30.0,
            limits=httpx.Limits(max_keepalive_connections=20, max_connections=100)
        )

        # Initialize Redis for caching
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        instance.redis_client = redis.from_url(redis_url, decode_responses=True)

        # Load service URLs from environment
        for service in ServiceEndpoint:
            url = os.getenv(service.value, DEFAULT_SERVICE_URLS[service])
            instance.service_urls[service] = url

        # Get service-to-service auth token (from environment or Auth Service)
        instance.service_token = os.getenv("SERVICE_AUTH_TOKEN")

        cls._initialized = True
        logger.info("Core services client initialized")

    @classmethod
    async def close(cls):
        """Close all connections"""
        instance = cls()

        if instance.http_client:
            await instance.http_client.aclose()

        if instance.redis_client:
            await instance.redis_client.close()

        logger.info("Core services client closed")

    @classmethod
    async def _request(
        cls,
        method: str,
        service: ServiceEndpoint,
        path: str,
        json: Optional[Dict] = None,
        params: Optional[Dict] = None,
        headers: Optional[Dict] = None,
        retry_count: int = 3
    ) -> Dict[str, Any]:
        """
        Make HTTP request to a core service with retry logic

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            service: Service endpoint enum
            path: API path (e.g., "/v1/users")
            json: Request body (for POST/PUT/PATCH)
            params: Query parameters
            headers: Additional headers
            retry_count: Number of retries on failure

        Returns:
            Response JSON

        Raises:
            httpx.HTTPStatusError: On 4xx/5xx status codes
        """
        instance = cls()

        if not cls._initialized:
            raise RuntimeError("CoreServicesClient not initialized. Call initialize() first.")

        base_url = instance.service_urls[service]
        url = f"{base_url}{path}"

        # Prepare headers
        request_headers = {
            "Content-Type": "application/json",
            "User-Agent": f"{os.getenv('SERVICE_NAME', 'domain-service')}/1.0"
        }

        # Add service auth token if available
        if instance.service_token:
            request_headers["Authorization"] = f"Bearer {instance.service_token}"

        if headers:
            request_headers.update(headers)

        # Retry logic with exponential backoff
        for attempt in range(retry_count):
            try:
                response = await instance.http_client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                    headers=request_headers
                )

                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error calling {service.value} {path}: {e.response.status_code}")
                raise

            except httpx.RequestError as e:
                logger.error(f"Request error calling {service.value} {path} (attempt {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

    # ======================
    # CACHE HELPERS
    # ======================

    @classmethod
    async def _get_cached(cls, key: str) -> Optional[Any]:
        """Get value from cache"""
        instance = cls()
        try:
            value = await instance.redis_client.get(key)
            return value
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None

    @classmethod
    async def _set_cached(cls, key: str, value: str, ttl: int = 300):
        """Set value in cache with TTL (default 5 minutes)"""
        instance = cls()
        try:
            await instance.redis_client.setex(key, ttl, value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")


# ======================
# AUTH SERVICE CLIENT
# ======================

class AuthServiceClient:
    """Client for Auth Service (Port 8000)"""

    @staticmethod
    async def validate_token(token: str) -> Dict[str, Any]:
        """
        Validate JWT token

        Args:
            token: JWT token to validate

        Returns:
            Decoded token payload with user_id, org_id, roles, etc.
        """
        # Check cache first
        cache_key = f"auth:token:{token[:16]}"  # Use first 16 chars as cache key
        cached = await CoreServicesClient._get_cached(cache_key)

        if cached:
            import json
            return json.loads(cached)

        # Call Auth Service
        response = await CoreServicesClient._request(
            method="POST",
            service=ServiceEndpoint.AUTH,
            path="/v1/auth/validate",
            json={"token": token}
        )

        # Cache for 5 minutes
        import json
        await CoreServicesClient._set_cached(cache_key, json.dumps(response), ttl=300)

        return response

    @staticmethod
    async def refresh_token(refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token

        Args:
            refresh_token: Refresh token

        Returns:
            New access token and refresh token
        """
        return await CoreServicesClient._request(
            method="POST",
            service=ServiceEndpoint.AUTH,
            path="/v1/auth/refresh",
            json={"refresh_token": refresh_token}
        )


# ======================
# USER SERVICE CLIENT
# ======================

class UserServiceClient:
    """Client for User Service (Port 8001)"""

    @staticmethod
    async def get_user(user_id: str) -> Dict[str, Any]:
        """
        Get user details

        Args:
            user_id: User ID

        Returns:
            User object with profile, org, roles
        """
        # Check cache first
        cache_key = f"user:profile:{user_id}"
        cached = await CoreServicesClient._get_cached(cache_key)

        if cached:
            import json
            return json.loads(cached)

        # Call User Service
        response = await CoreServicesClient._request(
            method="GET",
            service=ServiceEndpoint.USER,
            path=f"/v1/users/{user_id}"
        )

        # Cache for 10 minutes
        import json
        await CoreServicesClient._set_cached(cache_key, json.dumps(response), ttl=600)

        return response

    @staticmethod
    async def get_org(org_id: str) -> Dict[str, Any]:
        """
        Get organization details

        Args:
            org_id: Organization ID

        Returns:
            Org object
        """
        cache_key = f"org:{org_id}"
        cached = await CoreServicesClient._get_cached(cache_key)

        if cached:
            import json
            return json.loads(cached)

        response = await CoreServicesClient._request(
            method="GET",
            service=ServiceEndpoint.USER,
            path=f"/v1/orgs/{org_id}"
        )

        import json
        await CoreServicesClient._set_cached(cache_key, json.dumps(response), ttl=600)

        return response

    @staticmethod
    async def check_permission(user_id: str, resource: str, action: str) -> bool:
        """
        Check if user has permission to perform action on resource

        Args:
            user_id: User ID
            resource: Resource type (e.g., "site", "product")
            action: Action (e.g., "create", "read", "update", "delete")

        Returns:
            True if user has permission
        """
        response = await CoreServicesClient._request(
            method="POST",
            service=ServiceEndpoint.USER,
            path="/v1/permissions/check",
            json={
                "user_id": user_id,
                "resource": resource,
                "action": action
            }
        )

        return response.get("allowed", False)


# ======================
# BILLING SERVICE CLIENT
# ======================

class BillingServiceClient:
    """Client for Billing Service (Port 8002)"""

    @staticmethod
    async def check_feature_access(org_id: str, feature: str) -> bool:
        """
        Check if org's subscription plan includes a feature

        Args:
            org_id: Organization ID
            feature: Feature name (e.g., "storefront", "booking", "custom_domain")

        Returns:
            True if feature is enabled
        """
        cache_key = f"billing:feature:{org_id}:{feature}"
        cached = await CoreServicesClient._get_cached(cache_key)

        if cached:
            return cached == "true"

        response = await CoreServicesClient._request(
            method="POST",
            service=ServiceEndpoint.BILLING,
            path="/v1/features/check",
            json={
                "org_id": org_id,
                "feature": feature
            }
        )

        has_access = response.get("enabled", False)

        # Cache for 5 minutes
        await CoreServicesClient._set_cached(cache_key, "true" if has_access else "false", ttl=300)

        return has_access

    @staticmethod
    async def check_quota(org_id: str, resource: str) -> Dict[str, Any]:
        """
        Check resource quota (e.g., max sites, max products)

        Args:
            org_id: Organization ID
            resource: Resource type (e.g., "sites", "products")

        Returns:
            Quota info with current usage and limit
        """
        response = await CoreServicesClient._request(
            method="POST",
            service=ServiceEndpoint.BILLING,
            path="/v1/quotas/check",
            json={
                "org_id": org_id,
                "resource": resource
            }
        )

        return response

    @staticmethod
    async def record_usage(org_id: str, resource: str, quantity: int = 1):
        """
        Record resource usage for billing

        Args:
            org_id: Organization ID
            resource: Resource type
            quantity: Amount used
        """
        await CoreServicesClient._request(
            method="POST",
            service=ServiceEndpoint.BILLING,
            path="/v1/usage/record",
            json={
                "org_id": org_id,
                "resource": resource,
                "quantity": quantity,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


# ======================
# LLM GATEWAY CLIENT
# ======================

class LLMGatewayClient:
    """Client for LLM Gateway (Port 8003)"""

    @staticmethod
    async def execute_prompt(
        prompt_id: str,
        inputs: Dict[str, Any],
        model: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Execute a predefined prompt

        Args:
            prompt_id: Prompt template ID (e.g., "product_description", "seo_meta")
            inputs: Variables to inject into prompt
            model: Optional model override (defaults to prompt's configured model)
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        response = await CoreServicesClient._request(
            method="POST",
            service=ServiceEndpoint.LLM_GATEWAY,
            path="/v1/prompts/execute",
            json={
                "prompt_id": prompt_id,
                "inputs": inputs,
                "model": model,
                "temperature": temperature
            }
        )

        return response.get("output", "")

    @staticmethod
    async def chat_completion(
        messages: List[Dict[str, str]],
        model: str = "gpt-4",
        max_tokens: int = 500
    ) -> str:
        """
        Direct chat completion (for chatbots, etc.)

        Args:
            messages: Chat messages in format [{"role": "user", "content": "..."}]
            model: Model to use
            max_tokens: Max response length

        Returns:
            Generated response
        """
        response = await CoreServicesClient._request(
            method="POST",
            service=ServiceEndpoint.LLM_GATEWAY,
            path="/v1/chat/completions",
            json={
                "messages": messages,
                "model": model,
                "max_tokens": max_tokens
            }
        )

        return response.get("content", "")


# ======================
# NOTIFICATION SERVICE CLIENT
# ======================

class NotificationServiceClient:
    """Client for Notification Service (Port 8004)"""

    @staticmethod
    async def send_notification(
        template: str,
        recipient: str,
        channel: str,
        data: Dict[str, Any],
        org_id: Optional[str] = None
    ):
        """
        Send notification using template

        Args:
            template: Template name (e.g., "order_confirmation", "booking_reminder")
            recipient: Recipient identifier (phone, email, user_id)
            channel: Channel (email, sms, whatsapp, push)
            data: Template variables
            org_id: Optional org_id for tracking
        """
        await CoreServicesClient._request(
            method="POST",
            service=ServiceEndpoint.NOTIFICATION,
            path="/v1/notifications/send",
            json={
                "template": template,
                "recipient": recipient,
                "channel": channel,
                "data": data,
                "org_id": org_id
            }
        )

    @staticmethod
    async def send_bulk_notifications(
        template: str,
        recipients: List[str],
        channel: str,
        data: Dict[str, Any]
    ):
        """
        Send bulk notifications

        Args:
            template: Template name
            recipients: List of recipient identifiers
            channel: Channel
            data: Shared template variables
        """
        await CoreServicesClient._request(
            method="POST",
            service=ServiceEndpoint.NOTIFICATION,
            path="/v1/notifications/send-bulk",
            json={
                "template": template,
                "recipients": recipients,
                "channel": channel,
                "data": data
            }
        )


# ======================
# LOGGING SERVICE CLIENT
# ======================

class LoggingServiceClient:
    """Client for Logging & Audit Service (Port 8005)"""

    @staticmethod
    async def log_event(
        level: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        org_id: Optional[str] = None,
        user_id: Optional[str] = None
    ):
        """
        Log structured event

        Args:
            level: Log level (debug, info, warning, error, critical)
            message: Log message
            context: Additional context data
            org_id: Optional org_id
            user_id: Optional user_id
        """
        await CoreServicesClient._request(
            method="POST",
            service=ServiceEndpoint.LOGGING,
            path="/v1/logs",
            json={
                "level": level,
                "message": message,
                "context": context or {},
                "org_id": org_id,
                "user_id": user_id,
                "service": os.getenv("SERVICE_NAME", "unknown-service"),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )

    @staticmethod
    async def audit_action(
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: str,
        org_id: str,
        changes: Optional[Dict[str, Any]] = None
    ):
        """
        Log audit trail for important actions

        Args:
            action: Action performed (created, updated, deleted, etc.)
            resource_type: Type of resource (site, product, order, etc.)
            resource_id: Resource ID
            user_id: User who performed action
            org_id: Organization ID
            changes: What changed (before/after values)
        """
        await CoreServicesClient._request(
            method="POST",
            service=ServiceEndpoint.LOGGING,
            path="/v1/audit",
            json={
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "user_id": user_id,
                "org_id": org_id,
                "changes": changes or {},
                "service": os.getenv("SERVICE_NAME", "unknown-service"),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        )


# ======================
# CONVENIENCE EXPORTS
# ======================

__all__ = [
    "CoreServicesClient",
    "AuthServiceClient",
    "UserServiceClient",
    "BillingServiceClient",
    "LLMGatewayClient",
    "NotificationServiceClient",
    "LoggingServiceClient",
]
