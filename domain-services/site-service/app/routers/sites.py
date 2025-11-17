"""
Sites Router - API endpoints for site management

Following REST conventions from ARCHITECTURE.md:
- POST /v1/sites - Create site
- GET /v1/sites/{site_id} - Get site
- GET /v1/sites - List sites
- PUT /v1/sites/{site_id} - Update site
- PATCH /v1/sites/{site_id}/status - Update status
- GET /v1/sites/by-slug/{slug} - Get by slug (public)
- GET /v1/sites/by-domain/{domain} - Get by domain (public)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas import (
    SiteCreate,
    SiteUpdate,
    SiteResponse,
    SiteStatusUpdate,
    ErrorResponse
)
from app.services.site_service import SiteService
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post(
    "/",
    response_model=SiteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new site",
    description="Create a new website for the authenticated organization"
)
async def create_site(
    site_data: SiteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new site"""
    service = SiteService(db)

    try:
        site = await service.create_site(site_data, UUID(current_user['org_id']))
        return site
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create site: {str(e)}"
        )


@router.get(
    "/{site_id}",
    response_model=SiteResponse,
    summary="Get site by ID",
    description="Retrieve a site by its ID (requires ownership)"
)
async def get_site(
    site_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get site by ID"""
    service = SiteService(db)
    site = await service.get_site(site_id, UUID(current_user['org_id']))

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    return site


@router.get(
    "/",
    response_model=List[SiteResponse],
    summary="List all sites",
    description="List all sites for the authenticated organization"
)
async def list_sites(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all sites for current org"""
    service = SiteService(db)
    sites = await service.list_sites(UUID(current_user['org_id']))
    return sites


@router.put(
    "/{site_id}",
    response_model=SiteResponse,
    summary="Update site",
    description="Update site configuration"
)
async def update_site(
    site_id: UUID,
    site_data: SiteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update site"""
    service = SiteService(db)

    try:
        site = await service.update_site(site_id, site_data, UUID(current_user['org_id']))

        if not site:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Site not found"
            )

        return site
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch(
    "/{site_id}/status",
    response_model=SiteResponse,
    summary="Update site status",
    description="Change site status (draft, published, suspended)"
)
async def update_site_status(
    site_id: UUID,
    status_data: SiteStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update site status"""
    service = SiteService(db)
    site = await service.update_site_status(
        site_id,
        status_data.status,
        UUID(current_user['org_id'])
    )

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    return site


@router.delete(
    "/{site_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete site",
    description="Soft delete site (sets status to suspended)"
)
async def delete_site(
    site_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete site (soft delete)"""
    service = SiteService(db)
    success = await service.delete_site(site_id, UUID(current_user['org_id']))

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    return None


# ==================
# PUBLIC ENDPOINTS
# ==================

@router.get(
    "/by-slug/{slug}",
    response_model=SiteResponse,
    summary="Get site by slug",
    description="Retrieve a site by its slug (public endpoint for frontend)"
)
async def get_site_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get site by slug (public endpoint)"""
    service = SiteService(db)
    site = await service.get_site_by_slug(slug)

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site with slug '{slug}' not found"
        )

    # Only return published sites to public
    if site.status != 'published':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not available"
        )

    return site


@router.get(
    "/by-domain/{domain}",
    response_model=SiteResponse,
    summary="Get site by domain",
    description="Retrieve a site by its custom domain (public endpoint)"
)
async def get_site_by_domain(
    domain: str,
    db: AsyncSession = Depends(get_db)
):
    """Get site by custom domain (public endpoint)"""
    service = SiteService(db)
    site = await service.get_site_by_domain(domain)

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Site with domain '{domain}' not found"
        )

    # Only return published sites to public
    if site.status != 'published':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not available"
        )

    return site
