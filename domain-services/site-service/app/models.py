"""
Database models for Site Service

Following the schema defined in ARCHITECTURE.md:
- sites: Main site configuration
- templates: Reusable site templates
- site_sections: Dynamic page sections
"""

from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()


class Site(Base):
    """
    Site entity - represents a website instance

    Each site belongs to an organization and has its own:
    - Branding (colors, fonts, logo)
    - Configuration (features, settings)
    - Template and sections
    """
    __tablename__ = "sites"

    site_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Identification
    slug = Column(String(100), unique=True, nullable=False, index=True)
    domain = Column(String(255), unique=True, nullable=True, index=True)

    # Site Type & Template
    site_type = Column(String(50), nullable=False, index=True)  # departmental_store, salon, etc.
    template_id = Column(UUID(as_uuid=True), nullable=True)

    # Status
    status = Column(String(20), default='draft', index=True)  # draft, published, suspended

    # SEO & Meta
    meta_title = Column(String(200))
    meta_description = Column(Text)
    favicon_url = Column(String(500))
    logo_url = Column(String(500))

    # Branding
    primary_color = Column(String(7), default='#3b82f6')  # Hex color
    secondary_color = Column(String(7), default='#10b981')
    font_family = Column(String(100), default='Inter, sans-serif')

    # Flexible configuration
    config = Column(JSONB, default=dict, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Site(site_id={self.site_id}, slug={self.slug}, type={self.site_type})>"


class Template(Base):
    """
    Template entity - reusable website templates

    Templates define default layouts, sections, and styles for different site types.
    """
    __tablename__ = "templates"

    template_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_name = Column(String(100), nullable=False)
    site_type = Column(String(50), nullable=False, index=True)

    # Configuration
    layout_config = Column(JSONB, nullable=False)  # Default sections and order
    style_config = Column(JSONB)  # Default colors, fonts, spacing

    # Preview
    preview_url = Column(String(500))
    is_premium = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Template(template_id={self.template_id}, name={self.template_name})>"


class SiteSection(Base):
    """
    Site Section entity - dynamic page sections

    Sections are the building blocks of pages. Each section has:
    - Type (hero, product_grid, testimonials, etc.)
    - Configuration (props specific to that section type)
    - Order (for rendering)
    """
    __tablename__ = "site_sections"

    section_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Page location
    page_path = Column(String(200), default='/', nullable=False, index=True)  # '/', '/about', etc.

    # Section configuration
    section_type = Column(String(50), nullable=False)  # hero, product_grid, etc.
    section_order = Column(Integer, nullable=False, default=0)
    section_config = Column(JSONB, nullable=False)  # Props for this section instance

    # Visibility
    is_visible = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<SiteSection(section_id={self.section_id}, type={self.section_type}, page={self.page_path})>"
