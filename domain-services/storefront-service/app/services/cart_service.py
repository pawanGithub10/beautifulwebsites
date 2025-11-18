"""
Cart Service - Shopping cart operations

Handles:
- Cart creation (user and guest carts)
- Add/update/remove items
- Cart totals calculation
- Cart expiry
- Cart to order conversion
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete, func
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from app.models import Cart, CartItem, Product, ProductVariant
from app.schemas import CartItemAdd, CartItemUpdate
from app.config import settings

logger = logging.getLogger(__name__)


class CartService:
    """Service for managing shopping carts"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_cart(
        self,
        site_id: UUID,
        user_id: Optional[UUID] = None,
        session_id: Optional[str] = None
    ) -> Cart:
        """
        Get existing cart or create new one

        For authenticated users: find by user_id
        For guests: find by session_id
        """
        # Build query
        if user_id:
            query = select(Cart).where(
                and_(
                    Cart.site_id == site_id,
                    Cart.user_id == user_id,
                    Cart.status == 'active'
                )
            )
        elif session_id:
            query = select(Cart).where(
                and_(
                    Cart.site_id == site_id,
                    Cart.session_id == session_id,
                    Cart.status == 'active'
                )
            )
        else:
            raise ValueError("Either user_id or session_id must be provided")

        result = await self.db.execute(query)
        cart = result.scalar_one_or_none()

        if cart:
            # Check if cart is expired
            if cart.expires_at and cart.expires_at < datetime.utcnow():
                cart.status = 'abandoned'
                await self.db.flush()
                cart = None  # Create new cart

        if not cart:
            # Create new cart
            expires_at = datetime.utcnow() + timedelta(hours=settings.DEFAULT_CART_EXPIRY_HOURS)

            cart = Cart(
                site_id=site_id,
                user_id=user_id,
                session_id=session_id,
                status='active',
                expires_at=expires_at
            )

            self.db.add(cart)
            await self.db.flush()
            await self.db.refresh(cart)

            logger.info(f"Created new cart {cart.cart_id}")

        return cart

    async def get_cart(
        self,
        cart_id: UUID,
        site_id: UUID
    ) -> Optional[Cart]:
        """Get cart by ID"""
        result = await self.db.execute(
            select(Cart).where(
                and_(
                    Cart.cart_id == cart_id,
                    Cart.site_id == site_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_cart_items(
        self,
        cart_id: UUID
    ) -> List[CartItem]:
        """Get all items in cart"""
        result = await self.db.execute(
            select(CartItem).where(CartItem.cart_id == cart_id)
        )
        return list(result.scalars().all())

    async def add_item(
        self,
        cart: Cart,
        item_data: CartItemAdd
    ) -> CartItem:
        """Add item to cart"""
        # Verify product exists
        product_result = await self.db.execute(
            select(Product).where(
                and_(
                    Product.product_id == item_data.product_id,
                    Product.site_id == cart.site_id,
                    Product.is_active == True
                )
            )
        )
        product = product_result.scalar_one_or_none()

        if not product:
            raise ValueError("Product not found")

        # Get price (from variant or product)
        unit_price = product.price
        variant = None

        if item_data.variant_id:
            variant_result = await self.db.execute(
                select(ProductVariant).where(
                    and_(
                        ProductVariant.variant_id == item_data.variant_id,
                        ProductVariant.product_id == product.product_id,
                        ProductVariant.is_active == True
                    )
                )
            )
            variant = variant_result.scalar_one_or_none()

            if not variant:
                raise ValueError("Product variant not found")

            if variant.price:
                unit_price = variant.price

        # Check stock availability
        available_stock = variant.stock_quantity if variant else product.stock_quantity

        if product.track_inventory and not product.allow_backorder:
            if available_stock < item_data.quantity:
                raise ValueError(f"Only {available_stock} items available in stock")

        # Check if item already in cart
        existing_result = await self.db.execute(
            select(CartItem).where(
                and_(
                    CartItem.cart_id == cart.cart_id,
                    CartItem.product_id == item_data.product_id,
                    CartItem.variant_id == item_data.variant_id
                )
            )
        )
        existing_item = existing_result.scalar_one_or_none()

        if existing_item:
            # Update quantity
            existing_item.quantity += item_data.quantity
            existing_item.total_price = existing_item.unit_price * existing_item.quantity
            cart_item = existing_item
        else:
            # Check max items limit
            items_count_result = await self.db.execute(
                select(func.count()).where(CartItem.cart_id == cart.cart_id)
            )
            items_count = items_count_result.scalar()

            if items_count >= settings.MAX_CART_ITEMS:
                raise ValueError(f"Cart cannot have more than {settings.MAX_CART_ITEMS} items")

            # Create new cart item
            cart_item = CartItem(
                cart_id=cart.cart_id,
                product_id=item_data.product_id,
                variant_id=item_data.variant_id,
                quantity=item_data.quantity,
                unit_price=unit_price,
                total_price=unit_price * item_data.quantity
            )

            self.db.add(cart_item)

        await self.db.flush()

        # Recalculate cart totals
        await self._recalculate_cart(cart)

        await self.db.refresh(cart_item)
        logger.info(f"Added item to cart {cart.cart_id}: {product.name} x{item_data.quantity}")

        return cart_item

    async def update_item(
        self,
        cart_item_id: UUID,
        cart_id: UUID,
        item_data: CartItemUpdate
    ) -> Optional[CartItem]:
        """Update cart item quantity"""
        result = await self.db.execute(
            select(CartItem).where(
                and_(
                    CartItem.cart_item_id == cart_item_id,
                    CartItem.cart_id == cart_id
                )
            )
        )
        cart_item = result.scalar_one_or_none()

        if not cart_item:
            return None

        # Check stock availability for new quantity
        if cart_item.variant_id:
            variant_result = await self.db.execute(
                select(ProductVariant).where(ProductVariant.variant_id == cart_item.variant_id)
            )
            variant = variant_result.scalar_one_or_none()
            if variant:
                available_stock = variant.stock_quantity
        else:
            product_result = await self.db.execute(
                select(Product).where(Product.product_id == cart_item.product_id)
            )
            product = product_result.scalar_one_or_none()
            if product and product.track_inventory and not product.allow_backorder:
                available_stock = product.stock_quantity
                if available_stock < item_data.quantity:
                    raise ValueError(f"Only {available_stock} items available")

        # Update quantity
        cart_item.quantity = item_data.quantity
        cart_item.total_price = cart_item.unit_price * cart_item.quantity

        await self.db.flush()

        # Recalculate cart totals
        cart_result = await self.db.execute(
            select(Cart).where(Cart.cart_id == cart_id)
        )
        cart = cart_result.scalar_one_or_none()
        if cart:
            await self._recalculate_cart(cart)

        await self.db.refresh(cart_item)
        return cart_item

    async def remove_item(
        self,
        cart_item_id: UUID,
        cart_id: UUID
    ) -> bool:
        """Remove item from cart"""
        result = await self.db.execute(
            delete(CartItem).where(
                and_(
                    CartItem.cart_item_id == cart_item_id,
                    CartItem.cart_id == cart_id
                )
            )
        )

        if result.rowcount > 0:
            # Recalculate cart totals
            cart_result = await self.db.execute(
                select(Cart).where(Cart.cart_id == cart_id)
            )
            cart = cart_result.scalar_one_or_none()
            if cart:
                await self._recalculate_cart(cart)

            logger.info(f"Removed item {cart_item_id} from cart {cart_id}")
            return True

        return False

    async def clear_cart(
        self,
        cart_id: UUID
    ) -> bool:
        """Remove all items from cart"""
        await self.db.execute(
            delete(CartItem).where(CartItem.cart_id == cart_id)
        )

        # Reset cart totals
        cart_result = await self.db.execute(
            select(Cart).where(Cart.cart_id == cart_id)
        )
        cart = cart_result.scalar_one_or_none()

        if cart:
            cart.subtotal = Decimal('0')
            cart.tax = Decimal('0')
            cart.discount = Decimal('0')
            cart.total = Decimal('0')
            await self.db.flush()

            logger.info(f"Cleared cart {cart_id}")
            return True

        return False

    async def _recalculate_cart(self, cart: Cart):
        """Recalculate cart totals"""
        # Get all cart items
        items_result = await self.db.execute(
            select(CartItem).where(CartItem.cart_id == cart.cart_id)
        )
        items = items_result.scalars().all()

        # Calculate subtotal
        subtotal = sum(item.total_price for item in items)

        # Calculate tax (simplified - 5% for example)
        # In production, this would be based on location, product type, etc.
        tax = subtotal * Decimal('0.05')

        # Apply discounts (placeholder - would integrate with discount service)
        discount = Decimal('0')

        # Calculate total
        total = subtotal + tax - discount

        # Update cart
        cart.subtotal = subtotal
        cart.tax = tax
        cart.discount = discount
        cart.total = total

        await self.db.flush()

    async def merge_carts(
        self,
        guest_session_id: str,
        user_id: UUID,
        site_id: UUID
    ):
        """
        Merge guest cart into user cart when user logs in
        """
        # Get guest cart
        guest_cart_result = await self.db.execute(
            select(Cart).where(
                and_(
                    Cart.site_id == site_id,
                    Cart.session_id == guest_session_id,
                    Cart.status == 'active'
                )
            )
        )
        guest_cart = guest_cart_result.scalar_one_or_none()

        if not guest_cart:
            return  # No guest cart to merge

        # Get or create user cart
        user_cart = await self.get_or_create_cart(site_id, user_id=user_id)

        # Get guest cart items
        guest_items_result = await self.db.execute(
            select(CartItem).where(CartItem.cart_id == guest_cart.cart_id)
        )
        guest_items = guest_items_result.scalars().all()

        # Merge items
        for guest_item in guest_items:
            # Check if item already in user cart
            existing_result = await self.db.execute(
                select(CartItem).where(
                    and_(
                        CartItem.cart_id == user_cart.cart_id,
                        CartItem.product_id == guest_item.product_id,
                        CartItem.variant_id == guest_item.variant_id
                    )
                )
            )
            existing = existing_result.scalar_one_or_none()

            if existing:
                # Merge quantities
                existing.quantity += guest_item.quantity
                existing.total_price = existing.unit_price * existing.quantity
            else:
                # Move item to user cart
                guest_item.cart_id = user_cart.cart_id

        # Mark guest cart as converted
        guest_cart.status = 'converted'

        await self.db.flush()

        # Recalculate user cart totals
        await self._recalculate_cart(user_cart)

        logger.info(f"Merged guest cart {guest_cart.cart_id} into user cart {user_cart.cart_id}")
