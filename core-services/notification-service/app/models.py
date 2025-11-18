"""
Database models for Notification Service
"""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
import uuid
import enum

Base = declarative_base()


class NotificationType(str, enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"


class NotificationStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    BOUNCED = "bounced"
    OPENED = "opened"
    CLICKED = "clicked"


class NotificationPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Notification(Base):
    """
    Main notification records
    """
    __tablename__ = "notifications"

    notification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Recipient
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    recipient_email = Column(String(255), nullable=True)
    recipient_phone = Column(String(20), nullable=True)
    recipient_device_token = Column(String(500), nullable=True)

    # Notification details
    notification_type = Column(SQLEnum(NotificationType), nullable=False, index=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("notification_templates.template_id"), nullable=True)

    # Content
    subject = Column(String(500), nullable=True)  # For email
    body = Column(Text, nullable=False)
    html_body = Column(Text, nullable=True)  # For email
    data = Column(JSONB, default=dict)  # Additional data

    # Status tracking
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING, index=True)
    priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL)

    # Delivery tracking
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    failure_reason = Column(Text, nullable=True)

    # Provider details
    provider = Column(String(50), nullable=True)  # smtp, twilio, firebase, etc.
    provider_message_id = Column(String(500), nullable=True)
    provider_response = Column(JSONB, nullable=True)

    # Retry logic
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    next_retry_at = Column(DateTime, nullable=True)

    # Scheduling
    scheduled_for = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    # Metadata
    tags = Column(JSONB, default=list)
    metadata = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationTemplate(Base):
    """
    Reusable notification templates
    """
    __tablename__ = "notification_templates"

    template_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Template identification
    template_key = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)

    # Template type
    notification_type = Column(SQLEnum(NotificationType), nullable=False)

    # Content templates
    subject_template = Column(String(500), nullable=True)  # For email
    body_template = Column(Text, nullable=False)
    html_template = Column(Text, nullable=True)  # For email

    # Template variables
    variables = Column(JSONB, default=list)  # List of required variables

    # Settings
    is_active = Column(Boolean, default=True)
    default_priority = Column(SQLEnum(NotificationPriority), default=NotificationPriority.NORMAL)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationPreference(Base):
    """
    User notification preferences
    """
    __tablename__ = "notification_preferences"

    preference_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, unique=True, index=True)

    # Channel preferences
    email_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)

    # Category preferences
    marketing_enabled = Column(Boolean, default=True)
    transactional_enabled = Column(Boolean, default=True)
    security_enabled = Column(Boolean, default=True)

    # Frequency settings
    digest_frequency = Column(String(20), default="immediate")  # immediate, hourly, daily, weekly
    quiet_hours_start = Column(String(5), nullable=True)  # HH:MM format
    quiet_hours_end = Column(String(5), nullable=True)

    # Contact details
    preferred_email = Column(String(255), nullable=True)
    preferred_phone = Column(String(20), nullable=True)

    # Custom preferences
    custom_settings = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationBatch(Base):
    """
    Batch notification jobs
    """
    __tablename__ = "notification_batches"

    batch_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Batch details
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    template_id = Column(UUID(as_uuid=True), ForeignKey("notification_templates.template_id"))

    # Target
    recipient_count = Column(Integer, default=0)
    recipient_filters = Column(JSONB, default=dict)

    # Status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed

    # Progress
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)

    # Scheduling
    scheduled_for = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NotificationEvent(Base):
    """
    Track notification events (opens, clicks, etc.)
    """
    __tablename__ = "notification_events"

    event_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    notification_id = Column(UUID(as_uuid=True), ForeignKey("notifications.notification_id"), index=True)

    # Event details
    event_type = Column(String(50), nullable=False)  # opened, clicked, unsubscribed, etc.
    event_data = Column(JSONB, default=dict)

    # Tracking
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class NotificationProvider(Base):
    """
    Notification provider configurations
    """
    __tablename__ = "notification_providers"

    provider_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Provider details
    provider_type = Column(String(50), nullable=False)  # smtp, twilio, firebase, sendgrid, etc.
    provider_name = Column(String(100), nullable=False)

    # Configuration
    config = Column(JSONB, nullable=False)  # API keys, endpoints, etc.

    # Usage
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    priority = Column(Integer, default=0)

    # Rate limiting
    rate_limit_per_minute = Column(Integer, nullable=True)
    rate_limit_per_hour = Column(Integer, nullable=True)
    rate_limit_per_day = Column(Integer, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
