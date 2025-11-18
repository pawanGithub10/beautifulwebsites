"""
Temporal Worker

Runs workflows and activities for order and booking processes.
"""

import asyncio
import logging
from temporalio.client import Client
from temporalio.worker import Worker

# Import workflows
from orchestration.workflows.order.order_workflow import OrderProcessingWorkflow
from orchestration.workflows.booking.booking_workflow import BookingLifecycleWorkflow

# Import activities
from orchestration.activities.order import order_activities
from orchestration.activities.booking import booking_activities
from orchestration.activities.notification import notification_activities


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """
    Start the Temporal worker.
    """
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")

    # Create worker for order workflows
    order_worker = Worker(
        client,
        task_queue="order-task-queue",
        workflows=[OrderProcessingWorkflow],
        activities=[
            order_activities.validate_inventory,
            order_activities.process_payment,
            order_activities.confirm_order,
            order_activities.mark_preparing,
            order_activities.dispatch_order,
            order_activities.mark_delivered,
            order_activities.cancel_order,
            order_activities.restore_inventory,
            order_activities.handle_order_failure,
            notification_activities.send_order_confirmation,
            notification_activities.send_dispatch_notification,
            notification_activities.send_delivery_confirmation,
            notification_activities.send_order_cancelled_notification,
            notification_activities.send_payment_failed_notification,
        ],
    )

    # Create worker for booking workflows
    booking_worker = Worker(
        client,
        task_queue="booking-task-queue",
        workflows=[BookingLifecycleWorkflow],
        activities=[
            booking_activities.mark_completed,
            booking_activities.mark_no_show,
            booking_activities.cancel_booking,
            notification_activities.send_booking_confirmation,
            notification_activities.send_booking_reminder,
            notification_activities.send_booking_cancelled_notification,
            notification_activities.send_booking_completed_notification,
        ],
    )

    logger.info("Starting Temporal workers...")
    logger.info("Order worker: task queue = order-task-queue")
    logger.info("Booking worker: task queue = booking-task-queue")

    # Run both workers concurrently
    await asyncio.gather(
        order_worker.run(),
        booking_worker.run(),
    )


if __name__ == "__main__":
    asyncio.run(main())
