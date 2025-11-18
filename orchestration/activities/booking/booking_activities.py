"""
Booking Activities

Activities for booking lifecycle management.
"""

import httpx
import os
from typing import Dict, Any
from temporalio import activity


# Service URLs
BOOKING_SERVICE_URL = os.getenv("BOOKING_SERVICE_URL", "http://localhost:8012")


@activity.defn
async def mark_completed(booking_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update booking status to 'completed'.
    """
    booking_id = booking_info["booking_id"]
    site_id = booking_info["site_id"]

    activity.logger.info(f"Marking booking {booking_id} as completed")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{BOOKING_SERVICE_URL}/api/v1/{site_id}/bookings/{booking_id}/status",
                json={"booking_status": "completed"}
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        activity.logger.error(f"Failed to mark booking as completed: {str(e)}")
        raise


@activity.defn
async def mark_no_show(booking_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update booking status to 'no_show'.
    """
    booking_id = booking_info["booking_id"]
    site_id = booking_info["site_id"]

    activity.logger.info(f"Marking booking {booking_id} as no-show")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{BOOKING_SERVICE_URL}/api/v1/{site_id}/bookings/{booking_id}/status",
                json={"booking_status": "no_show"}
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        activity.logger.error(f"Failed to mark booking as no-show: {str(e)}")
        raise


@activity.defn
async def cancel_booking(cancellation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cancel the booking.
    """
    booking_id = cancellation_data["booking_id"]
    site_id = cancellation_data["site_id"]
    reason = cancellation_data.get("reason", "Cancelled by system")

    activity.logger.info(f"Cancelling booking {booking_id}: {reason}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BOOKING_SERVICE_URL}/api/v1/{site_id}/bookings/{booking_id}/cancel",
                json={"reason": reason}
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        activity.logger.error(f"Failed to cancel booking: {str(e)}")
        raise
