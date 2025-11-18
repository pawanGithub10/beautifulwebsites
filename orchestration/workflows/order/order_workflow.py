"""
Order Processing Workflow

This workflow orchestrates the complete order lifecycle:
1. Order Placed → Inventory Check → Payment Processing
2. Order Confirmed → Notification Sent → Prepare for Shipping
3. Preparing → Dispatch → Tracking Update
4. Dispatched → Delivery → Completion Notification

Handles:
- Inventory validation and deduction
- Payment processing
- Email/SMS notifications
- Inventory restoration on cancellation
- Order status updates
- Failure handling and retries
"""

from datetime import timedelta
from typing import Dict, Any
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from orchestration.activities.order import order_activities
    from orchestration.activities.notification import notification_activities


@workflow.defn
class OrderProcessingWorkflow:
    """
    Orchestrates the complete order lifecycle from placement to delivery.

    Workflow Steps:
    1. Validate order and check inventory
    2. Process payment
    3. Confirm order and send confirmation notification
    4. Wait for preparation (can be manual trigger)
    5. Dispatch order and send tracking notification
    6. Mark as delivered and send delivery notification
    """

    @workflow.run
    async def run(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the order processing workflow.

        Args:
            order_data: {
                "order_id": str,
                "site_id": str,
                "customer_email": str,
                "customer_phone": str,
                "total_amount": float,
                "items": List[dict]
            }

        Returns:
            Dict with workflow execution summary
        """
        order_id = order_data["order_id"]
        workflow.logger.info(f"Starting order workflow for order {order_id}")

        # Retry policy for activities
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            backoff_coefficient=2.0,
            maximum_attempts=3,
        )

        try:
            # Step 1: Validate inventory
            workflow.logger.info(f"Step 1: Validating inventory for order {order_id}")
            inventory_check = await workflow.execute_activity(
                order_activities.validate_inventory,
                order_data,
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy,
            )

            if not inventory_check["success"]:
                # Inventory not available - cancel order
                await workflow.execute_activity(
                    order_activities.cancel_order,
                    {
                        "order_id": order_id,
                        "site_id": order_data["site_id"],
                        "reason": "Insufficient inventory"
                    },
                    start_to_close_timeout=timedelta(seconds=30),
                )

                await workflow.execute_activity(
                    notification_activities.send_order_cancelled_notification,
                    {
                        "order_id": order_id,
                        "customer_email": order_data["customer_email"],
                        "customer_phone": order_data.get("customer_phone"),
                        "reason": "Some items are out of stock"
                    },
                    start_to_close_timeout=timedelta(seconds=30),
                )

                return {
                    "status": "cancelled",
                    "reason": "Insufficient inventory",
                    "order_id": order_id
                }

            # Step 2: Process payment
            workflow.logger.info(f"Step 2: Processing payment for order {order_id}")
            payment_result = await workflow.execute_activity(
                order_activities.process_payment,
                {
                    "order_id": order_id,
                    "amount": order_data["total_amount"],
                    "payment_method": order_data.get("payment_method", "cod")
                },
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=retry_policy,
            )

            if not payment_result["success"]:
                # Payment failed - restore inventory and cancel
                await workflow.execute_activity(
                    order_activities.restore_inventory,
                    order_data,
                    start_to_close_timeout=timedelta(seconds=30),
                )

                await workflow.execute_activity(
                    order_activities.cancel_order,
                    {
                        "order_id": order_id,
                        "site_id": order_data["site_id"],
                        "reason": "Payment failed"
                    },
                    start_to_close_timeout=timedelta(seconds=30),
                )

                await workflow.execute_activity(
                    notification_activities.send_payment_failed_notification,
                    {
                        "order_id": order_id,
                        "customer_email": order_data["customer_email"],
                        "customer_phone": order_data.get("customer_phone"),
                    },
                    start_to_close_timeout=timedelta(seconds=30),
                )

                return {
                    "status": "cancelled",
                    "reason": "Payment failed",
                    "order_id": order_id
                }

            # Step 3: Confirm order
            workflow.logger.info(f"Step 3: Confirming order {order_id}")
            await workflow.execute_activity(
                order_activities.confirm_order,
                {
                    "order_id": order_id,
                    "site_id": order_data["site_id"],
                },
                start_to_close_timeout=timedelta(seconds=30),
            )

            # Send confirmation notification
            await workflow.execute_activity(
                notification_activities.send_order_confirmation,
                {
                    "order_id": order_id,
                    "customer_email": order_data["customer_email"],
                    "customer_phone": order_data.get("customer_phone"),
                    "order_details": order_data,
                },
                start_to_close_timeout=timedelta(seconds=30),
            )

            # Step 4: Wait for preparation signal (manual or auto after 1 hour)
            workflow.logger.info(f"Step 4: Waiting for preparation signal for order {order_id}")
            try:
                await workflow.wait_condition(
                    lambda: workflow.info().is_continue_as_new_suggested(),
                    timeout=timedelta(hours=1),
                )
            except:
                # Auto-transition to preparing after 1 hour
                pass

            # Mark as preparing
            await workflow.execute_activity(
                order_activities.mark_preparing,
                {
                    "order_id": order_id,
                    "site_id": order_data["site_id"],
                },
                start_to_close_timeout=timedelta(seconds=30),
            )

            # Step 5: Wait for dispatch signal (manual)
            workflow.logger.info(f"Step 5: Waiting for dispatch signal for order {order_id}")
            await workflow.wait_condition(
                lambda: False,  # Wait for manual signal
                timeout=timedelta(days=7),
            )

            # Dispatch order
            dispatch_result = await workflow.execute_activity(
                order_activities.dispatch_order,
                {
                    "order_id": order_id,
                    "site_id": order_data["site_id"],
                },
                start_to_close_timeout=timedelta(seconds=30),
            )

            # Send dispatch notification with tracking
            await workflow.execute_activity(
                notification_activities.send_dispatch_notification,
                {
                    "order_id": order_id,
                    "customer_email": order_data["customer_email"],
                    "customer_phone": order_data.get("customer_phone"),
                    "tracking_number": dispatch_result.get("tracking_number"),
                },
                start_to_close_timeout=timedelta(seconds=30),
            )

            # Step 6: Wait for delivery confirmation (manual)
            workflow.logger.info(f"Step 6: Waiting for delivery confirmation for order {order_id}")
            await workflow.wait_condition(
                lambda: False,  # Wait for manual signal
                timeout=timedelta(days=30),
            )

            # Mark as delivered
            await workflow.execute_activity(
                order_activities.mark_delivered,
                {
                    "order_id": order_id,
                    "site_id": order_data["site_id"],
                },
                start_to_close_timeout=timedelta(seconds=30),
            )

            # Send delivery confirmation
            await workflow.execute_activity(
                notification_activities.send_delivery_confirmation,
                {
                    "order_id": order_id,
                    "customer_email": order_data["customer_email"],
                    "customer_phone": order_data.get("customer_phone"),
                },
                start_to_close_timeout=timedelta(seconds=30),
            )

            workflow.logger.info(f"Order workflow completed for order {order_id}")

            return {
                "status": "delivered",
                "order_id": order_id,
                "payment_status": "paid",
            }

        except Exception as e:
            workflow.logger.error(f"Order workflow failed for order {order_id}: {str(e)}")
            # Handle failure - restore inventory if payment not processed
            await workflow.execute_activity(
                order_activities.handle_order_failure,
                {
                    "order_id": order_id,
                    "site_id": order_data["site_id"],
                    "error": str(e),
                },
                start_to_close_timeout=timedelta(seconds=30),
            )

            raise


    @workflow.signal
    async def cancel_order_signal(self, reason: str):
        """Signal to cancel the order at any stage."""
        workflow.logger.info(f"Received cancel signal: {reason}")
        # This would trigger cancellation logic
        pass

    @workflow.signal
    async def mark_preparing_signal(self):
        """Signal to mark order as preparing."""
        workflow.logger.info("Received preparing signal")
        # Trigger state transition
        pass

    @workflow.signal
    async def dispatch_signal(self, tracking_number: str):
        """Signal to dispatch the order."""
        workflow.logger.info(f"Received dispatch signal with tracking: {tracking_number}")
        # Trigger dispatch
        pass

    @workflow.signal
    async def mark_delivered_signal(self):
        """Signal to mark order as delivered."""
        workflow.logger.info("Received delivered signal")
        # Trigger delivery confirmation
        pass
