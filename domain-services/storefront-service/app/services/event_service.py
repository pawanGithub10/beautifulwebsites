"""
Event Service - Event publishing for notifications and orchestration

Publishes CloudEvents for:
- Order lifecycle events
- Cart events
- Product events
- Inventory events

These events can trigger:
- Customer notifications (email, SMS)
- Admin notifications
- Orchestration workflows
- Analytics tracking
"""

from typing import Dict, Any, Optional
from uuid import UUID
import logging
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)


class EventService:
    """
    Service for publishing domain events

    Events follow CloudEvents specification and are published to:
    - Redis Streams (for real-time processing)
    - RabbitMQ (for reliable async processing)
    """

    def __init__(self):
        self.service_name = settings.SERVICE_NAME
        self.enabled = getattr(settings, 'EVENTS_ENABLED', False)

        # TODO: Initialize event publisher when shared library is available
        # from shared.events.publisher import EventPublisher
        # self.publisher = EventPublisher(
        #     redis_url=settings.REDIS_URL,
        #     rabbitmq_url=settings.RABBITMQ_URL
        # )

    async def publish_event(
        self,
        event_type: str,
        subject: str,
        data: Dict[str, Any],
        site_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None
    ):
        """
        Publish CloudEvent

        Args:
            event_type: Event type (e.g., 'order.placed', 'order.status_changed')
            subject: Event subject (e.g., order_id, product_id)
            data: Event payload
            site_id: Site context
            user_id: User context
        """
        if not self.enabled:
            logger.debug(f"Events disabled, skipping: {event_type}")
            return

        event = {
            "specversion": "1.0",
            "type": f"com.beautifulwebsites.storefront.{event_type}",
            "source": self.service_name,
            "subject": subject,
            "id": str(UUID()),
            "time": datetime.utcnow().isoformat(),
            "datacontenttype": "application/json",
            "data": data
        }

        # Add context
        if site_id:
            event["data"]["site_id"] = str(site_id)
        if user_id:
            event["data"]["user_id"] = str(user_id)

        logger.info(f"Publishing event: {event_type} - {subject}")

        # TODO: Publish to event streams when infrastructure is ready
        # await self.publisher.publish(event)

    # ======================
    # ORDER EVENTS
    # ======================

    async def publish_order_placed(
        self,
        order_id: UUID,
        order_number: str,
        site_id: UUID,
        customer_email: str,
        customer_phone: str,
        total: float,
        items_count: int,
        user_id: Optional[UUID] = None
    ):
        """
        Publish order placed event

        Triggers:
        - Order confirmation email to customer
        - Order notification to site owner
        - Admin dashboard update
        """
        await self.publish_event(
            event_type="order.placed",
            subject=str(order_id),
            site_id=site_id,
            user_id=user_id,
            data={
                "order_id": str(order_id),
                "order_number": order_number,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "total": total,
                "items_count": items_count,
                "notification_channels": ["email", "sms", "dashboard"]
            }
        )

    async def publish_order_status_changed(
        self,
        order_id: UUID,
        order_number: str,
        site_id: UUID,
        customer_email: str,
        customer_phone: str,
        old_status: str,
        new_status: str,
        user_id: Optional[UUID] = None
    ):
        """
        Publish order status changed event

        Triggers:
        - Status update notification to customer
        - Admin dashboard update
        """
        await self.publish_event(
            event_type="order.status_changed",
            subject=str(order_id),
            site_id=site_id,
            user_id=user_id,
            data={
                "order_id": str(order_id),
                "order_number": order_number,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "old_status": old_status,
                "new_status": new_status,
                "notification_channels": ["email", "sms"]
            }
        )

    async def publish_order_cancelled(
        self,
        order_id: UUID,
        order_number: str,
        site_id: UUID,
        customer_email: str,
        customer_phone: str,
        reason: str,
        user_id: Optional[UUID] = None
    ):
        """
        Publish order cancelled event

        Triggers:
        - Cancellation notification to customer
        - Refund processing (if applicable)
        - Admin notification
        """
        await self.publish_event(
            event_type="order.cancelled",
            subject=str(order_id),
            site_id=site_id,
            user_id=user_id,
            data={
                "order_id": str(order_id),
                "order_number": order_number,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "reason": reason,
                "notification_channels": ["email", "sms"]
            }
        )

    async def publish_order_delivered(
        self,
        order_id: UUID,
        order_number: str,
        site_id: UUID,
        customer_email: str,
        customer_phone: str,
        user_id: Optional[UUID] = None
    ):
        """
        Publish order delivered event

        Triggers:
        - Delivery confirmation to customer
        - Request for review
        - Payment settlement (for COD)
        """
        await self.publish_event(
            event_type="order.delivered",
            subject=str(order_id),
            site_id=site_id,
            user_id=user_id,
            data={
                "order_id": str(order_id),
                "order_number": order_number,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "notification_channels": ["email", "sms"]
            }
        )

    # ======================
    # CART EVENTS
    # ======================

    async def publish_cart_abandoned(
        self,
        cart_id: UUID,
        site_id: UUID,
        customer_email: Optional[str],
        items_count: int,
        total: float,
        user_id: Optional[UUID] = None
    ):
        """
        Publish cart abandoned event

        Triggers:
        - Abandoned cart recovery email
        - Discount offer
        """
        if not customer_email:
            return  # Can't send recovery email without email

        await self.publish_event(
            event_type="cart.abandoned",
            subject=str(cart_id),
            site_id=site_id,
            user_id=user_id,
            data={
                "cart_id": str(cart_id),
                "customer_email": customer_email,
                "items_count": items_count,
                "total": total,
                "notification_channels": ["email"]
            }
        )

    # ======================
    # INVENTORY EVENTS
    # ======================

    async def publish_low_stock_alert(
        self,
        product_id: UUID,
        product_name: str,
        site_id: UUID,
        current_stock: int,
        threshold: int,
        variant_id: Optional[UUID] = None
    ):
        """
        Publish low stock alert event

        Triggers:
        - Low stock notification to site owner
        - Admin dashboard alert
        """
        await self.publish_event(
            event_type="inventory.low_stock",
            subject=str(product_id),
            site_id=site_id,
            data={
                "product_id": str(product_id),
                "product_name": product_name,
                "variant_id": str(variant_id) if variant_id else None,
                "current_stock": current_stock,
                "threshold": threshold,
                "notification_channels": ["dashboard", "email"]
            }
        )

    async def publish_out_of_stock(
        self,
        product_id: UUID,
        product_name: str,
        site_id: UUID,
        variant_id: Optional[UUID] = None
    ):
        """
        Publish out of stock event

        Triggers:
        - Out of stock notification to site owner
        - Product hidden from storefront
        """
        await self.publish_event(
            event_type="inventory.out_of_stock",
            subject=str(product_id),
            site_id=site_id,
            data={
                "product_id": str(product_id),
                "product_name": product_name,
                "variant_id": str(variant_id) if variant_id else None,
                "notification_channels": ["dashboard", "email"]
            }
        )

    # ======================
    # PRODUCT EVENTS
    # ======================

    async def publish_product_created(
        self,
        product_id: UUID,
        product_name: str,
        site_id: UUID,
        user_id: Optional[UUID] = None
    ):
        """
        Publish product created event

        Triggers:
        - Search index update
        - Analytics tracking
        """
        await self.publish_event(
            event_type="product.created",
            subject=str(product_id),
            site_id=site_id,
            user_id=user_id,
            data={
                "product_id": str(product_id),
                "product_name": product_name
            }
        )

    async def publish_product_updated(
        self,
        product_id: UUID,
        product_name: str,
        site_id: UUID,
        user_id: Optional[UUID] = None
    ):
        """
        Publish product updated event

        Triggers:
        - Search index update
        - Cache invalidation
        """
        await self.publish_event(
            event_type="product.updated",
            subject=str(product_id),
            site_id=site_id,
            user_id=user_id,
            data={
                "product_id": str(product_id),
                "product_name": product_name
            }
        )


# Global event service instance
event_service = EventService()
