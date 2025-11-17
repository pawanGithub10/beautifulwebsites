"""
Event Service - Publishes domain events

Uses the shared event publisher library.
"""

import logging
from uuid import UUID
from datetime import datetime

logger = logging.getLogger(__name__)


class EventService:
    """Service for publishing domain events"""

    def __init__(self):
        # In production, this would use the shared events.publisher module
        # For now, we'll stub it out
        pass

    async def publish_site_created(self, site):
        """Publish SITE_CREATED event"""
        event_data = {
            "site_id": str(site.site_id),
            "org_id": str(site.org_id),
            "slug": site.slug,
            "site_type": site.site_type,
            "status": site.status,
        }

        logger.info(f"[EVENT] site.created: {event_data}")

        # TODO: Use shared event publisher
        # await publish_event(
        #     event_type="site.created",
        #     data=event_data,
        #     topic="site-events",
        #     subject=str(site.site_id)
        # )

    async def publish_site_updated(self, site):
        """Publish SITE_UPDATED event"""
        event_data = {
            "site_id": str(site.site_id),
            "org_id": str(site.org_id),
            "slug": site.slug,
        }

        logger.info(f"[EVENT] site.updated: {event_data}")

    async def publish_site_published(self, site):
        """Publish SITE_PUBLISHED event"""
        event_data = {
            "site_id": str(site.site_id),
            "org_id": str(site.org_id),
            "slug": site.slug,
            "site_type": site.site_type,
        }

        logger.info(f"[EVENT] site.published: {event_data}")

    async def publish_site_deleted(self, site):
        """Publish SITE_DELETED event"""
        event_data = {
            "site_id": str(site.site_id),
            "org_id": str(site.org_id),
        }

        logger.info(f"[EVENT] site.deleted: {event_data}")
