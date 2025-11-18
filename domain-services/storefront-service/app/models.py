"""
Database models for Storefront Service

Comprehensive e-commerce models:
- Categories (hierarchical)
- Products (with variants, images)
- Cart & CartItems
- Orders & OrderItems
- Order History
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey, Numeric, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timedelta

Base = declarative_base()


class Category(Base):
    """
    Product category - supports hierarchical structure
    """
    __tablename__ = "categories"

    category_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    parent_category_id = Column(UUID(as_uuid=True), ForeignKey('categories.category_id'), nullable=True)

    # Category info
    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)
    description = Column(Text)
    image_url = Column(String(500))

    # Display
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_category_site_slug', 'site_id', 'slug'),
        Index('idx_category_parent', 'parent_category_id'),
    )

    def __repr__(self):
        return f"<Category(id={self.category_id}, name={self.name})>"


class Product(Base):
    """
    Product entity - main product information
    """
    __tablename__ = "products"

    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey('categories.category_id'), nullable=True)

    # Product identification
    sku = Column(String(100), unique=True, index=True)
    name = Column(String(300), nullable=False)
    slug = Column(String(300), nullable=False)

    # Description
    description = Column(Text)
    short_description = Column(String(500))

    # Pricing
    price = Column(Numeric(10, 2), nullable=False)
    compare_at_price = Column(Numeric(10, 2))  # Original price for showing discounts
    cost = Column(Numeric(10, 2))  # Cost price for margin calculations

    # Images (array of URLs)
    images = Column(JSONB, default=list)

    # Categorization & Search
    tags = Column(ARRAY(String), default=list)

    # Status
    is_active = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)

    # Inventory
    stock_quantity = Column(Integer, default=0)
    track_inventory = Column(Boolean, default=True)
    allow_backorder = Column(Boolean, default=False)
    low_stock_threshold = Column(Integer, default=10)

    # Flexible attributes (color, size, weight, etc.)
    attributes = Column(JSONB, default=dict)

    # SEO
    meta_title = Column(String(200))
    meta_description = Column(Text)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Indexes
    __table_args__ = (
        Index('idx_product_site_slug', 'site_id', 'slug'),
        Index('idx_product_site_category', 'site_id', 'category_id'),
        Index('idx_product_active', 'is_active'),
        Index('idx_product_featured', 'is_featured'),
    )

    def __repr__(self):
        return f"<Product(id={self.product_id}, name={self.name}, price={self.price})>"


class ProductVariant(Base):
    """
    Product variants - for products with options (size, color, etc.)
    """
    __tablename__ = "product_variants"

    variant_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id', ondelete='CASCADE'), nullable=False)

    # Variant identification
    sku = Column(String(100), unique=True, index=True)
    name = Column(String(200))  # e.g., "Large / Red"

    # Variant options (e.g., {"size": "L", "color": "Red"})
    options = Column(JSONB, nullable=False)

    # Pricing override (optional)
    price = Column(Numeric(10, 2))  # If null, uses product price
    compare_at_price = Column(Numeric(10, 2))

    # Inventory
    stock_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    # Image
    image_url = Column(String(500))

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_variant_product', 'product_id'),
    )

    def __repr__(self):
        return f"<ProductVariant(id={self.variant_id}, name={self.name})>"


class Cart(Base):
    """
    Shopping cart - supports both user and guest carts
    """
    __tablename__ = "carts"

    cart_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # User or session identification
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # NULL for guest carts
    session_id = Column(String(255), nullable=True, index=True)  # For guest tracking

    # Cart lifecycle
    status = Column(String(20), default='active')  # active, abandoned, converted
    expires_at = Column(DateTime(timezone=True))

    # Totals (cached for performance)
    subtotal = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    tax = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), default=0)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_cart_user', 'user_id'),
        Index('idx_cart_session', 'session_id'),
        Index('idx_cart_status', 'status'),
    )

    def __repr__(self):
        return f"<Cart(id={self.cart_id}, total={self.total})>"


class CartItem(Base):
    """
    Items in a shopping cart
    """
    __tablename__ = "cart_items"

    cart_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUID(as_uuid=True), ForeignKey('carts.cart_id', ondelete='CASCADE'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey('product_variants.variant_id'), nullable=True)

    # Quantity
    quantity = Column(Integer, nullable=False, default=1)

    # Price snapshot (at time of adding to cart)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)

    # Timestamps
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_cart_item_cart', 'cart_id'),
        Index('idx_cart_item_product', 'product_id'),
    )

    def __repr__(self):
        return f"<CartItem(id={self.cart_item_id}, qty={self.quantity}, price={self.total_price})>"


class Order(Base):
    """
    Customer order - placed from cart
    """
    __tablename__ = "orders"

    order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Order identification
    order_number = Column(String(50), unique=True, nullable=False, index=True)  # Human-readable

    # Customer info
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # NULL for guest orders
    customer_name = Column(String(200), nullable=False)
    customer_email = Column(String(255))
    customer_phone = Column(String(20), nullable=False)

    # Delivery
    delivery_address = Column(JSONB)  # Full address object
    delivery_instructions = Column(Text)

    # Pricing
    subtotal = Column(Numeric(10, 2), nullable=False)
    tax = Column(Numeric(10, 2), default=0)
    delivery_fee = Column(Numeric(10, 2), default=0)
    discount = Column(Numeric(10, 2), default=0)
    total = Column(Numeric(10, 2), nullable=False)

    # Payment
    payment_method = Column(String(50))  # cod, online, upi, card
    payment_status = Column(String(20), default='pending', index=True)  # pending, paid, failed, refunded
    payment_reference = Column(String(255))  # Transaction ID from payment gateway

    # Order status workflow
    order_status = Column(String(20), default='placed', index=True)
    # placed → confirmed → preparing → dispatched → delivered / cancelled

    # Notes
    customer_notes = Column(Text)
    internal_notes = Column(Text)  # For staff only

    # Timestamps
    placed_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed_at = Column(DateTime(timezone=True))
    dispatched_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    cancelled_at = Column(DateTime(timezone=True))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        Index('idx_order_site_status', 'site_id', 'order_status'),
        Index('idx_order_user', 'user_id'),
        Index('idx_order_placed', 'placed_at'),
    )

    def __repr__(self):
        return f"<Order(number={self.order_number}, status={self.order_status}, total={self.total})>"


class OrderItem(Base):
    """
    Line items in an order
    """
    __tablename__ = "order_items"

    order_item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False)

    # Product snapshot (at time of order)
    product_id = Column(UUID(as_uuid=True), nullable=True)  # Can be NULL if product deleted
    variant_id = Column(UUID(as_uuid=True), nullable=True)
    product_name = Column(String(300), nullable=False)
    product_sku = Column(String(100))
    variant_options = Column(JSONB)  # Snapshot of variant options

    # Pricing
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(10, 2), nullable=False)

    # Product snapshot
    product_snapshot = Column(JSONB)  # Full product data at time of order

    __table_args__ = (
        Index('idx_order_item_order', 'order_id'),
    )

    def __repr__(self):
        return f"<OrderItem(product={self.product_name}, qty={self.quantity}, price={self.total_price})>"


class OrderHistory(Base):
    """
    Order status change history - audit trail
    """
    __tablename__ = "order_history"

    history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.order_id', ondelete='CASCADE'), nullable=False)

    # Status change
    old_status = Column(String(20))
    new_status = Column(String(20), nullable=False)

    # Notes
    notes = Column(Text)
    changed_by_user_id = Column(UUID(as_uuid=True))  # Staff member who made change

    # Notification tracking
    customer_notified = Column(Boolean, default=False)
    notification_sent_at = Column(DateTime(timezone=True))

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_order_history_order', 'order_id'),
    )

    def __repr__(self):
        return f"<OrderHistory(order={self.order_id}, {self.old_status}→{self.new_status})>"


class StockHistory(Base):
    """
    Inventory movement tracking
    """
    __tablename__ = "stock_history"

    history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey('product_variants.variant_id'), nullable=True)

    # Movement
    movement_type = Column(String(50), nullable=False)  # sale, restock, adjustment, return
    quantity_change = Column(Integer, nullable=False)  # Positive for increase, negative for decrease
    quantity_after = Column(Integer, nullable=False)

    # Reference
    reference_type = Column(String(50))  # order, purchase, adjustment
    reference_id = Column(UUID(as_uuid=True))  # Order ID, Purchase ID, etc.

    # Notes
    notes = Column(Text)
    created_by_user_id = Column(UUID(as_uuid=True))

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_stock_history_product', 'product_id'),
        Index('idx_stock_history_type', 'movement_type'),
    )

    def __repr__(self):
        return f"<StockHistory(product={self.product_id}, change={self.quantity_change})>"
