"""
Pydantic schemas for Notification Service
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from app.models import NotificationType, NotificationStatus, NotificationPriority


# ===== NOTIFICATION SCHEMAS =====

class NotificationBase(BaseModel):
    user_id: Optional[UUID] = None
    recipient_email: Optional[EmailStr] = None
    recipient_phone: Optional[str] = None
    notification_type: NotificationType
    subject: Optional[str] = None
    body: str
    html_body: Optional[str] = None
    data: Dict[str, Any] = {}
    priority: NotificationPriority = NotificationPriority.NORMAL
    scheduled_for: Optional[datetime] = None
    tags: List[str] = []


class NotificationCreate(NotificationBase):
    template_id: Optional[UUID] = None
    template_variables: Optional[Dict[str, Any]] = None


class NotificationResponse(NotificationBase):
    notification_id: UUID
    status: NotificationStatus
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    failed_at: Optional[datetime]
    failure_reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ===== TEMPLATE SCHEMAS =====

class TemplateBase(BaseModel):
    template_key: str
    name: str
    description: Optional[str] = None
    notification_type: NotificationType
    subject_template: Optional[str] = None
    body_template: str
    html_template: Optional[str] = None
    variables: List[str] = []
    default_priority: NotificationPriority = NotificationPriority.NORMAL


class TemplateCreate(TemplateBase):
    pass


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    subject_template: Optional[str] = None
    body_template: Optional[str] = None
    html_template: Optional[str] = None
    variables: Optional[List[str]] = None
    is_active: Optional[bool] = None


class TemplateResponse(TemplateBase):
    template_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== PREFERENCE SCHEMAS =====

class PreferenceBase(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = True
    push_enabled: bool = True
    in_app_enabled: bool = True
    marketing_enabled: bool = True
    transactional_enabled: bool = True
    security_enabled: bool = True
    digest_frequency: str = "immediate"
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


class PreferenceUpdate(PreferenceBase):
    preferred_email: Optional[EmailStr] = None
    preferred_phone: Optional[str] = None


class PreferenceResponse(PreferenceBase):
    preference_id: UUID
    user_id: UUID
    preferred_email: Optional[str]
    preferred_phone: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ===== BATCH SCHEMAS =====

class BatchCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template_id: UUID
    recipient_filters: Dict[str, Any]
    scheduled_for: Optional[datetime] = None


class BatchResponse(BaseModel):
    batch_id: UUID
    name: str
    template_id: UUID
    recipient_count: int
    sent_count: int
    delivered_count: int
    failed_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ===== EMAIL SCHEMAS =====

class EmailNotification(BaseModel):
    to: EmailStr
    subject: str
    body: str
    html: Optional[str] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None
    reply_to: Optional[EmailStr] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    attachments: Optional[List[Dict[str, str]]] = None


# ===== SMS SCHEMAS =====

class SMSNotification(BaseModel):
    to: str
    body: str
    from_number: Optional[str] = None


# ===== PUSH SCHEMAS =====

class PushNotification(BaseModel):
    device_token: str
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    badge: Optional[int] = None
    sound: Optional[str] = None


# ===== WEBHOOK SCHEMAS =====

class WebhookEvent(BaseModel):
    event_type: str
    notification_id: UUID
    status: str
    timestamp: datetime
    data: Dict[str, Any] = {}
