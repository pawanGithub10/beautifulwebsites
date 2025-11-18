"""
Order Activities

Activities are the actual work units that interact with domain services.
Each activity should be idempotent and handle failures gracefully.
"""

import httpx
import os
from typing import Dict, Any
from temporalio import activity


# Service URLs from environment
STOREFRONT_SERVICE_URL = os.getenv("STOREFRONT_SERVICE_URL", "http://localhost:8011")


@activity.defn
async def validate_inventory(order_data: Dict[str, Any]) -> Dict[str, bool]:
    """
    Validate that all items in the order are in stock.

    Args:
        order_data: Order with items to validate

    Returns:
        {"success": True/False, "message": str}
    """
    site_id = order_data["site_id"]
    items = order_data["items"]

    activity.logger.info(f"Validating inventory for {len(items)} items")

    try:
        async with httpx.AsyncClient() as client:
            # Check each item's stock
            for item in items:
                product_id = item["product_id"]
                variant_id = item.get("variant_id")
                quantity = item["quantity"]

                # Get product/variant stock
                if variant_id:
                    response = await client.get(
                        f"{STOREFRONT_SERVICE_URL}/api/v1/{site_id}/products/{product_id}/variants/{variant_id}"
                    )
                else:
                    response = await client.get(
                        f"{STOREFRONT_SERVICE_URL}/api/v1/{site_id}/products/{product_id}"
                    )

                response.raise_for_status()
                data = response.json()

                stock = data.get("stock_quantity", 0)
                if stock < quantity:
                    activity.logger.warning(
                        f"Insufficient stock for item {product_id}: needed {quantity}, available {stock}"
                    )
                    return {"success": False, "message": f"Insufficient stock for item"}

        return {"success": True, "message": "All items in stock"}

    except Exception as e:
        activity.logger.error(f"Inventory validation failed: {str(e)}")
        raise


@activity.defn
async def process_payment(payment_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process payment for the order.

    In a real system, this would integrate with a payment gateway.
    For MVP, we'll simulate payment processing.

    Args:
        payment_data: {order_id, amount, payment_method}

    Returns:
        {"success": bool, "transaction_id": str}
    """
    order_id = payment_data["order_id"]
    amount = payment_data["amount"]
    method = payment_data.get("payment_method", "cod")

    activity.logger.info(f"Processing payment for order {order_id}: {amount} via {method}")

    # Simulate payment processing
    if method == "cod":
        # COD always succeeds
        return {
            "success": True,
            "transaction_id": f"TXN-{order_id}",
            "payment_method": "cod"
        }
    else:
        # For other methods, simulate 95% success rate
        import random
        success = random.random() > 0.05

        if success:
            return {
                "success": True,
                "transaction_id": f"TXN-{order_id}-{method}",
                "payment_method": method
            }
        else:
            return {
                "success": False,
                "message": "Payment gateway declined"
            }


@activity.defn
async def confirm_order(order_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update order status to 'confirmed'.
    """
    order_id = order_info["order_id"]
    site_id = order_info["site_id"]

    activity.logger.info(f"Confirming order {order_id}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{STOREFRONT_SERVICE_URL}/api/v1/{site_id}/orders/{order_id}/status",
                json={"order_status": "confirmed"}
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        activity.logger.error(f"Failed to confirm order: {str(e)}")
        raise


@activity.defn
async def mark_preparing(order_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update order status to 'preparing'.
    """
    order_id = order_info["order_id"]
    site_id = order_info["site_id"]

    activity.logger.info(f"Marking order {order_id} as preparing")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{STOREFRONT_SERVICE_URL}/api/v1/{site_id}/orders/{order_id}/status",
                json={"order_status": "preparing"}
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        activity.logger.error(f"Failed to mark order as preparing: {str(e)}")
        raise


@activity.defn
async def dispatch_order(order_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update order status to 'dispatched' and generate tracking number.
    """
    order_id = order_info["order_id"]
    site_id = order_info["site_id"]

    activity.logger.info(f"Dispatching order {order_id}")

    # Generate tracking number
    import random
    import string
    tracking_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{STOREFRONT_SERVICE_URL}/api/v1/{site_id}/orders/{order_id}/status",
                json={"order_status": "dispatched"}
            )
            response.raise_for_status()

            return {
                **response.json(),
                "tracking_number": tracking_number
            }

    except Exception as e:
        activity.logger.error(f"Failed to dispatch order: {str(e)}")
        raise


@activity.defn
async def mark_delivered(order_info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update order status to 'delivered'.
    """
    order_id = order_info["order_id"]
    site_id = order_info["site_id"]

    activity.logger.info(f"Marking order {order_id} as delivered")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{STOREFRONT_SERVICE_URL}/api/v1/{site_id}/orders/{order_id}/status",
                json={"order_status": "delivered"}
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        activity.logger.error(f"Failed to mark order as delivered: {str(e)}")
        raise


@activity.defn
async def cancel_order(cancellation_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cancel the order and restore inventory.
    """
    order_id = cancellation_data["order_id"]
    site_id = cancellation_data["site_id"]
    reason = cancellation_data.get("reason", "Cancelled by system")

    activity.logger.info(f"Cancelling order {order_id}: {reason}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{STOREFRONT_SERVICE_URL}/api/v1/{site_id}/orders/{order_id}/cancel",
                json={"reason": reason}
            )
            response.raise_for_status()
            return response.json()

    except Exception as e:
        activity.logger.error(f"Failed to cancel order: {str(e)}")
        raise


@activity.defn
async def restore_inventory(order_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Restore inventory for cancelled order.
    This is automatically handled by the cancel_order endpoint.
    """
    activity.logger.info(f"Inventory restoration handled by cancel_order")
    return {"success": True}


@activity.defn
async def handle_order_failure(failure_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle order workflow failure - log and cleanup.
    """
    order_id = failure_data["order_id"]
    error = failure_data.get("error", "Unknown error")

    activity.logger.error(f"Order {order_id} failed: {error}")

    # Log to monitoring system
    # Send alert to operations team
    # Cleanup if needed

    return {"logged": True}
