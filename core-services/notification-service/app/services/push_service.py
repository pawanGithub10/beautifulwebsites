"""
Push notification service using Firebase Cloud Messaging (FCM)
"""

from typing import Optional, Dict, Any, List
import logging
from firebase_admin import messaging, credentials, initialize_app
import firebase_admin

from app.config import settings

logger = logging.getLogger(__name__)


class PushNotificationService:
    """
    Push notification service using Firebase Cloud Messaging
    """

    def __init__(self):
        if settings.FIREBASE_CREDENTIALS_PATH:
            try:
                # Initialize Firebase Admin SDK
                if not firebase_admin._apps:
                    cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
                    initialize_app(cred)
                self.enabled = True
                logger.info("Firebase Cloud Messaging initialized successfully")
            except Exception as e:
                self.enabled = False
                logger.error(f"Failed to initialize Firebase: {str(e)}")
        else:
            self.enabled = False
            logger.warning("Firebase credentials not configured. Push notifications disabled.")

    async def send_push_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None,
        badge: Optional[int] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Send a push notification to a single device

        Args:
            device_token: FCM device token
            title: Notification title
            body: Notification body
            data: Optional custom data payload
            image_url: Optional image URL for rich notifications
            badge: Optional badge count for iOS

        Returns:
            tuple: (success: bool, message_id: Optional[str])
        """
        if not self.enabled:
            logger.error("Push notification service is not enabled")
            return False, None

        try:
            # Build notification payload
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image_url
            )

            # Build Android config
            android_config = messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    sound='default',
                    color='#4CAF50'
                )
            )

            # Build iOS config
            apns_config = messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        badge=badge,
                        sound='default',
                        content_available=True
                    )
                )
            )

            # Create message
            message = messaging.Message(
                notification=notification,
                data=data or {},
                token=device_token,
                android=android_config,
                apns=apns_config
            )

            # Send the message
            response = messaging.send(message)

            logger.info(f"Push notification sent successfully. Message ID: {response}")
            return True, response

        except messaging.UnregisteredError:
            logger.warning(f"Device token is invalid or unregistered: {device_token}")
            return False, None

        except messaging.SenderIdMismatchError:
            logger.error(f"Sender ID mismatch for token: {device_token}")
            return False, None

        except Exception as e:
            logger.error(f"Failed to send push notification: {str(e)}")
            return False, None

    async def send_multicast_notification(
        self,
        device_tokens: List[str],
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None,
        image_url: Optional[str] = None
    ) -> tuple[int, int]:
        """
        Send push notification to multiple devices

        Args:
            device_tokens: List of FCM device tokens
            title: Notification title
            body: Notification body
            data: Optional custom data payload
            image_url: Optional image URL

        Returns:
            tuple: (success_count: int, failure_count: int)
        """
        if not self.enabled:
            logger.error("Push notification service is not enabled")
            return 0, len(device_tokens)

        try:
            # Build notification
            notification = messaging.Notification(
                title=title,
                body=body,
                image=image_url
            )

            # Create multicast message
            message = messaging.MulticastMessage(
                notification=notification,
                data=data or {},
                tokens=device_tokens
            )

            # Send to multiple devices
            response = messaging.send_multicast(message)

            logger.info(
                f"Push notifications sent: {response.success_count} succeeded, "
                f"{response.failure_count} failed out of {len(device_tokens)}"
            )

            # Log individual failures
            if response.failure_count > 0:
                for idx, result in enumerate(response.responses):
                    if not result.success:
                        logger.error(
                            f"Failed to send to token {device_tokens[idx]}: "
                            f"{result.exception}"
                        )

            return response.success_count, response.failure_count

        except Exception as e:
            logger.error(f"Failed to send multicast notification: {str(e)}")
            return 0, len(device_tokens)

    async def send_topic_notification(
        self,
        topic: str,
        title: str,
        body: str,
        data: Optional[Dict[str, str]] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Send notification to all devices subscribed to a topic

        Args:
            topic: Topic name (e.g., 'news', 'promotions')
            title: Notification title
            body: Notification body
            data: Optional custom data

        Returns:
            tuple: (success: bool, message_id: Optional[str])
        """
        if not self.enabled:
            logger.error("Push notification service is not enabled")
            return False, None

        try:
            # Build notification
            notification = messaging.Notification(
                title=title,
                body=body
            )

            # Create topic message
            message = messaging.Message(
                notification=notification,
                data=data or {},
                topic=topic
            )

            # Send to topic
            response = messaging.send(message)

            logger.info(f"Topic notification sent to '{topic}'. Message ID: {response}")
            return True, response

        except Exception as e:
            logger.error(f"Failed to send topic notification: {str(e)}")
            return False, None

    async def subscribe_to_topic(
        self,
        device_tokens: List[str],
        topic: str
    ) -> tuple[int, int]:
        """
        Subscribe devices to a topic

        Args:
            device_tokens: List of device tokens
            topic: Topic name

        Returns:
            tuple: (success_count: int, failure_count: int)
        """
        if not self.enabled:
            logger.error("Push notification service is not enabled")
            return 0, len(device_tokens)

        try:
            response = messaging.subscribe_to_topic(device_tokens, topic)

            logger.info(
                f"Topic subscription '{topic}': {response.success_count} succeeded, "
                f"{response.failure_count} failed"
            )

            return response.success_count, response.failure_count

        except Exception as e:
            logger.error(f"Failed to subscribe to topic: {str(e)}")
            return 0, len(device_tokens)

    async def unsubscribe_from_topic(
        self,
        device_tokens: List[str],
        topic: str
    ) -> tuple[int, int]:
        """
        Unsubscribe devices from a topic

        Args:
            device_tokens: List of device tokens
            topic: Topic name

        Returns:
            tuple: (success_count: int, failure_count: int)
        """
        if not self.enabled:
            logger.error("Push notification service is not enabled")
            return 0, len(device_tokens)

        try:
            response = messaging.unsubscribe_from_topic(device_tokens, topic)

            logger.info(
                f"Topic unsubscription '{topic}': {response.success_count} succeeded, "
                f"{response.failure_count} failed"
            )

            return response.success_count, response.failure_count

        except Exception as e:
            logger.error(f"Failed to unsubscribe from topic: {str(e)}")
            return 0, len(device_tokens)
