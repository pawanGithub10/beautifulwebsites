"""
Availability Service - Calculate available time slots

Complex logic for:
- Getting provider working hours (recurring + overrides)
- Checking existing bookings
- Checking blocked slots
- Generating available time slots
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import date, time, datetime, timedelta
import logging

from app.models import (
    Service, Provider, RecurringSchedule, ProviderSchedule,
    BlockedSlot, Booking
)
from app.schemas import TimeSlot, AvailabilityQuery

logger = logging.getLogger(__name__)


class AvailabilityService:
    """Service for checking availability and generating time slots"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_available_slots(
        self,
        site_id: UUID,
        query: AvailabilityQuery
    ) -> List[TimeSlot]:
        """
        Get available time slots for a service on a specific date

        Algorithm:
        1. Get service details (duration, requires_provider)
        2. Get list of providers (specific or all who can provide service)
        3. For each provider:
           a. Get working hours for that day
           b. Get existing bookings
           c. Get blocked slots
           d. Calculate available slots
        4. Return aggregated slots
        """
        # Get service
        service = await self._get_service(query.service_id, site_id)
        if not service or not service.is_active:
            return []

        # Get providers
        if query.provider_id:
            providers = [await self._get_provider(query.provider_id, site_id)]
            if not providers[0]:
                return []
        else:
            # Get all providers who can provide this service
            providers = await self._get_providers_for_service(site_id, query.service_id)

        if not providers:
            return []

        all_slots = []

        # Calculate slots for each provider
        for provider in providers:
            if not provider.is_active or not provider.accepts_bookings:
                continue

            # Get provider's working hours for this date
            working_periods = await self._get_working_hours(
                provider.provider_id,
                query.date
            )

            if not working_periods:
                continue

            # Get existing bookings for this provider on this date
            bookings = await self._get_provider_bookings(
                provider.provider_id,
                query.date
            )

            # Get blocked slots for this provider on this date
            blocked_slots = await self._get_blocked_slots_for_date(
                site_id,
                provider.provider_id,
                query.date
            )

            # Calculate available slots
            slots = self._calculate_available_slots(
                working_periods=working_periods,
                service_duration=service.duration_minutes + service.buffer_minutes,
                existing_bookings=bookings,
                blocked_slots=blocked_slots,
                provider_id=provider.provider_id,
                provider_name=provider.name
            )

            all_slots.extend(slots)

        # Sort by start time
        all_slots.sort(key=lambda s: s.start_time)

        return all_slots

    async def _get_service(
        self,
        service_id: UUID,
        site_id: UUID
    ) -> Optional[Service]:
        """Get service"""
        result = await self.db.execute(
            select(Service).where(
                and_(
                    Service.service_id == service_id,
                    Service.site_id == site_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def _get_provider(
        self,
        provider_id: UUID,
        site_id: UUID
    ) -> Optional[Provider]:
        """Get provider"""
        result = await self.db.execute(
            select(Provider).where(
                and_(
                    Provider.provider_id == provider_id,
                    Provider.site_id == site_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def _get_providers_for_service(
        self,
        site_id: UUID,
        service_id: UUID
    ) -> List[Provider]:
        """Get all providers who can provide this service"""
        result = await self.db.execute(
            select(Provider).where(
                and_(
                    Provider.site_id == site_id,
                    Provider.is_active == True,
                    Provider.accepts_bookings == True
                )
            )
        )
        all_providers = list(result.scalars().all())

        # Filter by service_ids
        service_id_str = str(service_id)
        providers = [
            p for p in all_providers
            if service_id_str in [str(sid) for sid in p.service_ids]
        ]

        return providers

    async def _get_working_hours(
        self,
        provider_id: UUID,
        check_date: date
    ) -> List[Tuple[time, time]]:
        """
        Get working hours for provider on specific date

        Checks:
        1. Specific date override (ProviderSchedule)
        2. Recurring weekly schedule (RecurringSchedule)

        Returns list of (start_time, end_time) tuples
        """
        # Check for specific date override
        specific_result = await self.db.execute(
            select(ProviderSchedule).where(
                and_(
                    ProviderSchedule.provider_id == provider_id,
                    ProviderSchedule.date == check_date
                )
            )
        )
        specific_schedule = specific_result.scalar_one_or_none()

        if specific_schedule:
            if not specific_schedule.is_available:
                return []  # Provider marked as unavailable
            return [(specific_schedule.start_time, specific_schedule.end_time)]

        # Check recurring schedule
        day_of_week = check_date.weekday()  # 0=Monday, 6=Sunday

        recurring_result = await self.db.execute(
            select(RecurringSchedule).where(
                and_(
                    RecurringSchedule.provider_id == provider_id,
                    RecurringSchedule.day_of_week == day_of_week,
                    RecurringSchedule.is_active == True
                )
            ).order_by(RecurringSchedule.start_time)
        )
        recurring_schedules = list(recurring_result.scalars().all())

        return [(s.start_time, s.end_time) for s in recurring_schedules]

    async def _get_provider_bookings(
        self,
        provider_id: UUID,
        check_date: date
    ) -> List[Booking]:
        """Get existing bookings for provider on date"""
        result = await self.db.execute(
            select(Booking).where(
                and_(
                    Booking.provider_id == provider_id,
                    Booking.booking_date == check_date,
                    Booking.booking_status.in_(['confirmed', 'completed'])
                )
            ).order_by(Booking.start_time)
        )
        return list(result.scalars().all())

    async def _get_blocked_slots_for_date(
        self,
        site_id: UUID,
        provider_id: UUID,
        check_date: date
    ) -> List[BlockedSlot]:
        """Get blocked slots for provider on date"""
        # Convert date to datetime range
        start_dt = datetime.combine(check_date, time.min)
        end_dt = datetime.combine(check_date, time.max)

        result = await self.db.execute(
            select(BlockedSlot).where(
                and_(
                    BlockedSlot.site_id == site_id,
                    or_(
                        BlockedSlot.provider_id == provider_id,
                        BlockedSlot.provider_id == None  # Site-wide blocks
                    ),
                    BlockedSlot.start_datetime <= end_dt,
                    BlockedSlot.end_datetime >= start_dt
                )
            )
        )
        return list(result.scalars().all())

    def _calculate_available_slots(
        self,
        working_periods: List[Tuple[time, time]],
        service_duration: int,  # minutes
        existing_bookings: List[Booking],
        blocked_slots: List[BlockedSlot],
        provider_id: UUID,
        provider_name: str
    ) -> List[TimeSlot]:
        """
        Calculate available time slots

        Algorithm:
        1. For each working period (start_time, end_time):
           2. Generate all possible slots based on service duration
           3. Remove slots that overlap with bookings
           4. Remove slots that overlap with blocked slots
           5. Return remaining slots
        """
        available_slots = []

        for work_start, work_end in working_periods:
            # Convert to minutes since midnight for easier calculation
            work_start_minutes = work_start.hour * 60 + work_start.minute
            work_end_minutes = work_end.hour * 60 + work_end.minute

            # Generate all possible slots
            current_minutes = work_start_minutes
            while current_minutes + service_duration <= work_end_minutes:
                slot_start = time(hour=current_minutes // 60, minute=current_minutes % 60)
                slot_end_minutes = current_minutes + service_duration
                slot_end = time(hour=slot_end_minutes // 60, minute=slot_end_minutes % 60)

                # Check if slot is available
                if self._is_slot_available(
                    slot_start,
                    slot_end,
                    existing_bookings,
                    blocked_slots
                ):
                    available_slots.append(
                        TimeSlot(
                            start_time=slot_start,
                            end_time=slot_end,
                            provider_id=provider_id,
                            provider_name=provider_name,
                            available=True
                        )
                    )

                # Move to next slot (15-minute intervals)
                current_minutes += 15

        return available_slots

    def _is_slot_available(
        self,
        slot_start: time,
        slot_end: time,
        bookings: List[Booking],
        blocked_slots: List[BlockedSlot]
    ) -> bool:
        """Check if slot is available (no overlaps with bookings or blocks)"""
        # Check bookings
        for booking in bookings:
            if self._times_overlap(
                slot_start, slot_end,
                booking.start_time, booking.end_time
            ):
                return False

        # Check blocked slots
        for block in blocked_slots:
            block_start = block.start_datetime.time()
            block_end = block.end_datetime.time()

            if self._times_overlap(
                slot_start, slot_end,
                block_start, block_end
            ):
                return False

        return True

    def _times_overlap(
        self,
        start1: time,
        end1: time,
        start2: time,
        end2: time
    ) -> bool:
        """Check if two time ranges overlap"""
        # Convert to minutes for easier comparison
        start1_min = start1.hour * 60 + start1.minute
        end1_min = end1.hour * 60 + end1.minute
        start2_min = start2.hour * 60 + start2.minute
        end2_min = end2.hour * 60 + end2.minute

        # Check overlap
        return not (end1_min <= start2_min or start1_min >= end2_min)
