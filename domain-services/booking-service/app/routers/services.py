"""
Services Router - API endpoints for service catalog

Endpoints for managing services and categories
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas import (
    ServiceCategoryResponse, ServiceCategoryCreate, ServiceCategoryUpdate,
    ServiceResponse, ServiceCreate, ServiceUpdate, ServiceFilters
)
from app.services.service_service import ServiceManagementService

router = APIRouter()

# Categories
@router.post("/{site_id}/categories", response_model=ServiceCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(site_id: UUID, category_data: ServiceCategoryCreate, db: AsyncSession = Depends(get_db)):
    service = ServiceManagementService(db)
    try:
        category = await service.create_category(site_id, category_data)
        return category
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{site_id}/categories", response_model=List[ServiceCategoryResponse])
async def list_categories(site_id: UUID, parent_id: Optional[UUID] = Query(None), db: AsyncSession = Depends(get_db)):
    service = ServiceManagementService(db)
    categories = await service.list_categories(site_id, parent_id=parent_id)
    return categories

# Services
@router.post("/{site_id}/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(site_id: UUID, service_data: ServiceCreate, db: AsyncSession = Depends(get_db)):
    service_mgmt = ServiceManagementService(db)
    try:
        new_service = await service_mgmt.create_service(site_id, service_data)
        return new_service
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{site_id}/services", response_model=List[ServiceResponse])
async def search_services(
    site_id: UUID,
    category_id: Optional[UUID] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    filters = ServiceFilters(category_id=category_id, search=search, page=page, page_size=page_size)
    service = ServiceManagementService(db)
    services, total = await service.search_services(site_id, filters)
    return services

@router.get("/{site_id}/services/{service_id}", response_model=ServiceResponse)
async def get_service(site_id: UUID, service_id: UUID, db: AsyncSession = Depends(get_db)):
    service_mgmt = ServiceManagementService(db)
    service_obj = await service_mgmt.get_service(service_id, site_id)
    if not service_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return service_obj
