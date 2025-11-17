"""
Site Service - Business logic for site management

This service layer handles:
- CRUD operations for sites
- Validation and business rules
- Event publishing
- Integration with core services
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from uuid import UUID
import logging

from app.models import Site, Template, SiteSection
from app.schemas import SiteCreate, SiteUpdate
from app.services.event_service import EventService
from app.services.core_services_client import BillingServiceClient

logger = logging.getLogger(__name__)


class SiteService:
    """Service for managing sites"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.event_service = EventService()

    async def create_site(
        self,
        site_data: SiteCreate,
        org_id: UUID
    ) -> Site:
        """
        Create a new site

        Args:
            site_data: Site creation data
            org_id: Organization ID from authenticated user

        Returns:
            Created site

        Raises:
            Exception: If slug already exists or quota exceeded
        """
        # 1. Check if slug already exists
        existing = await self.get_site_by_slug(site_data.slug)
        if existing:
            raise ValueError(f"Slug '{site_data.slug}' is already taken")

        # 2. Check billing quota (how many sites can this org create?)
        quota = await BillingServiceClient.check_quota(str(org_id), 'sites')
        if quota['current'] >= quota['limit']:
            raise ValueError(f"Site limit reached ({quota['limit']} sites)")

        # 3. If template_id provided, verify it exists
        if site_data.template_id:
            template = await self.get_template(site_data.template_id)
            if not template:
                raise ValueError("Template not found")

            # Verify template is for correct site type
            if template.site_type != site_data.site_type:
                raise ValueError(f"Template is for {template.site_type}, not {site_data.site_type}")

        # 4. Create site
        site = Site(
            org_id=org_id,
            slug=site_data.slug,
            site_type=site_data.site_type,
            template_id=site_data.template_id,
            domain=site_data.domain,
            meta_title=site_data.meta_title or site_data.slug.replace('-', ' ').title(),
            meta_description=site_data.meta_description,
            primary_color=site_data.primary_color or '#3b82f6',
            secondary_color=site_data.secondary_color or '#10b981',
            font_family=site_data.font_family or 'Inter, sans-serif',
            logo_url=site_data.logo_url,
            favicon_url=site_data.favicon_url,
            config=site_data.config or {},
            status='draft'
        )

        self.db.add(site)
        await self.db.flush()  # Get site_id without committing

        # 5. If template provided, create default sections
        if site_data.template_id and template:
            await self._create_sections_from_template(site.site_id, template)

        await self.db.commit()
        await self.db.refresh(site)

        # 6. Publish event
        await self.event_service.publish_site_created(site)

        # 7. Record usage in billing
        await BillingServiceClient.record_usage(str(org_id), 'sites', 1)

        logger.info(f"Created site {site.site_id} ({site.slug}) for org {org_id}")

        return site

    async def get_site(
        self,
        site_id: UUID,
        org_id: UUID
    ) -> Optional[Site]:
        """Get site by ID (with org check)"""
        result = await self.db.execute(
            select(Site).where(
                and_(
                    Site.site_id == site_id,
                    Site.org_id == org_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_site_by_slug(self, slug: str) -> Optional[Site]:
        """Get site by slug (public access)"""
        result = await self.db.execute(
            select(Site).where(Site.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_site_by_domain(self, domain: str) -> Optional[Site]:
        """Get site by custom domain (public access)"""
        result = await self.db.execute(
            select(Site).where(Site.domain == domain)
        )
        return result.scalar_one_or_none()

    async def list_sites(self, org_id: UUID) -> List[Site]:
        """List all sites for an organization"""
        result = await self.db.execute(
            select(Site)
            .where(Site.org_id == org_id)
            .order_by(Site.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_site(
        self,
        site_id: UUID,
        site_data: SiteUpdate,
        org_id: UUID
    ) -> Optional[Site]:
        """Update site"""
        site = await self.get_site(site_id, org_id)
        if not site:
            return None

        # Check slug uniqueness if changing
        if site_data.slug and site_data.slug != site.slug:
            existing = await self.get_site_by_slug(site_data.slug)
            if existing:
                raise ValueError(f"Slug '{site_data.slug}' is already taken")

        # Update fields
        update_data = site_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(site, field, value)

        await self.db.commit()
        await self.db.refresh(site)

        # Publish event
        await self.event_service.publish_site_updated(site)

        return site

    async def update_site_status(
        self,
        site_id: UUID,
        status: str,
        org_id: UUID
    ) -> Optional[Site]:
        """Update site status"""
        site = await self.get_site(site_id, org_id)
        if not site:
            return None

        old_status = site.status
        site.status = status

        await self.db.commit()
        await self.db.refresh(site)

        # Publish event
        if status == 'published' and old_status != 'published':
            await self.event_service.publish_site_published(site)

        return site

    async def delete_site(
        self,
        site_id: UUID,
        org_id: UUID
    ) -> bool:
        """Soft delete site (set status to suspended)"""
        site = await self.get_site(site_id, org_id)
        if not site:
            return False

        site.status = 'suspended'
        await self.db.commit()

        # Publish event
        await self.event_service.publish_site_deleted(site)

        return True

    async def get_template(self, template_id: UUID) -> Optional[Template]:
        """Get template by ID"""
        result = await self.db.execute(
            select(Template).where(Template.template_id == template_id)
        )
        return result.scalar_one_or_none()

    async def list_templates(
        self,
        site_type: Optional[str] = None
    ) -> List[Template]:
        """List available templates"""
        query = select(Template).order_by(Template.template_name)

        if site_type:
            query = query.where(Template.site_type == site_type)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def _create_sections_from_template(
        self,
        site_id: UUID,
        template: Template
    ):
        """Create default sections from template"""
        layout_config = template.layout_config
        sections = layout_config.get('sections', [])

        for idx, section_def in enumerate(sections):
            section = SiteSection(
                site_id=site_id,
                page_path='/',
                section_type=section_def['type'],
                section_order=idx,
                section_config=section_def.get('props', {}),
                is_visible=True
            )
            self.db.add(section)

        await self.db.flush()
