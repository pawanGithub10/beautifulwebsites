"""
Templates Router - API endpoints for template management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from app.database import get_db
from app.schemas import TemplateCreate, TemplateResponse
from app.services.site_service import SiteService
from app.middleware.auth import get_current_user

router = APIRouter()


@router.get(
    "/",
    response_model=List[TemplateResponse],
    summary="List templates",
    description="List available website templates"
)
async def list_templates(
    site_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List templates (optionally filtered by site type)"""
    service = SiteService(db)
    templates = await service.list_templates(site_type)
    return templates


@router.get(
    "/{template_id}",
    response_model=TemplateResponse,
    summary="Get template",
    description="Get template details by ID"
)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get template by ID"""
    service = SiteService(db)
    template = await service.get_template(template_id)

    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )

    return template
