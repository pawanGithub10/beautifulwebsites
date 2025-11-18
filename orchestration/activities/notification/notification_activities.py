"""
Notification Activities

Handles all notification sending via various channels:
- Email notifications
- SMS notifications
- Push notifications
- Webhook calls to n8n for complex notification workflows
"""

import httpx
import os
from typing import Dict, Any
from temporalio import activity


# Service URLs
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://localhost:8003")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "http://localhost:5678/webhook")


@activity.defn
async def send_order_confirmation(notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send order confirmation notification via email and SMS.
    """
    order_id = notification_data["order_id"]
    customer_email = notification_data["customer_email"]
    customer_phone = notification_data.get("customer_phone")

    activity.logger.info(f"Sending order confirmation for {order_id}")

    # Trigger n8n workflow for notification
    try:
        async with httpx.AsyncClient() as client:
            # Call n8n webhook
            response = await client.post(
                f"{N8N_WEBHOOK_URL}/order-confirmation",
                json={
                    "event": "order.confirmed",
                    "order_id": order_id,
                    "customer_email": customer_email,
                    "customer_phone": customer_phone,
                    "order_details": notification_data.get("order_details", {}),
                },
                timeout=30.0
            )

            activity.logger.info(f"Order confirmation sent: {response.status_code}")
            return {"success": True, "notification_sent": True}

    except Exception as e:
        activity.logger.error(f"Failed to send order confirmation: {str(e)}")
        # Don't fail the workflow for notification failures
        return {"success": False, "error": str(e)}


@activity.defn
async def send_dispatch_notification(notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send order dispatch notification with tracking number.
    """
    order_id = notification_data["order_id"]
    tracking_number = notification_data.get("tracking_number")

    activity.logger.info(f"Sending dispatch notification for {order_id}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{N8N_WEBHOOK_URL}/order-dispatched",
                json={
                    "event": "order.dispatched",
                    "order_id": order_id,
                    "customer_email": notification_data["customer_email"],
                    "customer_phone": notification_data.get("customer_phone"),
                    "tracking_number": tracking_number,
                },
                timeout=30.0
            )

            return {"success": True}

    except Exception as e:
        activity.logger.error(f"Failed to send dispatch notification: {str(e)}")
        return {"success": False, "error": str(e)}


@activity.defn
async def send_delivery_confirmation(notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send delivery confirmation notification.
    """
    order_id = notification_data["order_id"]

    activity.logger.info(f"Sending delivery confirmation for {order_id}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{N8N_WEBHOOK_URL}/order-delivered",
                json={
                    "event": "order.delivered",
                    "order_id": order_id,
                    "customer_email": notification_data["customer_email"],
                    "customer_phone": notification_data.get("customer_phone"),
                },
                timeout=30.0
            )

            return {"success": True}

    except Exception as e:
        activity.logger.error(f"Failed to send delivery confirmation: {str(e)}")
        return {"success": False, "error": str(e)}


@activity.defn
async def send_order_cancelled_notification(notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send order cancellation notification.
    """
    order_id = notification_data["order_id"]
    reason = notification_data.get("reason", "Order cancelled")

    activity.logger.info(f"Sending cancellation notification for {order_id}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{N8N_WEBHOOK_URL}/order-cancelled",
                json={
                    "event": "order.cancelled",
                    "order_id": order_id,
                    "customer_email": notification_data["customer_email"],
                    "customer_phone": notification_data.get("customer_phone"),
                    "reason": reason,
                },
                timeout=30.0
            )

            return {"success": True}

    except Exception as e:
        activity.logger.error(f"Failed to send cancellation notification: {str(e)}")
        return {"success": False, "error": str(e)}


@activity.defn
async def send_payment_failed_notification(notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send payment failure notification.
    """
    order_id = notification_data["order_id"]

    activity.logger.info(f"Sending payment failed notification for {order_id}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{N8N_WEBHOOK_URL}/payment-failed",
                json={
                    "event": "payment.failed",
                    "order_id": order_id,
                    "customer_email": notification_data["customer_email"],
                    "customer_phone": notification_data.get("customer_phone"),
                },
                timeout=30.0
            )

            return {"success": True}

    except Exception as e:
        activity.logger.error(f"Failed to send payment failed notification: {str(e)}")
        return {"success": False, "error": str(e)}


# ===== BOOKING NOTIFICATIONS =====

@activity.defn
async def send_booking_confirmation(notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send booking confirmation notification.
    """
    booking_id = notification_data["booking_id"]
    customer_email = notification_data["customer_email"]

    activity.logger.info(f"Sending booking confirmation for {booking_id}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{N8N_WEBHOOK_URL}/booking-confirmed",
                json={
                    "event": "booking.confirmed",
                    "booking_id": booking_id,
                    "customer_email": customer_email,
                    "customer_phone": notification_data.get("customer_phone"),
                    "booking_details": notification_data.get("booking_details", {}),
                },
                timeout=30.0
            )

            return {"success": True}

    except Exception as e:
        activity.logger.error(f"Failed to send booking confirmation: {str(e)}")
        return {"success": False, "error": str(e)}


@activity.defn
async def send_booking_reminder(notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send booking reminder (24h before appointment).
    """
    booking_id = notification_data["booking_id"]

    activity.logger.info(f"Sending booking reminder for {booking_id}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{N8N_WEBHOOK_URL}/booking-reminder",
                json={
                    "event": "booking.reminder",
                    "booking_id": booking_id,
                    "customer_email": notification_data["customer_email"],
                    "customer_phone": notification_data.get("customer_phone"),
                    "booking_time": notification_data.get("booking_time"),
                },
                timeout=30.0
            )

            return {"success": True}

    except Exception as e:
        activity.logger.error(f"Failed to send booking reminder: {str(e)}")
        return {"success": False, "error": str(e)}


@activity.defn
async def send_booking_cancelled_notification(notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send booking cancellation notification.
    """
    booking_id = notification_data["booking_id"]

    activity.logger.info(f"Sending booking cancellation notification for {booking_id}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{N8N_WEBHOOK_URL}/booking-cancelled",
                json={
                    "event": "booking.cancelled",
                    "booking_id": booking_id,
                    "customer_email": notification_data["customer_email"],
                    "customer_phone": notification_data.get("customer_phone"),
                    "reason": notification_data.get("reason", "Booking cancelled"),
                },
                timeout=30.0
            )

            return {"success": True}

    except Exception as e:
        activity.logger.error(f"Failed to send booking cancellation: {str(e)}")
        return {"success": False, "error": str(e)}


@activity.defn
async def send_booking_completed_notification(notification_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send booking completion notification.
    """
    booking_id = notification_data["booking_id"]

    activity.logger.info(f"Sending booking completion notification for {booking_id}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{N8N_WEBHOOK_URL}/booking-completed",
                json={
                    "event": "booking.completed",
                    "booking_id": booking_id,
                    "customer_email": notification_data["customer_email"],
                    "customer_phone": notification_data.get("customer_phone"),
                },
                timeout=30.0
            )

            return {"success": True}

    except Exception as e:
        activity.logger.error(f"Failed to send booking completion: {str(e)}")
        return {"success": False, "error": str(e)}
