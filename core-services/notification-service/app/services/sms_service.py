"""
SMS notification service using Twilio
"""

from typing import Optional
import logging
from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioRestException

from app.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """
    SMS sending service using Twilio
    """

    def __init__(self):
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = TwilioClient(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.from_number = settings.TWILIO_FROM_NUMBER
            self.enabled = True
        else:
            self.client = None
            self.enabled = False
            logger.warning("Twilio credentials not configured. SMS service disabled.")

    async def send_sms(
        self,
        to: str,
        body: str,
        from_number: Optional[str] = None
    ) -> tuple[bool, Optional[str]]:
        """
        Send an SMS message

        Args:
            to: Recipient phone number (E.164 format)
            body: Message body
            from_number: Optional sender number (defaults to config)

        Returns:
            tuple: (success: bool, message_sid: Optional[str])
        """
        if not self.enabled:
            logger.error("SMS service is not enabled")
            return False, None

        try:
            message = self.client.messages.create(
                body=body,
                from_=from_number or self.from_number,
                to=to
            )

            logger.info(f"SMS sent successfully to {to}. SID: {message.sid}")
            return True, message.sid

        except TwilioRestException as e:
            logger.error(f"Twilio error sending SMS to {to}: {e.msg}")
            return False, None

        except Exception as e:
            logger.error(f"Failed to send SMS to {to}: {str(e)}")
            return False, None

    def format_phone_number(self, phone: str, default_country_code: str = "+1") -> str:
        """
        Format phone number to E.164 format

        Args:
            phone: Phone number
            default_country_code: Default country code if not provided

        Returns:
            str: Formatted phone number
        """
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, phone))

        # Add country code if not present
        if not phone.startswith('+'):
            return f"{default_country_code}{digits}"

        return f"+{digits}"
