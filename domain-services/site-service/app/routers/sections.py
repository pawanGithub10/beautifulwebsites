"""
Sections Router - API endpoints for site section management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import SiteSection, Site
from app.schemas import (
    SectionCreate,
    SectionUpdate,
    SectionResponse,
    SectionReorderRequest
)
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post(
    "/{site_id}/sections",
    response_model=SectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add section to site",
    description="Add a new section to a page"
)
async def create_section(
    site_id: UUID,
    section_data: SectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Add section to site"""
    # Verify site ownership
    result = await db.execute(
        select(Site).where(
            and_(
                Site.site_id == site_id,
                Site.org_id == UUID(current_user['org_id'])
            )
        )
    )
    site = result.scalar_one_or_none()

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    # Create section
    section = SiteSection(
        site_id=site_id,
        page_path=section_data.page_path,
        section_type=section_data.section_type,
        section_order=section_data.section_order,
        section_config=section_data.section_config,
        is_visible=section_data.is_visible
    )

    db.add(section)
    await db.commit()
    await db.refresh(section)

    return section


@router.get(
    "/{site_id}/pages/{page_path:path}",
    response_model=List[SectionResponse],
    summary="Get page sections",
    description="Get all sections for a specific page"
)
async def get_page_sections(
    site_id: UUID,
    page_path: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all sections for a page (public endpoint)"""
    # Normalize page path
    if not page_path.startswith('/'):
        page_path = '/' + page_path

    result = await db.execute(
        select(SiteSection)
        .where(
            and_(
                SiteSection.site_id == site_id,
                SiteSection.page_path == page_path
            )
        )
        .order_by(SiteSection.section_order)
    )

    sections = list(result.scalars().all())
    return sections


@router.put(
    "/{site_id}/sections/{section_id}",
    response_model=SectionResponse,
    summary="Update section",
    description="Update section configuration"
)
async def update_section(
    site_id: UUID,
    section_id: UUID,
    section_data: SectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update section"""
    # Verify site ownership
    result = await db.execute(
        select(Site).where(
            and_(
                Site.site_id == site_id,
                Site.org_id == UUID(current_user['org_id'])
            )
        )
    )
    site = result.scalar_one_or_none()

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    # Get section
    result = await db.execute(
        select(SiteSection).where(
            and_(
                SiteSection.section_id == section_id,
                SiteSection.site_id == site_id
            )
        )
    )
    section = result.scalar_one_or_none()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )

    # Update fields
    update_data = section_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(section, field, value)

    await db.commit()
    await db.refresh(section)

    return section


@router.delete(
    "/{site_id}/sections/{section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete section",
    description="Remove a section from a page"
)
async def delete_section(
    site_id: UUID,
    section_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete section"""
    # Verify site ownership
    result = await db.execute(
        select(Site).where(
            and_(
                Site.site_id == site_id,
                Site.org_id == UUID(current_user['org_id'])
            )
        )
    )
    site = result.scalar_one_or_none()

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    # Get and delete section
    result = await db.execute(
        select(SiteSection).where(
            and_(
                SiteSection.section_id == section_id,
                SiteSection.site_id == site_id
            )
        )
    )
    section = result.scalar_one_or_none()

    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )

    await db.delete(section)
    await db.commit()

    return None


@router.post(
    "/{site_id}/sections/reorder",
    status_code=status.HTTP_200_OK,
    summary="Reorder sections",
    description="Update the order of multiple sections at once"
)
async def reorder_sections(
    site_id: UUID,
    reorder_data: SectionReorderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Reorder sections"""
    # Verify site ownership
    result = await db.execute(
        select(Site).where(
            and_(
                Site.site_id == site_id,
                Site.org_id == UUID(current_user['org_id'])
            )
        )
    )
    site = result.scalar_one_or_none()

    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    # Update section orders
    for section_id, new_order in reorder_data.section_orders.items():
        result = await db.execute(
            select(SiteSection).where(
                and_(
                    SiteSection.section_id == section_id,
                    SiteSection.site_id == site_id
                )
            )
        )
        section = result.scalar_one_or_none()

        if section:
            section.section_order = new_order

    await db.commit()

    return {"message": "Sections reordered successfully"}
