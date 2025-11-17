"""
Core Services Client - Stub for MVP

In production, this would use the shared integrations.core_services module.
For MVP, we provide stubs that simulate core service responses.
"""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class BillingServiceClient:
    """Client for Billing Service (stubbed for MVP)"""

    @staticmethod
    async def check_quota(org_id: str, resource: str) -> Dict[str, Any]:
        """
        Check resource quota

        In production, calls Billing Service API.
        For MVP, returns generous limits.
        """
        logger.info(f"[STUB] Checking {resource} quota for org {org_id}")

        # Stub: Return generous limits for MVP
        quotas = {
            'sites': {'current': 0, 'limit': 10},
            'products': {'current': 0, 'limit': 1000},
            'orders': {'current': 0, 'limit': 10000},
        }

        return quotas.get(resource, {'current': 0, 'limit': 100})

    @staticmethod
    async def record_usage(org_id: str, resource: str, quantity: int = 1):
        """
        Record resource usage

        In production, calls Billing Service API.
        For MVP, just logs.
        """
        logger.info(f"[STUB] Recording {quantity} {resource} usage for org {org_id}")
        # In production: POST to Billing Service /v1/usage/record


class UserServiceClient:
    """Client for User Service (stubbed for MVP)"""

    @staticmethod
    async def get_org(org_id: str) -> Dict[str, Any]:
        """
        Get organization details

        In production, calls User Service API.
        For MVP, returns mock data.
        """
        logger.info(f"[STUB] Fetching org {org_id}")

        return {
            "org_id": org_id,
            "org_name": "Test Organization",
            "plan": "free",
        }


class LLMGatewayClient:
    """Client for LLM Gateway (stubbed for MVP)"""

    @staticmethod
    async def execute_prompt(
        prompt_id: str,
        inputs: Dict[str, Any]
    ) -> str:
        """
        Execute AI prompt

        In production, calls LLM Gateway API.
        For MVP, returns placeholder.
        """
        logger.info(f"[STUB] Executing prompt {prompt_id} with inputs {inputs}")

        # Stub responses
        if prompt_id == "site_description":
            return "A beautiful website for your business."
        elif prompt_id == "seo_meta":
            return "SEO-optimized meta description for your site."

        return "Generated content placeholder"
