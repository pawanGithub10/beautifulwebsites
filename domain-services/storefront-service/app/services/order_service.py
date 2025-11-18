"""
Order Service - Order management and lifecycle

Handles:
- Order placement from cart
- Order status workflow
- Order history tracking
- Inventory deduction
- Notifications
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, desc
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import logging
import random
import string

from app.models import (
    Order, OrderItem, OrderHistory,
    Cart, CartItem,
    Product, ProductVariant,
    StockHistory
)
from app.schemas import OrderCreate, OrderStatusUpdate, OrderFilters

logger = logging.getLogger(__name__)


class OrderService:
    """Service for managing orders"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_order_number(self) -> str:
        """Generate unique order number"""
        # Format: ORD-YYYYMMDD-XXXXX
        date_part = datetime.utcnow().strftime('%Y%m%d')
        random_part = ''.join(random.choices(string.digits, k=5))
        return f"ORD-{date_part}-{random_part}"

    async def create_order(
        self,
        site_id: UUID,
        order_data: OrderCreate,
        user_id: Optional[UUID] = None
    ) -> Order:
        """
        Create order from cart

        Steps:
        1. Validate cart exists and has items
        2. Check inventory availability
        3. Create order and order items
        4. Deduct inventory
        5. Mark cart as converted
        6. Create order history entry
        7. Emit events for notifications
        """
        # 1. Get cart if cart_id provided
        cart = None
        cart_items = []

        if order_data.cart_id:
            cart_result = await self.db.execute(
                select(Cart).where(
                    and_(
                        Cart.cart_id == order_data.cart_id,
                        Cart.site_id == site_id,
                        Cart.status == 'active'
                    )
                )
            )
            cart = cart_result.scalar_one_or_none()

            if not cart:
                raise ValueError("Cart not found or already converted")

            # Get cart items
            items_result = await self.db.execute(
                select(CartItem).where(CartItem.cart_id == cart.cart_id)
            )
            cart_items = list(items_result.scalars().all())

            if not cart_items:
                raise ValueError("Cart is empty")

        else:
            raise ValueError("cart_id is required")

        # 2. Validate inventory for all items
        for cart_item in cart_items:
            product_result = await self.db.execute(
                select(Product).where(Product.product_id == cart_item.product_id)
            )
            product = product_result.scalar_one_or_none()

            if not product or not product.is_active:
                raise ValueError(f"Product {cart_item.product_id} is no longer available")

            if product.track_inventory and not product.allow_backorder:
                if cart_item.variant_id:
                    variant_result = await self.db.execute(
                        select(ProductVariant).where(ProductVariant.variant_id == cart_item.variant_id)
                    )
                    variant = variant_result.scalar_one_or_none()
                    if not variant or variant.stock_quantity < cart_item.quantity:
                        raise ValueError(f"Insufficient stock for {product.name}")
                else:
                    if product.stock_quantity < cart_item.quantity:
                        raise ValueError(f"Insufficient stock for {product.name}")

        # 3. Generate order number
        order_number = self._generate_order_number()

        # Ensure uniqueness
        while True:
            existing = await self.db.execute(
                select(Order).where(Order.order_number == order_number)
            )
            if not existing.scalar_one_or_none():
                break
            order_number = self._generate_order_number()

        # 4. Create order
        order = Order(
            site_id=site_id,
            user_id=user_id,
            order_number=order_number,
            customer_name=order_data.customer_name,
            customer_email=order_data.customer_email,
            customer_phone=order_data.customer_phone,
            delivery_address=order_data.delivery_address.model_dump(),
            delivery_instructions=order_data.delivery_instructions,
            subtotal=cart.subtotal,
            tax=cart.tax,
            delivery_fee=Decimal('0'),  # TODO: Calculate based on location
            discount=cart.discount,
            total=cart.total,
            payment_method=order_data.payment_method,
            payment_status='pending',
            order_status='placed',
            customer_notes=order_data.customer_notes
        )

        self.db.add(order)
        await self.db.flush()
        await self.db.refresh(order)

        # 5. Create order items and deduct inventory
        for cart_item in cart_items:
            # Get product details for snapshot
            product_result = await self.db.execute(
                select(Product).where(Product.product_id == cart_item.product_id)
            )
            product = product_result.scalar_one_or_none()

            variant_options = None
            if cart_item.variant_id:
                variant_result = await self.db.execute(
                    select(ProductVariant).where(ProductVariant.variant_id == cart_item.variant_id)
                )
                variant = variant_result.scalar_one_or_none()
                if variant:
                    variant_options = variant.options

            # Create order item with product snapshot
            order_item = OrderItem(
                order_id=order.order_id,
                product_id=cart_item.product_id,
                variant_id=cart_item.variant_id,
                product_name=product.name,
                product_sku=product.sku,
                variant_options=variant_options,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.total_price,
                product_snapshot={
                    'name': product.name,
                    'description': product.short_description,
                    'image': product.images[0] if product.images else None,
                    'attributes': product.attributes
                }
            )

            self.db.add(order_item)

            # Deduct inventory
            if product.track_inventory:
                if cart_item.variant_id:
                    # Update variant stock
                    variant_result = await self.db.execute(
                        select(ProductVariant).where(ProductVariant.variant_id == cart_item.variant_id)
                    )
                    variant = variant_result.scalar_one_or_none()
                    if variant:
                        old_stock = variant.stock_quantity
                        variant.stock_quantity -= cart_item.quantity

                        # Create stock history
                        stock_history = StockHistory(
                            product_id=product.product_id,
                            variant_id=variant.variant_id,
                            movement_type='sale',
                            quantity_change=-cart_item.quantity,
                            quantity_after=variant.stock_quantity,
                            reference_type='order',
                            reference_id=order.order_id,
                            notes=f"Sold via order {order.order_number}"
                        )
                        self.db.add(stock_history)
                else:
                    # Update product stock
                    old_stock = product.stock_quantity
                    product.stock_quantity -= cart_item.quantity

                    # Create stock history
                    stock_history = StockHistory(
                        product_id=product.product_id,
                        variant_id=None,
                        movement_type='sale',
                        quantity_change=-cart_item.quantity,
                        quantity_after=product.stock_quantity,
                        reference_type='order',
                        reference_id=order.order_id,
                        notes=f"Sold via order {order.order_number}"
                    )
                    self.db.add(stock_history)

        # 6. Mark cart as converted
        cart.status = 'converted'

        # 7. Create initial order history entry
        order_history = OrderHistory(
            order_id=order.order_id,
            old_status=None,
            new_status='placed',
            notes="Order placed by customer"
        )
        self.db.add(order_history)

        await self.db.flush()
        await self.db.refresh(order)

        logger.info(f"Created order {order.order_number} for site {site_id}")

        # TODO: Emit event for notifications
        # await self.event_service.publish_order_placed(order)

        return order

    async def get_order(
        self,
        order_id: UUID,
        site_id: UUID
    ) -> Optional[Order]:
        """Get order by ID"""
        result = await self.db.execute(
            select(Order).where(
                and_(
                    Order.order_id == order_id,
                    Order.site_id == site_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_order_by_number(
        self,
        order_number: str,
        site_id: UUID
    ) -> Optional[Order]:
        """Get order by order number"""
        result = await self.db.execute(
            select(Order).where(
                and_(
                    Order.order_number == order_number,
                    Order.site_id == site_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_order_items(
        self,
        order_id: UUID
    ) -> List[OrderItem]:
        """Get all items in order"""
        result = await self.db.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        return list(result.scalars().all())

    async def list_orders(
        self,
        site_id: UUID,
        filters: OrderFilters
    ) -> tuple[List[Order], int]:
        """
        List orders with filtering and pagination

        Returns:
            Tuple of (orders, total_count)
        """
        query = select(Order).where(Order.site_id == site_id)

        # Apply filters
        if filters.order_status:
            query = query.where(Order.order_status == filters.order_status)

        if filters.payment_status:
            query = query.where(Order.payment_status == filters.payment_status)

        if filters.customer_phone:
            query = query.where(Order.customer_phone == filters.customer_phone)

        if filters.date_from:
            query = query.where(Order.placed_at >= filters.date_from)

        if filters.date_to:
            query = query.where(Order.placed_at <= filters.date_to)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.order_by(desc(Order.placed_at)).offset(offset).limit(filters.page_size)

        # Execute query
        result = await self.db.execute(query)
        orders = list(result.scalars().all())

        return orders, total

    async def update_order_status(
        self,
        order_id: UUID,
        site_id: UUID,
        status_data: OrderStatusUpdate,
        changed_by_user_id: Optional[UUID] = None
    ) -> Optional[Order]:
        """
        Update order status

        Validates status transitions and creates history entry
        """
        order = await self.get_order(order_id, site_id)
        if not order:
            return None

        old_status = order.order_status
        new_status = status_data.order_status

        # Validate status transition
        valid_transitions = {
            'placed': ['confirmed', 'cancelled'],
            'confirmed': ['preparing', 'cancelled'],
            'preparing': ['dispatched', 'cancelled'],
            'dispatched': ['delivered', 'cancelled'],
            'delivered': [],  # Terminal state
            'cancelled': []   # Terminal state
        }

        if new_status not in valid_transitions.get(old_status, []):
            raise ValueError(f"Invalid status transition from {old_status} to {new_status}")

        # Update order status
        order.order_status = new_status

        # Update internal notes if provided
        if status_data.internal_notes:
            order.internal_notes = (order.internal_notes or "") + f"\n{status_data.internal_notes}"

        # Update timestamps based on status
        if new_status == 'confirmed':
            order.confirmed_at = datetime.utcnow()
        elif new_status == 'dispatched':
            order.dispatched_at = datetime.utcnow()
        elif new_status == 'delivered':
            order.delivered_at = datetime.utcnow()
            order.payment_status = 'paid'  # For COD orders
        elif new_status == 'cancelled':
            order.cancelled_at = datetime.utcnow()
            # TODO: Restore inventory

        # Create history entry
        order_history = OrderHistory(
            order_id=order.order_id,
            old_status=old_status,
            new_status=new_status,
            notes=status_data.internal_notes,
            changed_by_user_id=changed_by_user_id
        )
        self.db.add(order_history)

        await self.db.flush()
        await self.db.refresh(order)

        logger.info(f"Updated order {order.order_number} status: {old_status} → {new_status}")

        # TODO: Emit event for notifications
        # await self.event_service.publish_order_status_changed(order, old_status)

        return order

    async def cancel_order(
        self,
        order_id: UUID,
        site_id: UUID,
        reason: str,
        user_id: Optional[UUID] = None
    ) -> Optional[Order]:
        """
        Cancel order and restore inventory
        """
        order = await self.get_order(order_id, site_id)
        if not order:
            return None

        if order.order_status in ['delivered', 'cancelled']:
            raise ValueError(f"Cannot cancel order with status {order.order_status}")

        old_status = order.order_status
        order.order_status = 'cancelled'
        order.cancelled_at = datetime.utcnow()

        # Restore inventory
        items = await self.get_order_items(order_id)

        for item in items:
            if item.variant_id:
                # Restore variant stock
                variant_result = await self.db.execute(
                    select(ProductVariant).where(ProductVariant.variant_id == item.variant_id)
                )
                variant = variant_result.scalar_one_or_none()
                if variant:
                    variant.stock_quantity += item.quantity

                    # Create stock history
                    stock_history = StockHistory(
                        product_id=item.product_id,
                        variant_id=variant.variant_id,
                        movement_type='return',
                        quantity_change=item.quantity,
                        quantity_after=variant.stock_quantity,
                        reference_type='order',
                        reference_id=order.order_id,
                        notes=f"Returned from cancelled order {order.order_number}"
                    )
                    self.db.add(stock_history)
            else:
                # Restore product stock
                product_result = await self.db.execute(
                    select(Product).where(Product.product_id == item.product_id)
                )
                product = product_result.scalar_one_or_none()
                if product:
                    product.stock_quantity += item.quantity

                    # Create stock history
                    stock_history = StockHistory(
                        product_id=product.product_id,
                        variant_id=None,
                        movement_type='return',
                        quantity_change=item.quantity,
                        quantity_after=product.stock_quantity,
                        reference_type='order',
                        reference_id=order.order_id,
                        notes=f"Returned from cancelled order {order.order_number}"
                    )
                    self.db.add(stock_history)

        # Create history entry
        order_history = OrderHistory(
            order_id=order.order_id,
            old_status=old_status,
            new_status='cancelled',
            notes=f"Order cancelled: {reason}",
            changed_by_user_id=user_id
        )
        self.db.add(order_history)

        await self.db.flush()
        await self.db.refresh(order)

        logger.info(f"Cancelled order {order.order_number}")

        return order

    async def get_order_history(
        self,
        order_id: UUID
    ) -> List[OrderHistory]:
        """Get order status history"""
        result = await self.db.execute(
            select(OrderHistory)
            .where(OrderHistory.order_id == order_id)
            .order_by(OrderHistory.created_at)
        )
        return list(result.scalars().all())
