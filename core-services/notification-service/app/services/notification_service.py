"""
Main notification service - orchestrates all notification channels
"""

from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from jinja2 import Environment, FileSystemLoader, Template

from app.models import (
    Notification, NotificationTemplate, NotificationPreference,
    NotificationBatch, NotificationType, NotificationStatus,
    NotificationPriority
)
from app.schemas import NotificationCreate, NotificationResponse
from app.services.email_service import EmailService
from app.services.sms_service import SMSService
from app.services.push_service import PushNotificationService
from app.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Main notification service that orchestrates all notification channels
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.email_service = EmailService()
        self.sms_service = SMSService()
        self.push_service = PushNotificationService()

    async def send_notification(
        self,
        notification_data: NotificationCreate,
        user_id: Optional[UUID] = None
    ) -> NotificationResponse:
        """
        Send a notification through the appropriate channel

        Args:
            notification_data: Notification data
            user_id: Optional user ID

        Returns:
            NotificationResponse with status
        """
        # Check user preferences if user_id provided
        if user_id:
            preferences = await self._get_user_preferences(user_id)
            if not self._should_send(notification_data.notification_type, preferences):
                logger.info(f"Notification skipped due to user preferences: {user_id}")
                return None

        # Render template if template_id provided
        subject, body, html_body = await self._render_template(
            notification_data.template_id,
            notification_data.template_variables or {}
        ) if notification_data.template_id else (
            notification_data.subject,
            notification_data.body,
            notification_data.html_body
        )

        # Create notification record
        notification = Notification(
            user_id=user_id,
            recipient_email=notification_data.recipient_email,
            recipient_phone=notification_data.recipient_phone,
            notification_type=notification_data.notification_type,
            subject=subject,
            body=body,
            html_body=html_body,
            status=NotificationStatus.PENDING,
            priority=notification_data.priority or NotificationPriority.NORMAL,
            metadata=notification_data.metadata
        )

        self.db.add(notification)
        await self.db.commit()
        await self.db.refresh(notification)

        # Send through appropriate channel
        try:
            success = await self._send_via_channel(notification)

            if success:
                notification.status = NotificationStatus.SENT
                notification.sent_at = datetime.utcnow()
            else:
                notification.status = NotificationStatus.FAILED
                notification.error_message = "Failed to send notification"

            await self.db.commit()
            await self.db.refresh(notification)

            return NotificationResponse.from_orm(notification)

        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            notification.status = NotificationStatus.FAILED
            notification.error_message = str(e)
            await self.db.commit()
            await self.db.refresh(notification)

            return NotificationResponse.from_orm(notification)

    async def _send_via_channel(self, notification: Notification) -> bool:
        """
        Send notification via the appropriate channel

        Args:
            notification: Notification record

        Returns:
            bool: Success status
        """
        if notification.notification_type == NotificationType.EMAIL:
            return await self._send_email(notification)

        elif notification.notification_type == NotificationType.SMS:
            return await self._send_sms(notification)

        elif notification.notification_type == NotificationType.PUSH:
            return await self._send_push(notification)

        elif notification.notification_type == NotificationType.IN_APP:
            # In-app notifications are just stored in DB
            return True

        else:
            logger.error(f"Unknown notification type: {notification.notification_type}")
            return False

    async def _send_email(self, notification: Notification) -> bool:
        """Send email notification"""
        if not notification.recipient_email:
            logger.error(f"No recipient email for notification {notification.notification_id}")
            return False

        success = await self.email_service.send_email(
            to=notification.recipient_email,
            subject=notification.subject or "Notification",
            body=notification.body,
            html=notification.html_body
        )

        return success

    async def _send_sms(self, notification: Notification) -> bool:
        """Send SMS notification"""
        if not notification.recipient_phone:
            logger.error(f"No recipient phone for notification {notification.notification_id}")
            return False

        # Format phone number
        formatted_phone = self.sms_service.format_phone_number(notification.recipient_phone)

        success, message_sid = await self.sms_service.send_sms(
            to=formatted_phone,
            body=notification.body
        )

        if success and message_sid:
            notification.provider_message_id = message_sid

        return success

    async def _send_push(self, notification: Notification) -> bool:
        """Send push notification"""
        # Get device token from metadata
        device_token = notification.metadata.get("device_token") if notification.metadata else None

        if not device_token:
            logger.error(f"No device token for notification {notification.notification_id}")
            return False

        success, message_id = await self.push_service.send_push_notification(
            device_token=device_token,
            title=notification.subject or "Notification",
            body=notification.body,
            data=notification.metadata.get("data") if notification.metadata else None
        )

        if success and message_id:
            notification.provider_message_id = message_id

        return success

    async def _render_template(
        self,
        template_id: UUID,
        variables: Dict[str, Any]
    ) -> tuple[str, str, Optional[str]]:
        """
        Render notification template

        Args:
            template_id: Template ID
            variables: Template variables

        Returns:
            tuple: (subject, body, html_body)
        """
        # Get template
        result = await self.db.execute(
            select(NotificationTemplate).where(
                NotificationTemplate.template_id == template_id
            )
        )
        template = result.scalar_one_or_none()

        if not template:
            logger.error(f"Template not found: {template_id}")
            raise ValueError(f"Template not found: {template_id}")

        # Render subject
        subject = Template(template.subject_template).render(**variables) if template.subject_template else None

        # Render body
        body = Template(template.body_template).render(**variables)

        # Render HTML if available
        html_body = None
        if template.html_template:
            html_body = Template(template.html_template).render(**variables)

        return subject, body, html_body

    async def _get_user_preferences(self, user_id: UUID) -> Optional[NotificationPreference]:
        """Get user notification preferences"""
        result = await self.db.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    def _should_send(
        self,
        notification_type: NotificationType,
        preferences: Optional[NotificationPreference]
    ) -> bool:
        """
        Check if notification should be sent based on user preferences

        Args:
            notification_type: Type of notification
            preferences: User preferences

        Returns:
            bool: Whether to send
        """
        if not preferences:
            return True

        # Check channel preferences
        if notification_type == NotificationType.EMAIL and not preferences.email_enabled:
            return False
        elif notification_type == NotificationType.SMS and not preferences.sms_enabled:
            return False
        elif notification_type == NotificationType.PUSH and not preferences.push_enabled:
            return False

        # Check quiet hours
        if preferences.quiet_hours_start and preferences.quiet_hours_end:
            now = datetime.utcnow().time()
            start = datetime.strptime(preferences.quiet_hours_start, "%H:%M").time()
            end = datetime.strptime(preferences.quiet_hours_end, "%H:%M").time()

            if start <= now <= end:
                return False

        return True

    async def retry_failed_notifications(self, max_retries: int = 3) -> int:
        """
        Retry failed notifications

        Args:
            max_retries: Maximum number of retries

        Returns:
            int: Number of notifications retried
        """
        # Get failed notifications that haven't exceeded max retries
        result = await self.db.execute(
            select(Notification).where(
                Notification.status == NotificationStatus.FAILED,
                Notification.retry_count < max_retries
            )
        )
        failed_notifications = result.scalars().all()

        retried_count = 0

        for notification in failed_notifications:
            try:
                success = await self._send_via_channel(notification)

                notification.retry_count += 1

                if success:
                    notification.status = NotificationStatus.SENT
                    notification.sent_at = datetime.utcnow()
                    retried_count += 1
                    logger.info(f"Successfully retried notification {notification.notification_id}")
                else:
                    logger.warning(f"Retry failed for notification {notification.notification_id}")

            except Exception as e:
                logger.error(f"Error retrying notification {notification.notification_id}: {str(e)}")
                notification.retry_count += 1

        await self.db.commit()

        logger.info(f"Retried {retried_count} out of {len(failed_notifications)} failed notifications")
        return retried_count

    async def get_notification_status(self, notification_id: UUID) -> Optional[NotificationResponse]:
        """
        Get notification status

        Args:
            notification_id: Notification ID

        Returns:
            NotificationResponse or None
        """
        result = await self.db.execute(
            select(Notification).where(
                Notification.notification_id == notification_id
            )
        )
        notification = result.scalar_one_or_none()

        if not notification:
            return None

        return NotificationResponse.from_orm(notification)

    async def get_user_notifications(
        self,
        user_id: UUID,
        notification_type: Optional[NotificationType] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[NotificationResponse]:
        """
        Get user's notifications

        Args:
            user_id: User ID
            notification_type: Optional filter by type
            limit: Number of results
            offset: Pagination offset

        Returns:
            List of notifications
        """
        query = select(Notification).where(
            Notification.user_id == user_id
        )

        if notification_type:
            query = query.where(Notification.notification_type == notification_type)

        query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)

        result = await self.db.execute(query)
        notifications = result.scalars().all()

        return [NotificationResponse.from_orm(n) for n in notifications]

    async def mark_as_read(self, notification_id: UUID) -> bool:
        """
        Mark notification as read (for in-app notifications)

        Args:
            notification_id: Notification ID

        Returns:
            bool: Success status
        """
        result = await self.db.execute(
            update(Notification)
            .where(Notification.notification_id == notification_id)
            .values(read_at=datetime.utcnow())
        )

        await self.db.commit()

        return result.rowcount > 0

    async def create_template(
        self,
        template_key: str,
        subject_template: Optional[str],
        body_template: str,
        html_template: Optional[str] = None,
        variables: Optional[List[str]] = None
    ) -> NotificationTemplate:
        """
        Create a notification template

        Args:
            template_key: Unique template key
            subject_template: Subject template (Jinja2)
            body_template: Body template (Jinja2)
            html_template: Optional HTML template
            variables: List of required variables

        Returns:
            Created template
        """
        template = NotificationTemplate(
            template_key=template_key,
            subject_template=subject_template,
            body_template=body_template,
            html_template=html_template,
            variables=variables or []
        )

        self.db.add(template)
        await self.db.commit()
        await self.db.refresh(template)

        return template

    async def update_user_preferences(
        self,
        user_id: UUID,
        email_enabled: Optional[bool] = None,
        sms_enabled: Optional[bool] = None,
        push_enabled: Optional[bool] = None,
        marketing_enabled: Optional[bool] = None,
        quiet_hours_start: Optional[str] = None,
        quiet_hours_end: Optional[str] = None
    ) -> NotificationPreference:
        """
        Update user notification preferences

        Args:
            user_id: User ID
            email_enabled: Enable email notifications
            sms_enabled: Enable SMS notifications
            push_enabled: Enable push notifications
            marketing_enabled: Enable marketing notifications
            quiet_hours_start: Quiet hours start (HH:MM)
            quiet_hours_end: Quiet hours end (HH:MM)

        Returns:
            Updated preferences
        """
        # Get or create preferences
        result = await self.db.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id
            )
        )
        preferences = result.scalar_one_or_none()

        if not preferences:
            preferences = NotificationPreference(user_id=user_id)
            self.db.add(preferences)

        # Update fields
        if email_enabled is not None:
            preferences.email_enabled = email_enabled
        if sms_enabled is not None:
            preferences.sms_enabled = sms_enabled
        if push_enabled is not None:
            preferences.push_enabled = push_enabled
        if marketing_enabled is not None:
            preferences.marketing_enabled = marketing_enabled
        if quiet_hours_start is not None:
            preferences.quiet_hours_start = quiet_hours_start
        if quiet_hours_end is not None:
            preferences.quiet_hours_end = quiet_hours_end

        await self.db.commit()
        await self.db.refresh(preferences)

        return preferences
