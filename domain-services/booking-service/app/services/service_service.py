"""
Service Management - Business logic for services and categories

Handles:
- Service category CRUD
- Service CRUD
- Service search and filtering
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional, Tuple
from uuid import UUID

from app.models import Service, ServiceCategory
from app.schemas import (
    ServiceCategoryCreate, ServiceCategoryUpdate,
    ServiceCreate, ServiceUpdate, ServiceFilters
)


class ServiceManagementService:
    """Service for managing services and categories"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ======================
    # CATEGORY OPERATIONS
    # ======================

    async def create_category(
        self,
        site_id: UUID,
        category_data: ServiceCategoryCreate
    ) -> ServiceCategory:
        """Create service category"""
        # Check if parent exists
        if category_data.parent_id:
            parent = await self.get_category(category_data.parent_id, site_id)
            if not parent:
                raise ValueError("Parent category not found")

        # Check slug uniqueness
        existing = await self.db.execute(
            select(ServiceCategory).where(
                and_(
                    ServiceCategory.site_id == site_id,
                    ServiceCategory.slug == category_data.slug
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Category with slug '{category_data.slug}' already exists")

        category = ServiceCategory(
            site_id=site_id,
            **category_data.model_dump()
        )

        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)

        return category

    async def get_category(
        self,
        category_id: UUID,
        site_id: UUID
    ) -> Optional[ServiceCategory]:
        """Get category by ID"""
        result = await self.db.execute(
            select(ServiceCategory).where(
                and_(
                    ServiceCategory.category_id == category_id,
                    ServiceCategory.site_id == site_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_categories(
        self,
        site_id: UUID,
        parent_id: Optional[UUID] = None,
        active_only: bool = True
    ) -> List[ServiceCategory]:
        """List categories"""
        conditions = [ServiceCategory.site_id == site_id]

        if active_only:
            conditions.append(ServiceCategory.is_active == True)

        if parent_id is not None:
            conditions.append(ServiceCategory.parent_id == parent_id)

        result = await self.db.execute(
            select(ServiceCategory)
            .where(and_(*conditions))
            .order_by(ServiceCategory.display_order, ServiceCategory.name)
        )
        return list(result.scalars().all())

    async def update_category(
        self,
        category_id: UUID,
        site_id: UUID,
        category_data: ServiceCategoryUpdate
    ) -> Optional[ServiceCategory]:
        """Update category"""
        category = await self.get_category(category_id, site_id)
        if not category:
            return None

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
        """Soft delete category"""
        category = await self.get_category(category_id, site_id)
        if not category:
            return False

        # Check if has children
        children = await self.list_categories(site_id, parent_id=category_id, active_only=False)
        if children:
            raise ValueError("Cannot delete category with subcategories")

        category.is_active = False
        await self.db.flush()

        return True

    # ======================
    # SERVICE OPERATIONS
    # ======================

    async def create_service(
        self,
        site_id: UUID,
        service_data: ServiceCreate
    ) -> Service:
        """Create service"""
        # Check category exists
        if service_data.category_id:
            category = await self.get_category(service_data.category_id, site_id)
            if not category:
                raise ValueError("Category not found")

        # Check slug uniqueness
        existing = await self.db.execute(
            select(Service).where(
                and_(
                    Service.site_id == site_id,
                    Service.slug == service_data.slug
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Service with slug '{service_data.slug}' already exists")

        service = Service(
            site_id=site_id,
            **service_data.model_dump()
        )

        self.db.add(service)
        await self.db.flush()
        await self.db.refresh(service)

        return service

    async def get_service(
        self,
        service_id: UUID,
        site_id: UUID
    ) -> Optional[Service]:
        """Get service by ID"""
        result = await self.db.execute(
            select(Service).where(
                and_(
                    Service.service_id == service_id,
                    Service.site_id == site_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_service_by_slug(
        self,
        slug: str,
        site_id: UUID
    ) -> Optional[Service]:
        """Get service by slug"""
        result = await self.db.execute(
            select(Service).where(
                and_(
                    Service.slug == slug,
                    Service.site_id == site_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def search_services(
        self,
        site_id: UUID,
        filters: ServiceFilters
    ) -> Tuple[List[Service], int]:
        """Search services with filters and pagination"""
        # Base conditions
        conditions = [
            Service.site_id == site_id,
            Service.is_active == True
        ]

        # Apply filters
        if filters.category_id:
            conditions.append(Service.category_id == filters.category_id)

        if filters.search:
            search_term = f"%{filters.search}%"
            conditions.append(
                or_(
                    Service.name.ilike(search_term),
                    Service.description.ilike(search_term),
                    Service.short_description.ilike(search_term)
                )
            )

        if filters.tags:
            # JSONB array contains
            for tag in filters.tags:
                conditions.append(Service.tags.contains([tag]))

        if filters.min_price is not None:
            conditions.append(Service.price >= filters.min_price)

        if filters.max_price is not None:
            conditions.append(Service.price <= filters.max_price)

        if filters.is_featured is not None:
            conditions.append(Service.is_featured == filters.is_featured)

        # Count total
        count_query = select(func.count()).select_from(Service).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Build query
        query = select(Service).where(and_(*conditions))

        # Sorting
        if filters.sort_by == "price":
            order_field = Service.price
        elif filters.sort_by == "name":
            order_field = Service.name
        else:
            order_field = Service.created_at

        if filters.sort_order == "asc":
            query = query.order_by(order_field.asc())
        else:
            query = query.order_by(order_field.desc())

        # Pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        # Execute
        result = await self.db.execute(query)
        services = list(result.scalars().all())

        return services, total

    async def update_service(
        self,
        service_id: UUID,
        site_id: UUID,
        service_data: ServiceUpdate
    ) -> Optional[Service]:
        """Update service"""
        service = await self.get_service(service_id, site_id)
        if not service:
            return None

        # Update fields
        update_data = service_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(service, field, value)

        await self.db.flush()
        await self.db.refresh(service)

        return service

    async def delete_service(
        self,
        service_id: UUID,
        site_id: UUID
    ) -> bool:
        """Soft delete service"""
        service = await self.get_service(service_id, site_id)
        if not service:
            return False

        service.is_active = False
        await self.db.flush()

        return True
