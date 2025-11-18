"""
Notification API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas import (
    NotificationCreate, NotificationResponse,
    NotificationTemplateCreate, NotificationTemplateResponse,
    NotificationPreferenceUpdate, NotificationPreferenceResponse,
    EmailNotification, SMSNotification, PushNotification
)
from app.services.notification_service import NotificationService
from app.models import NotificationType

router = APIRouter()


@router.post("/send", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def send_notification(
    notification_data: NotificationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a notification

    Supports multiple channels:
    - Email (requires recipient_email)
    - SMS (requires recipient_phone)
    - Push (requires device_token in metadata)
    - In-app (requires user_id)
    """
    notification_service = NotificationService(db)
    notification = await notification_service.send_notification(notification_data)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to send notification (possibly blocked by user preferences)"
        )

    return notification


@router.post("/send/email", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def send_email_notification(
    email_data: EmailNotification,
    user_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Send an email notification
    """
    notification_data = NotificationCreate(
        notification_type=NotificationType.EMAIL,
        recipient_email=email_data.to,
        subject=email_data.subject,
        body=email_data.body,
        html_body=email_data.html,
        metadata={
            "from_email": email_data.from_email,
            "cc": email_data.cc,
            "attachments": email_data.attachments
        } if (email_data.from_email or email_data.cc or email_data.attachments) else None
    )

    notification_service = NotificationService(db)
    notification = await notification_service.send_notification(notification_data, user_id)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to send email"
        )

    return notification


@router.post("/send/sms", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def send_sms_notification(
    sms_data: SMSNotification,
    user_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Send an SMS notification
    """
    notification_data = NotificationCreate(
        notification_type=NotificationType.SMS,
        recipient_phone=sms_data.to,
        body=sms_data.body,
        metadata={
            "from_number": sms_data.from_number
        } if sms_data.from_number else None
    )

    notification_service = NotificationService(db)
    notification = await notification_service.send_notification(notification_data, user_id)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to send SMS"
        )

    return notification


@router.post("/send/push", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def send_push_notification(
    push_data: PushNotification,
    user_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a push notification
    """
    notification_data = NotificationCreate(
        notification_type=NotificationType.PUSH,
        subject=push_data.title,
        body=push_data.body,
        metadata={
            "device_token": push_data.device_token,
            "data": push_data.data
        }
    )

    notification_service = NotificationService(db)
    notification = await notification_service.send_notification(notification_data, user_id)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to send push notification"
        )

    return notification


@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get notification status by ID
    """
    notification_service = NotificationService(db)
    notification = await notification_service.get_notification_status(notification_id)

    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return notification


@router.get("/user/{user_id}", response_model=List[NotificationResponse])
async def get_user_notifications(
    user_id: UUID,
    notification_type: Optional[NotificationType] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Get notifications for a specific user
    """
    notification_service = NotificationService(db)
    notifications = await notification_service.get_user_notifications(
        user_id=user_id,
        notification_type=notification_type,
        limit=limit,
        offset=offset
    )

    return notifications


@router.post("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Mark an in-app notification as read
    """
    notification_service = NotificationService(db)
    success = await notification_service.mark_as_read(notification_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )

    return None


@router.post("/retry-failed", status_code=status.HTTP_200_OK)
async def retry_failed_notifications(
    max_retries: int = Query(3, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """
    Retry all failed notifications

    This endpoint can be called periodically by a scheduler
    to retry failed notifications.
    """
    notification_service = NotificationService(db)
    retried_count = await notification_service.retry_failed_notifications(max_retries)

    return {
        "message": f"Retried {retried_count} failed notifications",
        "retried_count": retried_count
    }


# Template Management Endpoints

@router.post("/templates", response_model=NotificationTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: NotificationTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a notification template

    Templates use Jinja2 syntax for variable substitution:
    Example: "Hello {{ user_name }}, your order {{ order_id }} is ready!"
    """
    notification_service = NotificationService(db)

    try:
        template = await notification_service.create_template(
            template_key=template_data.template_key,
            subject_template=template_data.subject_template,
            body_template=template_data.body_template,
            html_template=template_data.html_template,
            variables=template_data.variables
        )

        return NotificationTemplateResponse.from_orm(template)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create template: {str(e)}"
        )


# User Preference Endpoints

@router.get("/preferences/{user_id}", response_model=NotificationPreferenceResponse)
async def get_user_preferences(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's notification preferences
    """
    notification_service = NotificationService(db)
    preferences = await notification_service._get_user_preferences(user_id)

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User preferences not found"
        )

    return NotificationPreferenceResponse.from_orm(preferences)


@router.put("/preferences/{user_id}", response_model=NotificationPreferenceResponse)
async def update_user_preferences(
    user_id: UUID,
    preference_data: NotificationPreferenceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update user's notification preferences

    Controls:
    - Which notification channels are enabled (email, SMS, push)
    - Marketing notifications opt-in/out
    - Quiet hours (notifications won't be sent during this time)
    - Digest frequency
    """
    notification_service = NotificationService(db)

    try:
        preferences = await notification_service.update_user_preferences(
            user_id=user_id,
            email_enabled=preference_data.email_enabled,
            sms_enabled=preference_data.sms_enabled,
            push_enabled=preference_data.push_enabled,
            marketing_enabled=preference_data.marketing_enabled,
            quiet_hours_start=preference_data.quiet_hours_start,
            quiet_hours_end=preference_data.quiet_hours_end
        )

        return NotificationPreferenceResponse.from_orm(preferences)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update preferences: {str(e)}"
        )
