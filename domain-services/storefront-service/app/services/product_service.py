"""
Product Service - Business logic for product management

Handles:
- Products CRUD
- Categories CRUD
- Product variants
- Search and filtering
- Stock checking
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from typing import List, Optional, Tuple
from uuid import UUID
import logging

from app.models import Product, Category, ProductVariant, StockHistory
from app.schemas import (
    ProductCreate, ProductUpdate,
    CategoryCreate, CategoryUpdate,
    VariantCreate, VariantUpdate,
    ProductFilters
)

logger = logging.getLogger(__name__)


class ProductService:
    """Service for managing products and categories"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ======================
    # CATEGORY METHODS
    # ======================

    async def create_category(
        self,
        site_id: UUID,
        category_data: CategoryCreate
    ) -> Category:
        """Create new category"""
        # Check slug uniqueness for this site
        existing = await self.db.execute(
            select(Category).where(
                and_(
                    Category.site_id == site_id,
                    Category.slug == category_data.slug
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Category with slug '{category_data.slug}' already exists")

        # Verify parent category exists if specified
        if category_data.parent_category_id:
            parent = await self.db.execute(
                select(Category).where(
                    and_(
                        Category.category_id == category_data.parent_category_id,
                        Category.site_id == site_id
                    )
                )
            )
            if not parent.scalar_one_or_none():
                raise ValueError("Parent category not found")

        category = Category(
            site_id=site_id,
            **category_data.model_dump()
        )

        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)

        logger.info(f"Created category {category.category_id} ({category.name})")
        return category

    async def get_category(
        self,
        category_id: UUID,
        site_id: UUID
    ) -> Optional[Category]:
        """Get category by ID"""
        result = await self.db.execute(
            select(Category).where(
                and_(
                    Category.category_id == category_id,
                    Category.site_id == site_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_categories(
        self,
        site_id: UUID,
        parent_id: Optional[UUID] = None,
        active_only: bool = False
    ) -> List[Category]:
        """List categories for site"""
        query = select(Category).where(Category.site_id == site_id)

        if parent_id is not None:
            query = query.where(Category.parent_category_id == parent_id)

        if active_only:
            query = query.where(Category.is_active == True)

        query = query.order_by(Category.sort_order, Category.name)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_category(
        self,
        category_id: UUID,
        site_id: UUID,
        category_data: CategoryUpdate
    ) -> Optional[Category]:
        """Update category"""
        category = await self.get_category(category_id, site_id)
        if not category:
            return None

        # Check slug uniqueness if changing
        if category_data.slug and category_data.slug != category.slug:
            existing = await self.db.execute(
                select(Category).where(
                    and_(
                        Category.site_id == site_id,
                        Category.slug == category_data.slug,
                        Category.category_id != category_id
                    )
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Category with slug '{category_data.slug}' already exists")

        # Update fields
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        await self.db.flush()
        await self.db.refresh(category)

        return category

    async def delete_category(
        self,
        category_id: UUID,
        site_id: UUID
    ) -> bool:
        """Soft delete category (set inactive)"""
        category = await self.get_category(category_id, site_id)
        if not category:
            return False

        # Check if category has children
        children = await self.db.execute(
            select(Category).where(Category.parent_category_id == category_id)
        )
        if children.scalar_one_or_none():
            raise ValueError("Cannot delete category with subcategories")

        # Check if category has products
        products = await self.db.execute(
            select(Product).where(Product.category_id == category_id)
        )
        if products.scalar_one_or_none():
            raise ValueError("Cannot delete category with products")

        category.is_active = False
        await self.db.flush()

        return True

    # ======================
    # PRODUCT METHODS
    # ======================

    async def create_product(
        self,
        site_id: UUID,
        product_data: ProductCreate
    ) -> Product:
        """Create new product"""
        # Check slug uniqueness
        existing = await self.db.execute(
            select(Product).where(
                and_(
                    Product.site_id == site_id,
                    Product.slug == product_data.slug
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Product with slug '{product_data.slug}' already exists")

        # Check SKU uniqueness if provided
        if product_data.sku:
            existing_sku = await self.db.execute(
                select(Product).where(Product.sku == product_data.sku)
            )
            if existing_sku.scalar_one_or_none():
                raise ValueError(f"Product with SKU '{product_data.sku}' already exists")

        # Verify category exists if specified
        if product_data.category_id:
            category = await self.get_category(product_data.category_id, site_id)
            if not category:
                raise ValueError("Category not found")

        product = Product(
            site_id=site_id,
            **product_data.model_dump()
        )

        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)

        # Create stock history entry
        if product.track_inventory:
            await self._create_stock_history(
                product.product_id,
                None,
                'initial',
                product.stock_quantity,
                product.stock_quantity,
                "Initial stock"
            )

        logger.info(f"Created product {product.product_id} ({product.name})")
        return product

    async def get_product(
        self,
        product_id: UUID,
        site_id: UUID
    ) -> Optional[Product]:
        """Get product by ID"""
        result = await self.db.execute(
            select(Product).where(
                and_(
                    Product.product_id == product_id,
                    Product.site_id == site_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_product_by_slug(
        self,
        slug: str,
        site_id: UUID
    ) -> Optional[Product]:
        """Get product by slug"""
        result = await self.db.execute(
            select(Product).where(
                and_(
                    Product.slug == slug,
                    Product.site_id == site_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def search_products(
        self,
        site_id: UUID,
        filters: ProductFilters
    ) -> Tuple[List[Product], int]:
        """
        Search and filter products with pagination

        Returns:
            Tuple of (products, total_count)
        """
        # Base query
        query = select(Product).where(Product.site_id == site_id)

        # Apply filters
        if filters.category_id:
            query = query.where(Product.category_id == filters.category_id)

        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Product.name.ilike(search_term),
                    Product.description.ilike(search_term),
                    Product.short_description.ilike(search_term)
                )
            )

        if filters.tags:
            # Products with ANY of the specified tags
            query = query.where(Product.tags.overlap(filters.tags))

        if filters.min_price is not None:
            query = query.where(Product.price >= filters.min_price)

        if filters.max_price is not None:
            query = query.where(Product.price <= filters.max_price)

        if filters.is_featured is not None:
            query = query.where(Product.is_featured == filters.is_featured)

        if filters.in_stock:
            query = query.where(Product.stock_quantity > 0)

        # Always filter active products for public queries
        query = query.where(Product.is_active == True)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Apply sorting
        sort_column = getattr(Product, filters.sort_by, Product.created_at)
        if filters.sort_order == 'asc':
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        # Execute query
        result = await self.db.execute(query)
        products = list(result.scalars().all())

        return products, total

    async def update_product(
        self,
        product_id: UUID,
        site_id: UUID,
        product_data: ProductUpdate
    ) -> Optional[Product]:
        """Update product"""
        product = await self.get_product(product_id, site_id)
        if not product:
            return None

        # Check slug uniqueness if changing
        if product_data.slug and product_data.slug != product.slug:
            existing = await self.db.execute(
                select(Product).where(
                    and_(
                        Product.site_id == site_id,
                        Product.slug == product_data.slug,
                        Product.product_id != product_id
                    )
                )
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Product with slug '{product_data.slug}' already exists")

        # Track stock changes
        old_stock = product.stock_quantity

        # Update fields
        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)

        await self.db.flush()
        await self.db.refresh(product)

        # Log stock change if quantity changed
        if product.track_inventory and product_data.stock_quantity is not None and product_data.stock_quantity != old_stock:
            change = product.stock_quantity - old_stock
            await self._create_stock_history(
                product.product_id,
                None,
                'adjustment',
                change,
                product.stock_quantity,
                "Manual stock update"
            )

        return product

    async def delete_product(
        self,
        product_id: UUID,
        site_id: UUID
    ) -> bool:
        """Soft delete product (set inactive)"""
        product = await self.get_product(product_id, site_id)
        if not product:
            return False

        product.is_active = False
        await self.db.flush()

        logger.info(f"Deleted product {product_id}")
        return True

    # ======================
    # VARIANT METHODS
    # ======================

    async def create_variant(
        self,
        product_id: UUID,
        site_id: UUID,
        variant_data: VariantCreate
    ) -> ProductVariant:
        """Create product variant"""
        # Verify product exists
        product = await self.get_product(product_id, site_id)
        if not product:
            raise ValueError("Product not found")

        # Check SKU uniqueness if provided
        if variant_data.sku:
            existing = await self.db.execute(
                select(ProductVariant).where(ProductVariant.sku == variant_data.sku)
            )
            if existing.scalar_one_or_none():
                raise ValueError(f"Variant with SKU '{variant_data.sku}' already exists")

        variant = ProductVariant(
            product_id=product_id,
            **variant_data.model_dump()
        )

        self.db.add(variant)
        await self.db.flush()
        await self.db.refresh(variant)

        # Create stock history
        await self._create_stock_history(
            product_id,
            variant.variant_id,
            'initial',
            variant.stock_quantity,
            variant.stock_quantity,
            f"Initial stock for variant {variant.name}"
        )

        logger.info(f"Created variant {variant.variant_id} for product {product_id}")
        return variant

    async def list_variants(
        self,
        product_id: UUID,
        site_id: UUID
    ) -> List[ProductVariant]:
        """List all variants for a product"""
        # Verify product exists and belongs to site
        product = await self.get_product(product_id, site_id)
        if not product:
            return []

        result = await self.db.execute(
            select(ProductVariant).where(ProductVariant.product_id == product_id)
        )
        return list(result.scalars().all())

    async def update_variant(
        self,
        variant_id: UUID,
        variant_data: VariantUpdate
    ) -> Optional[ProductVariant]:
        """Update product variant"""
        result = await self.db.execute(
            select(ProductVariant).where(ProductVariant.variant_id == variant_id)
        )
        variant = result.scalar_one_or_none()

        if not variant:
            return None

        # Track stock changes
        old_stock = variant.stock_quantity

        # Update fields
        update_data = variant_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(variant, field, value)

        await self.db.flush()
        await self.db.refresh(variant)

        # Log stock change
        if variant_data.stock_quantity is not None and variant_data.stock_quantity != old_stock:
            change = variant.stock_quantity - old_stock
            await self._create_stock_history(
                variant.product_id,
                variant.variant_id,
                'adjustment',
                change,
                variant.stock_quantity,
                "Manual stock update"
            )

        return variant

    # ======================
    # STOCK METHODS
    # ======================

    async def check_stock(
        self,
        product_id: UUID,
        variant_id: Optional[UUID],
        quantity: int
    ) -> bool:
        """Check if requested quantity is available"""
        if variant_id:
            result = await self.db.execute(
                select(ProductVariant).where(ProductVariant.variant_id == variant_id)
            )
            variant = result.scalar_one_or_none()
            if not variant or not variant.is_active:
                return False
            return variant.stock_quantity >= quantity
        else:
            result = await self.db.execute(
                select(Product).where(Product.product_id == product_id)
            )
            product = result.scalar_one_or_none()
            if not product or not product.is_active:
                return False
            if not product.track_inventory:
                return True
            if product.allow_backorder:
                return True
            return product.stock_quantity >= quantity

    async def _create_stock_history(
        self,
        product_id: UUID,
        variant_id: Optional[UUID],
        movement_type: str,
        quantity_change: int,
        quantity_after: int,
        notes: str
    ):
        """Internal method to create stock history record"""
        history = StockHistory(
            product_id=product_id,
            variant_id=variant_id,
            movement_type=movement_type,
            quantity_change=quantity_change,
            quantity_after=quantity_after,
            notes=notes
        )
        self.db.add(history)
        await self.db.flush()
