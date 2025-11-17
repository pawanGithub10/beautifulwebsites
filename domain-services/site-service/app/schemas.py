"""
Pydantic schemas for request/response validation

These schemas define the API contract for Site Service.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
import re


# ======================
# SITE SCHEMAS
# ======================

class SiteCreate(BaseModel):
    """Schema for creating a new site"""
    slug: str = Field(..., min_length=3, max_length=100, description="URL-friendly site identifier")
    site_type: str = Field(..., description="Type of website (departmental_store, salon, etc.)")
    template_id: Optional[UUID] = Field(None, description="Template to use for initial setup")
    domain: Optional[str] = Field(None, description="Custom domain (optional)")

    # SEO
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = Field(None)

    # Branding
    primary_color: Optional[str] = Field(None, description="Primary brand color (hex)")
    secondary_color: Optional[str] = Field(None, description="Secondary brand color (hex)")
    font_family: Optional[str] = Field(None)
    logo_url: Optional[str] = Field(None)
    favicon_url: Optional[str] = Field(None)

    # Configuration
    config: Dict[str, Any] = Field(default_factory=dict)

    @validator('slug')
    def validate_slug(cls, v):
        """Ensure slug is URL-friendly"""
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v

    @validator('primary_color', 'secondary_color')
    def validate_color(cls, v):
        """Ensure color is valid hex"""
        if v and not re.match(r'^#[0-9a-fA-F]{6}$', v):
            raise ValueError('Color must be a valid hex color (e.g., #3b82f6)')
        return v


class SiteUpdate(BaseModel):
    """Schema for updating a site"""
    slug: Optional[str] = Field(None, min_length=3, max_length=100)
    domain: Optional[str] = None
    meta_title: Optional[str] = Field(None, max_length=200)
    meta_description: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    font_family: Optional[str] = None
    logo_url: Optional[str] = None
    favicon_url: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

    @validator('slug')
    def validate_slug(cls, v):
        if v and not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v


class SiteResponse(BaseModel):
    """Schema for site response"""
    site_id: UUID
    org_id: UUID
    slug: str
    domain: Optional[str]
    site_type: str
    template_id: Optional[UUID]
    status: str
    meta_title: Optional[str]
    meta_description: Optional[str]
    favicon_url: Optional[str]
    logo_url: Optional[str]
    primary_color: str
    secondary_color: str
    font_family: str
    config: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SiteStatusUpdate(BaseModel):
    """Schema for updating site status"""
    status: str = Field(..., description="New status (draft, published, suspended)")

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['draft', 'published', 'suspended']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


# ======================
# TEMPLATE SCHEMAS
# ======================

class TemplateCreate(BaseModel):
    """Schema for creating a template"""
    template_name: str = Field(..., min_length=3, max_length=100)
    site_type: str = Field(..., description="Site type this template is for")
    layout_config: Dict[str, Any] = Field(..., description="Default sections and layout")
    style_config: Optional[Dict[str, Any]] = Field(None, description="Default colors and fonts")
    preview_url: Optional[str] = None
    is_premium: bool = False


class TemplateResponse(BaseModel):
    """Schema for template response"""
    template_id: UUID
    template_name: str
    site_type: str
    layout_config: Dict[str, Any]
    style_config: Optional[Dict[str, Any]]
    preview_url: Optional[str]
    is_premium: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ======================
# SITE SECTION SCHEMAS
# ======================

class SectionCreate(BaseModel):
    """Schema for creating a section"""
    page_path: str = Field(default='/', description="Page path (/, /about, etc.)")
    section_type: str = Field(..., description="Type of section (hero, product_grid, etc.)")
    section_order: int = Field(default=0, description="Order in which section appears")
    section_config: Dict[str, Any] = Field(..., description="Configuration props for this section")
    is_visible: bool = Field(default=True)


class SectionUpdate(BaseModel):
    """Schema for updating a section"""
    section_order: Optional[int] = None
    section_config: Optional[Dict[str, Any]] = None
    is_visible: Optional[bool] = None


class SectionResponse(BaseModel):
    """Schema for section response"""
    section_id: UUID
    site_id: UUID
    page_path: str
    section_type: str
    section_order: int
    section_config: Dict[str, Any]
    is_visible: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SectionReorderRequest(BaseModel):
    """Schema for reordering sections"""
    section_orders: Dict[UUID, int] = Field(..., description="Map of section_id to new order")


# ======================
# COMMON SCHEMAS
# ======================

class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str
    error_code: Optional[str] = None


class SuccessResponse(BaseModel):
    """Schema for generic success responses"""
    message: str
    data: Optional[Dict[str, Any]] = None
