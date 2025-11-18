"""
Products Router - API endpoints for catalog management

Comprehensive endpoints for:
- Categories (hierarchical)
- Products (with search, filtering, pagination)
- Product variants
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    ProductCreate, ProductUpdate, ProductResponse,
    VariantCreate, VariantUpdate, VariantResponse,
    ProductFilters, PaginatedResponse
)
from app.services.product_service import ProductService

router = APIRouter()


# ======================
# CATEGORY ENDPOINTS
# ======================

@router.post(
    "/{site_id}/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create category",
    description="Create a new product category"
)
async def create_category(
    site_id: UUID,
    category_data: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new category"""
    service = ProductService(db)

    try:
        category = await service.create_category(site_id, category_data)
        return category
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{site_id}/categories",
    response_model=List[CategoryResponse],
    summary="List categories",
    description="Get all categories for a site (optionally filtered by parent)"
)
async def list_categories(
    site_id: UUID,
    parent_id: Optional[UUID] = Query(None, description="Filter by parent category"),
    active_only: bool = Query(True, description="Only return active categories"),
    db: AsyncSession = Depends(get_db)
):
    """List categories"""
    service = ProductService(db)
    categories = await service.list_categories(site_id, parent_id, active_only)
    return categories


@router.get(
    "/{site_id}/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Get category",
    description="Get category by ID"
)
async def get_category(
    site_id: UUID,
    category_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get category by ID"""
    service = ProductService(db)
    category = await service.get_category(category_id, site_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


@router.put(
    "/{site_id}/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Update category",
    description="Update category details"
)
async def update_category(
    site_id: UUID,
    category_id: UUID,
    category_data: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update category"""
    service = ProductService(db)

    try:
        category = await service.update_category(category_id, site_id, category_data)

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        return category
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{site_id}/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete category",
    description="Soft delete category (sets inactive)"
)
async def delete_category(
    site_id: UUID,
    category_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete category"""
    service = ProductService(db)

    try:
        success = await service.delete_category(category_id, site_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ======================
# PRODUCT ENDPOINTS
# ======================

@router.post(
    "/{site_id}/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    description="Create a new product"
)
async def create_product(
    site_id: UUID,
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new product"""
    service = ProductService(db)

    try:
        product = await service.create_product(site_id, product_data)
        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{site_id}/products",
    summary="Search products",
    description="Search and filter products with pagination"
)
async def search_products(
    site_id: UUID,
    category_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None, description="Search in name and description"),
    tags: Optional[List[str]] = Query(None),
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    is_featured: Optional[bool] = Query(None),
    in_stock: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="asc or desc"),
    db: AsyncSession = Depends(get_db)
):
    """Search products with filters and pagination"""
    service = ProductService(db)

    # Build filters
    filters = ProductFilters(
        category_id=category_id,
        search=search,
        tags=tags,
        min_price=min_price,
        max_price=max_price,
        is_featured=is_featured,
        in_stock=in_stock,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order
    )

    products, total = await service.search_products(site_id, filters)

    # Calculate pages
    pages = (total + page_size - 1) // page_size

    return {
        "items": products,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages
    }


@router.get(
    "/{site_id}/products/{product_id}",
    response_model=ProductResponse,
    summary="Get product",
    description="Get product by ID"
)
async def get_product(
    site_id: UUID,
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get product by ID"""
    service = ProductService(db)
    product = await service.get_product(product_id, site_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


@router.get(
    "/{site_id}/products/by-slug/{slug}",
    response_model=ProductResponse,
    summary="Get product by slug",
    description="Get product by slug (for SEO-friendly URLs)"
)
async def get_product_by_slug(
    site_id: UUID,
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get product by slug"""
    service = ProductService(db)
    product = await service.get_product_by_slug(slug, site_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with slug '{slug}' not found"
        )

    return product


@router.put(
    "/{site_id}/products/{product_id}",
    response_model=ProductResponse,
    summary="Update product",
    description="Update product details"
)
async def update_product(
    site_id: UUID,
    product_id: UUID,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update product"""
    service = ProductService(db)

    try:
        product = await service.update_product(product_id, site_id, product_data)

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )

        return product
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{site_id}/products/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product",
    description="Soft delete product (sets inactive)"
)
async def delete_product(
    site_id: UUID,
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete product"""
    service = ProductService(db)
    success = await service.delete_product(product_id, site_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return None


# ======================
# VARIANT ENDPOINTS
# ======================

@router.post(
    "/{site_id}/products/{product_id}/variants",
    response_model=VariantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create variant",
    description="Create a product variant (e.g., different size/color)"
)
async def create_variant(
    site_id: UUID,
    product_id: UUID,
    variant_data: VariantCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create product variant"""
    service = ProductService(db)

    try:
        variant = await service.create_variant(product_id, site_id, variant_data)
        return variant
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{site_id}/products/{product_id}/variants",
    response_model=List[VariantResponse],
    summary="List variants",
    description="Get all variants for a product"
)
async def list_variants(
    site_id: UUID,
    product_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """List product variants"""
    service = ProductService(db)
    variants = await service.list_variants(product_id, site_id)
    return variants


@router.put(
    "/{site_id}/products/{product_id}/variants/{variant_id}",
    response_model=VariantResponse,
    summary="Update variant",
    description="Update product variant"
)
async def update_variant(
    site_id: UUID,
    product_id: UUID,
    variant_id: UUID,
    variant_data: VariantUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update variant"""
    service = ProductService(db)
    variant = await service.update_variant(variant_id, variant_data)

    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Variant not found"
        )

    return variant
