"""
Orders Router - API endpoints for order management

Comprehensive endpoints for:
- Order placement
- Order status updates
- Order history tracking
- Order cancellation
- Order queries and filtering
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas import (
    OrderCreate, OrderResponse, OrderItemResponse,
    OrderStatusUpdate, OrderFilters,
    OrderHistoryResponse, PaginatedResponse
)
from app.services.order_service import OrderService

router = APIRouter()


# ======================
# ORDER ENDPOINTS
# ======================

@router.post(
    "/{site_id}/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create order",
    description="Place order from cart"
)
async def create_order(
    site_id: UUID,
    order_data: OrderCreate,
    user_id: Optional[UUID] = None,  # TODO: Extract from auth token
    db: AsyncSession = Depends(get_db)
):
    """
    Place order from cart

    Steps:
    1. Validates cart exists and has items
    2. Checks inventory availability
    3. Creates order with product snapshots
    4. Deducts inventory
    5. Marks cart as converted
    6. Creates order history entry
    """
    service = OrderService(db)

    try:
        order = await service.create_order(site_id, order_data, user_id)
        await db.commit()

        # Get order items
        items = await service.get_order_items(order.order_id)

        return {
            "order_id": order.order_id,
            "site_id": order.site_id,
            "user_id": order.user_id,
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "customer_phone": order.customer_phone,
            "delivery_address": order.delivery_address,
            "delivery_instructions": order.delivery_instructions,
            "subtotal": order.subtotal,
            "tax": order.tax,
            "delivery_fee": order.delivery_fee,
            "discount": order.discount,
            "total": order.total,
            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "order_status": order.order_status,
            "customer_notes": order.customer_notes,
            "internal_notes": order.internal_notes,
            "placed_at": order.placed_at,
            "confirmed_at": order.confirmed_at,
            "dispatched_at": order.dispatched_at,
            "delivered_at": order.delivered_at,
            "cancelled_at": order.cancelled_at,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "items": items
        }
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )


@router.get(
    "/{site_id}/orders",
    summary="List orders",
    description="List orders with filtering and pagination"
)
async def list_orders(
    site_id: UUID,
    order_status: Optional[str] = Query(None, description="Filter by order status"),
    payment_status: Optional[str] = Query(None, description="Filter by payment status"),
    customer_phone: Optional[str] = Query(None, description="Filter by customer phone"),
    date_from: Optional[str] = Query(None, description="Filter by date from (ISO format)"),
    date_to: Optional[str] = Query(None, description="Filter by date to (ISO format)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List orders with filters and pagination"""
    service = OrderService(db)

    # Build filters
    from datetime import datetime

    filters = OrderFilters(
        order_status=order_status,
        payment_status=payment_status,
        customer_phone=customer_phone,
        date_from=datetime.fromisoformat(date_from) if date_from else None,
        date_to=datetime.fromisoformat(date_to) if date_to else None,
        page=page,
        page_size=page_size
    )

    orders, total = await service.list_orders(site_id, filters)

    # Calculate pages
    pages = (total + page_size - 1) // page_size

    return {
        "items": orders,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }


@router.get(
    "/{site_id}/orders/{order_id}",
    response_model=OrderResponse,
    summary="Get order",
    description="Get order by ID"
)
async def get_order(
    site_id: UUID,
    order_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get order by ID"""
    service = OrderService(db)
    order = await service.get_order(order_id, site_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    # Get order items
    items = await service.get_order_items(order.order_id)

    return {
        "order_id": order.order_id,
        "site_id": order.site_id,
        "user_id": order.user_id,
        "order_number": order.order_number,
        "customer_name": order.customer_name,
        "customer_email": order.customer_email,
        "customer_phone": order.customer_phone,
        "delivery_address": order.delivery_address,
        "delivery_instructions": order.delivery_instructions,
        "subtotal": order.subtotal,
        "tax": order.tax,
        "delivery_fee": order.delivery_fee,
        "discount": order.discount,
        "total": order.total,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "order_status": order.order_status,
        "customer_notes": order.customer_notes,
        "internal_notes": order.internal_notes,
        "placed_at": order.placed_at,
        "confirmed_at": order.confirmed_at,
        "dispatched_at": order.dispatched_at,
        "delivered_at": order.delivered_at,
        "cancelled_at": order.cancelled_at,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "items": items
    }


@router.get(
    "/{site_id}/orders/by-number/{order_number}",
    response_model=OrderResponse,
    summary="Get order by number",
    description="Get order by order number (for customer lookup)"
)
async def get_order_by_number(
    site_id: UUID,
    order_number: str,
    db: AsyncSession = Depends(get_db)
):
    """Get order by order number"""
    service = OrderService(db)
    order = await service.get_order_by_number(order_number, site_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {order_number} not found"
        )

    # Get order items
    items = await service.get_order_items(order.order_id)

    return {
        "order_id": order.order_id,
        "site_id": order.site_id,
        "user_id": order.user_id,
        "order_number": order.order_number,
        "customer_name": order.customer_name,
        "customer_email": order.customer_email,
        "customer_phone": order.customer_phone,
        "delivery_address": order.delivery_address,
        "delivery_instructions": order.delivery_instructions,
        "subtotal": order.subtotal,
        "tax": order.tax,
        "delivery_fee": order.delivery_fee,
        "discount": order.discount,
        "total": order.total,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "order_status": order.order_status,
        "customer_notes": order.customer_notes,
        "internal_notes": order.internal_notes,
        "placed_at": order.placed_at,
        "confirmed_at": order.confirmed_at,
        "dispatched_at": order.dispatched_at,
        "delivered_at": order.delivered_at,
        "cancelled_at": order.cancelled_at,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "items": items
    }


@router.get(
    "/{site_id}/orders/{order_id}/items",
    response_model=List[OrderItemResponse],
    summary="Get order items",
    description="Get all items in order"
)
async def get_order_items(
    site_id: UUID,
    order_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get order items"""
    service = OrderService(db)

    # Verify order exists
    order = await service.get_order(order_id, site_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    items = await service.get_order_items(order_id)
    return items


# ======================
# ORDER STATUS ENDPOINTS
# ======================

@router.put(
    "/{site_id}/orders/{order_id}/status",
    response_model=OrderResponse,
    summary="Update order status",
    description="Update order status (validates transitions)"
)
async def update_order_status(
    site_id: UUID,
    order_id: UUID,
    status_data: OrderStatusUpdate,
    user_id: Optional[UUID] = None,  # TODO: Extract from auth token
    db: AsyncSession = Depends(get_db)
):
    """
    Update order status

    Valid transitions:
    - placed → confirmed, cancelled
    - confirmed → preparing, cancelled
    - preparing → dispatched, cancelled
    - dispatched → delivered, cancelled
    - delivered → (terminal state)
    - cancelled → (terminal state)
    """
    service = OrderService(db)

    try:
        order = await service.update_order_status(
            order_id=order_id,
            site_id=site_id,
            status_data=status_data,
            changed_by_user_id=user_id
        )

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        await db.commit()

        # Get order items
        items = await service.get_order_items(order.order_id)

        return {
            "order_id": order.order_id,
            "site_id": order.site_id,
            "user_id": order.user_id,
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "customer_phone": order.customer_phone,
            "delivery_address": order.delivery_address,
            "delivery_instructions": order.delivery_instructions,
            "subtotal": order.subtotal,
            "tax": order.tax,
            "delivery_fee": order.delivery_fee,
            "discount": order.discount,
            "total": order.total,
            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "order_status": order.order_status,
            "customer_notes": order.customer_notes,
            "internal_notes": order.internal_notes,
            "placed_at": order.placed_at,
            "confirmed_at": order.confirmed_at,
            "dispatched_at": order.dispatched_at,
            "delivered_at": order.delivered_at,
            "cancelled_at": order.cancelled_at,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "items": items
        }
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update order status: {str(e)}"
        )


@router.post(
    "/{site_id}/orders/{order_id}/cancel",
    response_model=OrderResponse,
    summary="Cancel order",
    description="Cancel order and restore inventory"
)
async def cancel_order(
    site_id: UUID,
    order_id: UUID,
    reason: str,
    user_id: Optional[UUID] = None,  # TODO: Extract from auth token
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel order

    - Restores inventory for all items
    - Cannot cancel delivered or already cancelled orders
    """
    service = OrderService(db)

    try:
        order = await service.cancel_order(
            order_id=order_id,
            site_id=site_id,
            reason=reason,
            user_id=user_id
        )

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )

        await db.commit()

        # Get order items
        items = await service.get_order_items(order.order_id)

        return {
            "order_id": order.order_id,
            "site_id": order.site_id,
            "user_id": order.user_id,
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "customer_email": order.customer_email,
            "customer_phone": order.customer_phone,
            "delivery_address": order.delivery_address,
            "delivery_instructions": order.delivery_instructions,
            "subtotal": order.subtotal,
            "tax": order.tax,
            "delivery_fee": order.delivery_fee,
            "discount": order.discount,
            "total": order.total,
            "payment_method": order.payment_method,
            "payment_status": order.payment_status,
            "order_status": order.order_status,
            "customer_notes": order.customer_notes,
            "internal_notes": order.internal_notes,
            "placed_at": order.placed_at,
            "confirmed_at": order.confirmed_at,
            "dispatched_at": order.dispatched_at,
            "delivered_at": order.delivered_at,
            "cancelled_at": order.cancelled_at,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "items": items
        }
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel order: {str(e)}"
        )


@router.get(
    "/{site_id}/orders/{order_id}/history",
    response_model=List[OrderHistoryResponse],
    summary="Get order history",
    description="Get complete order status history"
)
async def get_order_history(
    site_id: UUID,
    order_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get order status history"""
    service = OrderService(db)

    # Verify order exists
    order = await service.get_order(order_id, site_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    history = await service.get_order_history(order_id)
    return history
