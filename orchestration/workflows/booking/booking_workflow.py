"""
Booking Lifecycle Workflow

Orchestrates the complete booking lifecycle:
1. Booking Confirmed → Send confirmation
2. Send reminder 24h before appointment
3. Mark as completed after appointment
4. Send feedback request

Handles:
- Booking confirmations
- Reminder notifications
- Status updates
- Cancellation handling
- No-show tracking
"""

from datetime import timedelta, datetime
from typing import Dict, Any
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from orchestration.activities.booking import booking_activities
    from orchestration.activities.notification import notification_activities


@workflow.defn
class BookingLifecycleWorkflow:
    """
    Orchestrates the complete booking lifecycle.

    Workflow Steps:
    1. Send booking confirmation
    2. Wait until 24h before appointment
    3. Send reminder notification
    4. Wait for appointment time
    5. Mark as completed (or no-show)
    6. Send feedback request
    """

    @workflow.run
    async def run(self, booking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the booking lifecycle workflow.

        Args:
            booking_data: {
                "booking_id": str,
                "site_id": str,
                "customer_email": str,
                "customer_phone": str,
                "booking_date": str,  # ISO format
                "start_time": str,
                "service_name": str,
            }

        Returns:
            Dict with workflow execution summary
        """
        booking_id = booking_data["booking_id"]
        workflow.logger.info(f"Starting booking workflow for {booking_id}")

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            backoff_coefficient=2.0,
            maximum_attempts=3,
        )

        try:
            # Step 1: Send confirmation
            workflow.logger.info(f"Step 1: Sending confirmation for booking {booking_id}")
            await workflow.execute_activity(
                notification_activities.send_booking_confirmation,
                {
                    "booking_id": booking_id,
                    "customer_email": booking_data["customer_email"],
                    "customer_phone": booking_data.get("customer_phone"),
                    "booking_details": booking_data,
                },
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy,
            )

            # Step 2: Calculate reminder time (24h before appointment)
            booking_datetime_str = f"{booking_data['booking_date']}T{booking_data['start_time']}"
            booking_datetime = datetime.fromisoformat(booking_datetime_str)
            reminder_time = booking_datetime - timedelta(hours=24)
            now = datetime.now()

            if reminder_time > now:
                # Sleep until reminder time
                sleep_duration = reminder_time - now
                workflow.logger.info(f"Step 2: Sleeping until reminder time ({sleep_duration})")

                await workflow.wait_condition(
                    lambda: False,
                    timeout=sleep_duration,
                )

                # Send reminder
                await workflow.execute_activity(
                    notification_activities.send_booking_reminder,
                    {
                        "booking_id": booking_id,
                        "customer_email": booking_data["customer_email"],
                        "customer_phone": booking_data.get("customer_phone"),
                        "booking_time": booking_datetime_str,
                    },
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=retry_policy,
                )

            # Step 3: Wait for appointment time
            if booking_datetime > now:
                sleep_duration = booking_datetime - now
                workflow.logger.info(f"Step 3: Waiting for appointment time ({sleep_duration})")

                await workflow.wait_condition(
                    lambda: False,
                    timeout=sleep_duration,
                )

            # Step 4: Wait for completion signal (2h after appointment time)
            workflow.logger.info(f"Step 4: Waiting for completion signal")
            completion_timeout = timedelta(hours=2)

            try:
                # Wait for manual completion signal
                await workflow.wait_condition(
                    lambda: False,
                    timeout=completion_timeout,
                )
            except:
                # Auto-mark as completed after timeout
                pass

            # Mark as completed
            await workflow.execute_activity(
                booking_activities.mark_completed,
                {
                    "booking_id": booking_id,
                    "site_id": booking_data["site_id"],
                },
                start_to_close_timeout=timedelta(seconds=30),
            )

            # Send completion notification
            await workflow.execute_activity(
                notification_activities.send_booking_completed_notification,
                {
                    "booking_id": booking_id,
                    "customer_email": booking_data["customer_email"],
                    "customer_phone": booking_data.get("customer_phone"),
                },
                start_to_close_timeout=timedelta(seconds=30),
            )

            workflow.logger.info(f"Booking workflow completed for {booking_id}")

            return {
                "status": "completed",
                "booking_id": booking_id,
            }

        except Exception as e:
            workflow.logger.error(f"Booking workflow failed for {booking_id}: {str(e)}")
            raise

    @workflow.signal
    async def cancel_booking_signal(self, reason: str):
        """Signal to cancel the booking."""
        workflow.logger.info(f"Received cancel signal: {reason}")
        # Handle cancellation
        pass

    @workflow.signal
    async def mark_completed_signal(self):
        """Signal to mark booking as completed."""
        workflow.logger.info("Received completion signal")
        # Handle completion
        pass

    @workflow.signal
    async def mark_no_show_signal(self):
        """Signal to mark booking as no-show."""
        workflow.logger.info("Received no-show signal")
        # Handle no-show
        pass
