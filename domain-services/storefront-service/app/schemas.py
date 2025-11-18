"""
Pydantic schemas for Storefront Service

Comprehensive schemas for all entities with validation.
"""

from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
import re


# ======================
# CATEGORY SCHEMAS
# ======================

class CategoryCreate(BaseModel):
    """Create category"""
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_category_id: Optional[UUID] = None
    sort_order: int = Field(default=0)

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v


class CategoryUpdate(BaseModel):
    """Update category"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    image_url: Optional[str] = None
    parent_category_id: Optional[UUID] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(BaseModel):
    """Category response"""
    category_id: UUID
    site_id: UUID
    name: str
    slug: str
    description: Optional[str]
    image_url: Optional[str]
    parent_category_id: Optional[UUID]
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ======================
# PRODUCT SCHEMAS
# ======================

class ProductCreate(BaseModel):
    """Create product"""
    name: str = Field(..., min_length=1, max_length=300)
    slug: str = Field(..., min_length=1, max_length=300)
    sku: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)

    # Pricing
    price: Decimal = Field(..., gt=0, decimal_places=2)
    compare_at_price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    cost: Optional[Decimal] = Field(None, ge=0, decimal_places=2)

    # Category
    category_id: Optional[UUID] = None

    # Images
    images: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)

    # Inventory
    stock_quantity: int = Field(default=0, ge=0)
    track_inventory: bool = True
    allow_backorder: bool = False
    low_stock_threshold: int = Field(default=10, ge=0)

    # Attributes
    attributes: Dict[str, Any] = Field(default_factory=dict)

    # SEO
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = None

    # Status
    is_featured: bool = False

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v


class ProductUpdate(BaseModel):
    """Update product"""
    name: Optional[str] = Field(None, min_length=1, max_length=300)
    slug: Optional[str] = Field(None, min_length=1, max_length=300)
    sku: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)

    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    compare_at_price: Optional[Decimal] = Field(None, decimal_places=2)
    cost: Optional[Decimal] = Field(None, decimal_places=2)

    category_id: Optional[UUID] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None

    stock_quantity: Optional[int] = Field(None, ge=0)
    track_inventory: Optional[bool] = None
    allow_backorder: Optional[bool] = None
    low_stock_threshold: Optional[int] = Field(None, ge=0)

    attributes: Optional[Dict[str, Any]] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = None

    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None


class ProductResponse(BaseModel):
    """Product response"""
    product_id: UUID
    site_id: UUID
    category_id: Optional[UUID]
    sku: Optional[str]
    name: str
    slug: str
    description: Optional[str]
    short_description: Optional[str]
    price: Decimal
    compare_at_price: Optional[Decimal]
    cost: Optional[Decimal]
    images: List[str]
    tags: List[str]
    is_active: bool
    is_featured: bool
    stock_quantity: int
    track_inventory: bool
    allow_backorder: bool
    low_stock_threshold: int
    attributes: Dict[str, Any]
    meta_title: Optional[str]
    meta_description: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ======================
# VARIANT SCHEMAS
# ======================

class VariantCreate(BaseModel):
    """Create product variant"""
    name: str = Field(..., min_length=1, max_length=200)
    sku: Optional[str] = Field(None, max_length=100)
    options: Dict[str, str] = Field(..., description="Variant options like {size: 'L', color: 'Red'}")
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    compare_at_price: Optional[Decimal] = Field(None, decimal_places=2)
    stock_quantity: int = Field(default=0, ge=0)
    image_url: Optional[str] = None


class VariantUpdate(BaseModel):
    """Update product variant"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    sku: Optional[str] = Field(None, max_length=100)
    options: Optional[Dict[str, str]] = None
    price: Optional[Decimal] = Field(None, decimal_places=2)
    compare_at_price: Optional[Decimal] = Field(None, decimal_places=2)
    stock_quantity: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None
    is_active: Optional[bool] = None


class VariantResponse(BaseModel):
    """Variant response"""
    variant_id: UUID
    product_id: UUID
    name: str
    sku: Optional[str]
    options: Dict[str, str]
    price: Optional[Decimal]
    compare_at_price: Optional[Decimal]
    stock_quantity: int
    is_active: bool
    image_url: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ======================
# CART SCHEMAS
# ======================

class CartItemAdd(BaseModel):
    """Add item to cart"""
    product_id: UUID
    variant_id: Optional[UUID] = None
    quantity: int = Field(..., gt=0, le=100)


class CartItemUpdate(BaseModel):
    """Update cart item quantity"""
    quantity: int = Field(..., gt=0, le=100)


class CartItemResponse(BaseModel):
    """Cart item response"""
    cart_item_id: UUID
    product_id: UUID
    variant_id: Optional[UUID]
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    added_at: datetime

    # Include product details for convenience
    product_name: Optional[str] = None
    product_image: Optional[str] = None
    variant_options: Optional[Dict[str, str]] = None

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """Cart response with items"""
    cart_id: UUID
    site_id: UUID
    user_id: Optional[UUID]
    session_id: Optional[str]
    status: str
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal
    items: List[CartItemResponse] = []
    expires_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ======================
# ORDER SCHEMAS
# ======================

class DeliveryAddress(BaseModel):
    """Delivery address"""
    street: str
    city: str
    state: str
    postal_code: str
    country: str = "India"
    landmark: Optional[str] = None


class OrderCreate(BaseModel):
    """Create order from cart"""
    cart_id: Optional[UUID] = None  # If placing from cart
    customer_name: str = Field(..., min_length=1, max_length=200)
    customer_email: Optional[str] = Field(None, max_length=255)
    customer_phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')  # E.164 format
    delivery_address: DeliveryAddress
    delivery_instructions: Optional[str] = None
    payment_method: str = Field(..., description="cod, online, upi, card")
    customer_notes: Optional[str] = None

    @field_validator('payment_method')
    @classmethod
    def validate_payment_method(cls, v):
        allowed = ['cod', 'online', 'upi', 'card']
        if v not in allowed:
            raise ValueError(f'Payment method must be one of: {", ".join(allowed)}')
        return v


class OrderStatusUpdate(BaseModel):
    """Update order status"""
    order_status: str = Field(..., description="confirmed, preparing, dispatched, delivered, cancelled")
    internal_notes: Optional[str] = None

    @field_validator('order_status')
    @classmethod
    def validate_status(cls, v):
        allowed = ['confirmed', 'preparing', 'dispatched', 'delivered', 'cancelled']
        if v not in allowed:
            raise ValueError(f'Status must be one of: {", ".join(allowed)}')
        return v


class OrderItemResponse(BaseModel):
    """Order item response"""
    order_item_id: UUID
    product_id: Optional[UUID]
    variant_id: Optional[UUID]
    product_name: str
    product_sku: Optional[str]
    variant_options: Optional[Dict[str, str]]
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """Order response"""
    order_id: UUID
    site_id: UUID
    order_number: str
    user_id: Optional[UUID]
    customer_name: str
    customer_email: Optional[str]
    customer_phone: str
    delivery_address: Dict[str, Any]
    delivery_instructions: Optional[str]
    subtotal: Decimal
    tax: Decimal
    delivery_fee: Decimal
    discount: Decimal
    total: Decimal
    payment_method: str
    payment_status: str
    payment_reference: Optional[str]
    order_status: str
    customer_notes: Optional[str]
    internal_notes: Optional[str]
    items: List[OrderItemResponse] = []
    placed_at: datetime
    confirmed_at: Optional[datetime]
    dispatched_at: Optional[datetime]
    delivered_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class OrderHistoryResponse(BaseModel):
    """Order status history"""
    history_id: UUID
    old_status: Optional[str]
    new_status: str
    notes: Optional[str]
    changed_by_user_id: Optional[UUID]
    customer_notified: bool
    notification_sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ======================
# SEARCH & FILTER SCHEMAS
# ======================

class ProductFilters(BaseModel):
    """Product search and filter parameters"""
    category_id: Optional[UUID] = None
    search: Optional[str] = None  # Search in name, description
    tags: Optional[List[str]] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    is_featured: Optional[bool] = None
    in_stock: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default='created_at')  # created_at, name, price
    sort_order: str = Field(default='desc')  # asc, desc


class OrderFilters(BaseModel):
    """Order search and filter parameters"""
    order_status: Optional[str] = None
    payment_status: Optional[str] = None
    customer_phone: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# ======================
# INVENTORY SCHEMAS
# ======================

class StockAdjustment(BaseModel):
    """Manual stock adjustment"""
    quantity_change: int = Field(..., description="Positive for increase, negative for decrease")
    notes: Optional[str] = None
    adjustment_type: str = Field(default='manual')  # manual, damage, loss, found


class StockHistoryResponse(BaseModel):
    """Stock movement history"""
    history_id: UUID
    product_id: UUID
    variant_id: Optional[UUID]
    movement_type: str
    quantity_change: int
    quantity_after: int
    reference_type: Optional[str]
    reference_id: Optional[UUID]
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ======================
# COMMON SCHEMAS
# ======================

class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int


class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    error_code: Optional[str] = None


class SuccessResponse(BaseModel):
    """Success response"""
    message: str
    data: Optional[Dict[str, Any]] = None
