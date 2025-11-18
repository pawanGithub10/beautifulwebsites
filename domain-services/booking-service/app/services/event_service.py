"""
Event Service - Event publishing for notifications and orchestration

Publishes CloudEvents for:
- Booking lifecycle events
- Reminder events
- Provider schedule events

These events can trigger:
- Customer notifications (email, SMS)
- Provider notifications
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
            event_type: Event type (e.g., 'booking.created', 'booking.cancelled')
            subject: Event subject (e.g., booking_id)
            data: Event payload
            site_id: Site context
            user_id: User context
        """
        if not self.enabled:
            logger.debug(f"Events disabled, skipping: {event_type}")
            return

        event = {
            "specversion": "1.0",
            "type": f"com.beautifulwebsites.booking.{event_type}",
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
    # BOOKING EVENTS
    # ======================

    async def publish_booking_created(
        self,
        booking_id: UUID,
        booking_number: str,
        site_id: UUID,
        service_name: str,
        provider_name: Optional[str],
        booking_date: str,
        start_time: str,
        customer_name: str,
        customer_email: Optional[str],
        customer_phone: str,
        user_id: Optional[UUID] = None
    ):
        """
        Publish booking created event

        Triggers:
        - Booking confirmation email to customer
        - SMS confirmation to customer
        - Provider notification
        - Admin dashboard update
        """
        await self.publish_event(
            event_type="booking.created",
            subject=str(booking_id),
            site_id=site_id,
            user_id=user_id,
            data={
                "booking_id": str(booking_id),
                "booking_number": booking_number,
                "service_name": service_name,
                "provider_name": provider_name,
                "booking_date": booking_date,
                "start_time": start_time,
                "customer_name": customer_name,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "notification_channels": ["email", "sms", "dashboard"]
            }
        )

    async def publish_booking_rescheduled(
        self,
        booking_id: UUID,
        booking_number: str,
        site_id: UUID,
        old_date: str,
        old_time: str,
        new_date: str,
        new_time: str,
        customer_email: Optional[str],
        customer_phone: str,
        user_id: Optional[UUID] = None
    ):
        """
        Publish booking rescheduled event

        Triggers:
        - Reschedule notification to customer
        - Provider notification
        """
        await self.publish_event(
            event_type="booking.rescheduled",
            subject=str(booking_id),
            site_id=site_id,
            user_id=user_id,
            data={
                "booking_id": str(booking_id),
                "booking_number": booking_number,
                "old_date": old_date,
                "old_time": old_time,
                "new_date": new_date,
                "new_time": new_time,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "notification_channels": ["email", "sms"]
            }
        )

    async def publish_booking_cancelled(
        self,
        booking_id: UUID,
        booking_number: str,
        site_id: UUID,
        booking_date: str,
        start_time: str,
        customer_email: Optional[str],
        customer_phone: str,
        reason: str,
        cancelled_by_customer: bool,
        user_id: Optional[UUID] = None
    ):
        """
        Publish booking cancelled event

        Triggers:
        - Cancellation notification to customer
        - Provider notification
        - Admin notification
        """
        await self.publish_event(
            event_type="booking.cancelled",
            subject=str(booking_id),
            site_id=site_id,
            user_id=user_id,
            data={
                "booking_id": str(booking_id),
                "booking_number": booking_number,
                "booking_date": booking_date,
                "start_time": start_time,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "reason": reason,
                "cancelled_by": "customer" if cancelled_by_customer else "business",
                "notification_channels": ["email", "sms"]
            }
        )

    async def publish_booking_completed(
        self,
        booking_id: UUID,
        booking_number: str,
        site_id: UUID,
        service_name: str,
        customer_email: Optional[str],
        customer_phone: str,
        user_id: Optional[UUID] = None
    ):
        """
        Publish booking completed event

        Triggers:
        - Thank you message to customer
        - Review request
        - Payment settlement (if pending)
        """
        await self.publish_event(
            event_type="booking.completed",
            subject=str(booking_id),
            site_id=site_id,
            user_id=user_id,
            data={
                "booking_id": str(booking_id),
                "booking_number": booking_number,
                "service_name": service_name,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "notification_channels": ["email", "sms"]
            }
        )

    async def publish_booking_reminder(
        self,
        booking_id: UUID,
        booking_number: str,
        site_id: UUID,
        service_name: str,
        provider_name: Optional[str],
        booking_date: str,
        start_time: str,
        customer_email: Optional[str],
        customer_phone: str,
        hours_before: int
    ):
        """
        Publish booking reminder event

        Triggers:
        - Reminder email to customer
        - Reminder SMS to customer
        """
        await self.publish_event(
            event_type="booking.reminder",
            subject=str(booking_id),
            site_id=site_id,
            data={
                "booking_id": str(booking_id),
                "booking_number": booking_number,
                "service_name": service_name,
                "provider_name": provider_name,
                "booking_date": booking_date,
                "start_time": start_time,
                "customer_email": customer_email,
                "customer_phone": customer_phone,
                "hours_before": hours_before,
                "notification_channels": ["email", "sms"]
            }
        )

    async def publish_no_show(
        self,
        booking_id: UUID,
        booking_number: str,
        site_id: UUID,
        customer_phone: str,
        user_id: Optional[UUID] = None
    ):
        """
        Publish no-show event

        Triggers:
        - Provider notification
        - Admin notification
        - Customer follow-up
        """
        await self.publish_event(
            event_type="booking.no_show",
            subject=str(booking_id),
            site_id=site_id,
            user_id=user_id,
            data={
                "booking_id": str(booking_id),
                "booking_number": booking_number,
                "customer_phone": customer_phone,
                "notification_channels": ["dashboard"]
            }
        )


# Global event service instance
event_service = EventService()
