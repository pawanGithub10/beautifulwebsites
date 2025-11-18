"""
Cart Router - API endpoints for shopping cart management

Comprehensive endpoints for:
- Get or create cart (user/guest)
- Add/update/remove items
- Clear cart
- Cart merging (guest to user)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas import (
    CartResponse, CartItemResponse,
    CartItemAdd, CartItemUpdate
)
from app.services.cart_service import CartService

router = APIRouter()


# ======================
# CART ENDPOINTS
# ======================

@router.get(
    "/{site_id}/cart",
    response_model=CartResponse,
    summary="Get or create cart",
    description="Get existing cart or create new one for user/guest"
)
async def get_or_create_cart(
    site_id: UUID,
    session_id: Optional[str] = Header(None, description="Guest session ID"),
    user_id: Optional[UUID] = None,  # TODO: Extract from auth token
    db: AsyncSession = Depends(get_db)
):
    """
    Get or create shopping cart

    For authenticated users: Uses user_id from auth token
    For guests: Uses X-Session-ID header
    """
    service = CartService(db)

    try:
        cart = await service.get_or_create_cart(
            site_id=site_id,
            user_id=user_id,
            session_id=session_id
        )

        # Get cart items
        items = await service.get_cart_items(cart.cart_id)

        return {
            "cart_id": cart.cart_id,
            "site_id": cart.site_id,
            "user_id": cart.user_id,
            "session_id": cart.session_id,
            "status": cart.status,
            "subtotal": cart.subtotal,
            "tax": cart.tax,
            "discount": cart.discount,
            "total": cart.total,
            "expires_at": cart.expires_at,
            "created_at": cart.created_at,
            "updated_at": cart.updated_at,
            "items": items
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{site_id}/cart/{cart_id}",
    response_model=CartResponse,
    summary="Get cart by ID",
    description="Get cart details by cart ID"
)
async def get_cart(
    site_id: UUID,
    cart_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get cart by ID"""
    service = CartService(db)
    cart = await service.get_cart(cart_id, site_id)

    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    # Get cart items
    items = await service.get_cart_items(cart.cart_id)

    return {
        "cart_id": cart.cart_id,
        "site_id": cart.site_id,
        "user_id": cart.user_id,
        "session_id": cart.session_id,
        "status": cart.status,
        "subtotal": cart.subtotal,
        "tax": cart.tax,
        "discount": cart.discount,
        "total": cart.total,
        "expires_at": cart.expires_at,
        "created_at": cart.created_at,
        "updated_at": cart.updated_at,
        "items": items
    }


# ======================
# CART ITEM ENDPOINTS
# ======================

@router.post(
    "/{site_id}/cart/{cart_id}/items",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to cart",
    description="Add product to cart (updates quantity if already exists)"
)
async def add_cart_item(
    site_id: UUID,
    cart_id: UUID,
    item_data: CartItemAdd,
    db: AsyncSession = Depends(get_db)
):
    """Add item to cart"""
    service = CartService(db)

    # Verify cart exists
    cart = await service.get_cart(cart_id, site_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    try:
        cart_item = await service.add_item(cart, item_data)
        return cart_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{site_id}/cart/{cart_id}/items",
    response_model=List[CartItemResponse],
    summary="List cart items",
    description="Get all items in cart"
)
async def list_cart_items(
    site_id: UUID,
    cart_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """List all cart items"""
    service = CartService(db)

    # Verify cart exists
    cart = await service.get_cart(cart_id, site_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    items = await service.get_cart_items(cart_id)
    return items


@router.put(
    "/{site_id}/cart/{cart_id}/items/{cart_item_id}",
    response_model=CartItemResponse,
    summary="Update cart item",
    description="Update item quantity in cart"
)
async def update_cart_item(
    site_id: UUID,
    cart_id: UUID,
    cart_item_id: UUID,
    item_data: CartItemUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update cart item quantity"""
    service = CartService(db)

    # Verify cart exists
    cart = await service.get_cart(cart_id, site_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    try:
        cart_item = await service.update_item(cart_item_id, cart_id, item_data)

        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )

        return cart_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{site_id}/cart/{cart_id}/items/{cart_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove cart item",
    description="Remove item from cart"
)
async def remove_cart_item(
    site_id: UUID,
    cart_id: UUID,
    cart_item_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Remove item from cart"""
    service = CartService(db)

    # Verify cart exists
    cart = await service.get_cart(cart_id, site_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    success = await service.remove_item(cart_item_id, cart_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )

    return None


@router.delete(
    "/{site_id}/cart/{cart_id}/items",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear cart",
    description="Remove all items from cart"
)
async def clear_cart(
    site_id: UUID,
    cart_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Clear all items from cart"""
    service = CartService(db)

    # Verify cart exists
    cart = await service.get_cart(cart_id, site_id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )

    await service.clear_cart(cart_id)
    return None


# ======================
# CART OPERATIONS
# ======================

@router.post(
    "/{site_id}/cart/merge",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Merge guest cart into user cart",
    description="Merge guest cart into user cart when user logs in"
)
async def merge_carts(
    site_id: UUID,
    session_id: str = Header(..., description="Guest session ID"),
    user_id: Optional[UUID] = None,  # TODO: Extract from auth token
    db: AsyncSession = Depends(get_db)
):
    """
    Merge guest cart into user cart

    Called when user logs in to merge their guest cart
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User must be authenticated to merge carts"
        )

    service = CartService(db)

    try:
        await service.merge_carts(
            guest_session_id=session_id,
            user_id=user_id,
            site_id=site_id
        )

        await db.commit()
        return None
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to merge carts: {str(e)}"
        )
