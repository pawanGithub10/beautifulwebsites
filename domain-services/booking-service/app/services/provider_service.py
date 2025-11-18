"""
Provider Management - Business logic for providers and schedules

Handles:
- Provider CRUD
- Recurring weekly schedules
- Specific date overrides
- Blocked time slots
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from typing import List, Optional
from uuid import UUID
from datetime import date, time, datetime

from app.models import Provider, RecurringSchedule, ProviderSchedule, BlockedSlot
from app.schemas import (
    ProviderCreate, ProviderUpdate,
    RecurringScheduleCreate, RecurringScheduleUpdate,
    ProviderScheduleCreate, ProviderScheduleUpdate,
    BlockedSlotCreate
)


class ProviderManagementService:
    """Service for managing providers and their schedules"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ======================
    # PROVIDER OPERATIONS
    # ======================

    async def create_provider(
        self,
        site_id: UUID,
        provider_data: ProviderCreate
    ) -> Provider:
        """Create provider"""
        provider = Provider(
            site_id=site_id,
            **provider_data.model_dump()
        )

        self.db.add(provider)
        await self.db.flush()
        await self.db.refresh(provider)

        return provider

    async def get_provider(
        self,
        provider_id: UUID,
        site_id: UUID
    ) -> Optional[Provider]:
        """Get provider by ID"""
        result = await self.db.execute(
            select(Provider).where(
                and_(
                    Provider.provider_id == provider_id,
                    Provider.site_id == site_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_providers(
        self,
        site_id: UUID,
        service_id: Optional[UUID] = None,
        active_only: bool = True,
        accepts_bookings_only: bool = False
    ) -> List[Provider]:
        """List providers"""
        conditions = [Provider.site_id == site_id]

        if active_only:
            conditions.append(Provider.is_active == True)

        if accepts_bookings_only:
            conditions.append(Provider.accepts_bookings == True)

        result = await self.db.execute(
            select(Provider)
            .where(and_(*conditions))
            .order_by(Provider.name)
        )
        providers = list(result.scalars().all())

        # Filter by service if specified
        if service_id:
            providers = [
                p for p in providers
                if str(service_id) in [str(sid) for sid in p.service_ids]
            ]

        return providers

    async def update_provider(
        self,
        provider_id: UUID,
        site_id: UUID,
        provider_data: ProviderUpdate
    ) -> Optional[Provider]:
        """Update provider"""
        provider = await self.get_provider(provider_id, site_id)
        if not provider:
            return None

        # Update fields
        update_data = provider_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(provider, field, value)

        await self.db.flush()
        await self.db.refresh(provider)

        return provider

    async def delete_provider(
        self,
        provider_id: UUID,
        site_id: UUID
    ) -> bool:
        """Soft delete provider"""
        provider = await self.get_provider(provider_id, site_id)
        if not provider:
            return False

        provider.is_active = False
        await self.db.flush()

        return True

    # ======================
    # RECURRING SCHEDULE OPERATIONS
    # ======================

    async def create_recurring_schedule(
        self,
        provider_id: UUID,
        site_id: UUID,
        schedule_data: RecurringScheduleCreate
    ) -> RecurringSchedule:
        """Create recurring weekly schedule"""
        # Verify provider exists
        provider = await self.get_provider(provider_id, site_id)
        if not provider:
            raise ValueError("Provider not found")

        schedule = RecurringSchedule(
            provider_id=provider_id,
            **schedule_data.model_dump()
        )

        self.db.add(schedule)
        await self.db.flush()
        await self.db.refresh(schedule)

        return schedule

    async def get_recurring_schedules(
        self,
        provider_id: UUID,
        day_of_week: Optional[int] = None
    ) -> List[RecurringSchedule]:
        """Get recurring schedules for provider"""
        conditions = [
            RecurringSchedule.provider_id == provider_id,
            RecurringSchedule.is_active == True
        ]

        if day_of_week is not None:
            conditions.append(RecurringSchedule.day_of_week == day_of_week)

        result = await self.db.execute(
            select(RecurringSchedule)
            .where(and_(*conditions))
            .order_by(RecurringSchedule.day_of_week, RecurringSchedule.start_time)
        )
        return list(result.scalars().all())

    async def update_recurring_schedule(
        self,
        schedule_id: UUID,
        schedule_data: RecurringScheduleUpdate
    ) -> Optional[RecurringSchedule]:
        """Update recurring schedule"""
        result = await self.db.execute(
            select(RecurringSchedule).where(
                RecurringSchedule.schedule_id == schedule_id
            )
        )
        schedule = result.scalar_one_or_none()

        if not schedule:
            return None

        # Update fields
        update_data = schedule_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(schedule, field, value)

        await self.db.flush()
        await self.db.refresh(schedule)

        return schedule

    async def delete_recurring_schedule(
        self,
        schedule_id: UUID
    ) -> bool:
        """Delete recurring schedule"""
        result = await self.db.execute(
            delete(RecurringSchedule).where(
                RecurringSchedule.schedule_id == schedule_id
            )
        )
        return result.rowcount > 0

    # ======================
    # SPECIFIC DATE SCHEDULE OPERATIONS
    # ======================

    async def create_provider_schedule(
        self,
        provider_id: UUID,
        site_id: UUID,
        schedule_data: ProviderScheduleCreate
    ) -> ProviderSchedule:
        """Create specific date schedule override"""
        # Verify provider exists
        provider = await self.get_provider(provider_id, site_id)
        if not provider:
            raise ValueError("Provider not found")

        # Check if schedule already exists for this date
        existing = await self.db.execute(
            select(ProviderSchedule).where(
                and_(
                    ProviderSchedule.provider_id == provider_id,
                    ProviderSchedule.date == schedule_data.date
                )
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError(f"Schedule already exists for {schedule_data.date}")

        schedule = ProviderSchedule(
            provider_id=provider_id,
            **schedule_data.model_dump()
        )

        self.db.add(schedule)
        await self.db.flush()
        await self.db.refresh(schedule)

        return schedule

    async def get_provider_schedule(
        self,
        provider_id: UUID,
        schedule_date: date
    ) -> Optional[ProviderSchedule]:
        """Get schedule for specific date"""
        result = await self.db.execute(
            select(ProviderSchedule).where(
                and_(
                    ProviderSchedule.provider_id == provider_id,
                    ProviderSchedule.date == schedule_date
                )
            )
        )
        return result.scalar_one_or_none()

    async def update_provider_schedule(
        self,
        schedule_id: UUID,
        schedule_data: ProviderScheduleUpdate
    ) -> Optional[ProviderSchedule]:
        """Update specific date schedule"""
        result = await self.db.execute(
            select(ProviderSchedule).where(
                ProviderSchedule.schedule_id == schedule_id
            )
        )
        schedule = result.scalar_one_or_none()

        if not schedule:
            return None

        # Update fields
        update_data = schedule_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(schedule, field, value)

        await self.db.flush()
        await self.db.refresh(schedule)

        return schedule

    async def delete_provider_schedule(
        self,
        schedule_id: UUID
    ) -> bool:
        """Delete specific date schedule"""
        result = await self.db.execute(
            delete(ProviderSchedule).where(
                ProviderSchedule.schedule_id == schedule_id
            )
        )
        return result.rowcount > 0

    # ======================
    # BLOCKED SLOT OPERATIONS
    # ======================

    async def create_blocked_slot(
        self,
        site_id: UUID,
        blocked_data: BlockedSlotCreate,
        created_by: Optional[UUID] = None
    ) -> BlockedSlot:
        """Create blocked time slot"""
        # Verify provider if specified
        if blocked_data.provider_id:
            provider = await self.get_provider(blocked_data.provider_id, site_id)
            if not provider:
                raise ValueError("Provider not found")

        blocked_slot = BlockedSlot(
            site_id=site_id,
            created_by_user_id=created_by,
            **blocked_data.model_dump()
        )

        self.db.add(blocked_slot)
        await self.db.flush()
        await self.db.refresh(blocked_slot)

        return blocked_slot

    async def get_blocked_slots(
        self,
        site_id: UUID,
        provider_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[BlockedSlot]:
        """Get blocked slots"""
        conditions = [BlockedSlot.site_id == site_id]

        if provider_id:
            conditions.append(
                or_(
                    BlockedSlot.provider_id == provider_id,
                    BlockedSlot.provider_id == None  # Site-wide blocks
                )
            )

        if start_date:
            conditions.append(BlockedSlot.end_datetime >= start_date)

        if end_date:
            conditions.append(BlockedSlot.start_datetime <= end_date)

        result = await self.db.execute(
            select(BlockedSlot)
            .where(and_(*conditions))
            .order_by(BlockedSlot.start_datetime)
        )
        return list(result.scalars().all())

    async def delete_blocked_slot(
        self,
        blocked_slot_id: UUID,
        site_id: UUID
    ) -> bool:
        """Delete blocked slot"""
        result = await self.db.execute(
            delete(BlockedSlot).where(
                and_(
                    BlockedSlot.blocked_slot_id == blocked_slot_id,
                    BlockedSlot.site_id == site_id
                )
            )
        )
        return result.rowcount > 0
