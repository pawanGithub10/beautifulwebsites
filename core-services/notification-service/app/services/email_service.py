"""
Email notification service
"""

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import Optional, List, Dict
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email sending service using SMTP
    """

    def __init__(self):
        self.host = settings.SMTP_HOST
        self.port = settings.SMTP_PORT
        self.username = settings.SMTP_USER
        self.password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.from_name = settings.SMTP_FROM_NAME
        self.use_tls = settings.SMTP_USE_TLS

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, str]]] = None
    ) -> bool:
        """
        Send an email

        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text body
            html: Optional HTML body
            from_email: Optional sender email (defaults to config)
            from_name: Optional sender name (defaults to config)
            reply_to: Optional reply-to address
            cc: Optional list of CC addresses
            bcc: Optional list of BCC addresses
            attachments: Optional list of attachments

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = f"{from_name or self.from_name} <{from_email or self.from_email}>"
            message["To"] = to
            message["Subject"] = subject

            if reply_to:
                message["Reply-To"] = reply_to

            if cc:
                message["Cc"] = ", ".join(cc)

            # Add plain text body
            text_part = MIMEText(body, "plain")
            message.attach(text_part)

            # Add HTML body if provided
            if html:
                html_part = MIMEText(html, "html")
                message.attach(html_part)

            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.get("content", ""))
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {attachment.get('filename', 'file')}"
                    )
                    message.attach(part)

            # Build recipient list
            recipients = [to]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                use_tls=self.use_tls,
            )

            logger.info(f"Email sent successfully to {to}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to}: {str(e)}")
            return False

    async def send_template_email(
        self,
        to: str,
        template_name: str,
        context: Dict,
        subject: str
    ) -> bool:
        """
        Send email using a Jinja2 template

        Args:
            to: Recipient email
            template_name: Template file name
            context: Template variables
            subject: Email subject

        Returns:
            bool: Success status
        """
        from jinja2 import Environment, FileSystemLoader

        try:
            # Load template
            env = Environment(loader=FileSystemLoader(settings.TEMPLATE_DIR))

            # Render text template
            text_template = env.get_template(f"{template_name}.txt")
            body = text_template.render(**context)

            # Render HTML template if exists
            html = None
            try:
                html_template = env.get_template(f"{template_name}.html")
                html = html_template.render(**context)
            except:
                pass

            # Send email
            return await self.send_email(
                to=to,
                subject=subject,
                body=body,
                html=html
            )

        except Exception as e:
            logger.error(f"Failed to send template email: {str(e)}")
            return False
