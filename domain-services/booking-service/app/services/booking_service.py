"""
Booking Service - Core booking management logic

Handles:
- Booking creation with validation
- Booking updates (reschedule)
- Booking status management
- Cancellation with policies
- Booking history
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import date, time, datetime, timedelta
from decimal import Decimal
import logging

from app.models import Booking, BookingHistory, Service, Provider
from app.schemas import (
    BookingCreate, BookingUpdate, BookingStatusUpdate,
    BookingCancellation, BookingFilters
)
from app.config import settings

logger = logging.getLogger(__name__)


class BookingManagementService:
    """Service for managing bookings"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_booking(
        self,
        site_id: UUID,
        booking_data: BookingCreate,
        user_id: Optional[UUID] = None
    ) -> Booking:
        """
        Create new booking

        Steps:
        1. Validate service exists
        2. Validate provider (if specified)
        3. Check slot availability
        4. Generate unique booking number
        5. Create booking with service/provider snapshots
        6. Create initial history entry
        """
        # Get service
        service = await self._get_service(booking_data.service_id, site_id)
        if not service or not service.is_active:
            raise ValueError("Service not found or inactive")

        # Get provider (if specified)
        provider = None
        provider_name = None
        if booking_data.provider_id:
            provider = await self._get_provider(booking_data.provider_id, site_id)
            if not provider or not provider.is_active:
                raise ValueError("Provider not found or inactive")
            provider_name = provider.name

        # Check if service requires provider
        if service.requires_provider and not booking_data.provider_id:
            raise ValueError("This service requires a provider selection")

        # Check booking date is not in the past
        if booking_data.booking_date < date.today():
            raise ValueError("Cannot book appointments in the past")

        # Check booking is within advance booking window
        max_advance_date = date.today() + timedelta(days=settings.BOOKING_ADVANCE_DAYS)
        if booking_data.booking_date > max_advance_date:
            raise ValueError(
                f"Cannot book more than {settings.BOOKING_ADVANCE_DAYS} days in advance"
            )

        # Calculate end time
        duration = service.duration_minutes
        start_dt = datetime.combine(booking_data.booking_date, booking_data.start_time)
        end_dt = start_dt + timedelta(minutes=duration)
        end_time = end_dt.time()

        # Check slot availability
        await self._check_slot_availability(
            provider_id=booking_data.provider_id,
            booking_date=booking_data.booking_date,
            start_time=booking_data.start_time,
            end_time=end_time,
            service_duration=duration
        )

        # Generate booking number
        booking_number = await self._generate_booking_number(site_id)

        # Create booking
        booking = Booking(
            site_id=site_id,
            user_id=user_id,
            booking_number=booking_number,
            service_id=booking_data.service_id,
            provider_id=booking_data.provider_id,
            booking_date=booking_data.booking_date,
            start_time=booking_data.start_time,
            end_time=end_time,
            duration_minutes=duration,
            customer_name=booking_data.customer_name,
            customer_email=booking_data.customer_email,
            customer_phone=booking_data.customer_phone,
            customer_notes=booking_data.customer_notes,
            service_price=service.price,
            service_name=service.name,
            provider_name=provider_name,
            payment_method=booking_data.payment_method,
            payment_status='pending',
            booking_status='confirmed',
            confirmed_at=datetime.utcnow()
        )

        self.db.add(booking)
        await self.db.flush()
        await self.db.refresh(booking)

        # Create history entry
        await self._create_history(
            booking.booking_id,
            old_status=None,
            new_status='confirmed',
            notes="Booking created"
        )

        return booking

    async def _check_slot_availability(
        self,
        provider_id: Optional[UUID],
        booking_date: date,
        start_time: time,
        end_time: time,
        service_duration: int
    ):
        """Check if slot is available (no overlapping bookings)"""
        if not provider_id:
            return  # No provider, can't check overlaps

        # Check for overlapping bookings
        result = await self.db.execute(
            select(Booking).where(
                and_(
                    Booking.provider_id == provider_id,
                    Booking.booking_date == booking_date,
                    Booking.booking_status.in_(['confirmed', 'completed']),
                    # Check overlap: new booking overlaps if it starts before existing ends
                    # and ends after existing starts
                    or_(
                        and_(
                            Booking.start_time < end_time,
                            Booking.end_time > start_time
                        )
                    )
                )
            )
        )
        overlapping = result.scalars().all()

        if overlapping:
            raise ValueError(
                f"Time slot not available - conflicts with existing booking at "
                f"{overlapping[0].start_time.strftime('%H:%M')}"
            )

    async def _generate_booking_number(self, site_id: UUID) -> str:
        """Generate unique booking number (BKG-YYYYMMDD-XXXXX)"""
        today_str = datetime.utcnow().strftime("%Y%m%d")
        prefix = f"BKG-{today_str}"

        # Find highest number for today
        result = await self.db.execute(
            select(func.count()).select_from(Booking).where(
                and_(
                    Booking.site_id == site_id,
                    Booking.booking_number.like(f"{prefix}%")
                )
            )
        )
        count = result.scalar()

        # Generate number
        seq_num = str(count + 1).zfill(5)
        return f"{prefix}-{seq_num}"

    async def get_booking(
        self,
        booking_id: UUID,
        site_id: UUID
    ) -> Optional[Booking]:
        """Get booking by ID"""
        result = await self.db.execute(
            select(Booking).where(
                and_(
                    Booking.booking_id == booking_id,
                    Booking.site_id == site_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_booking_by_number(
        self,
        booking_number: str,
        site_id: UUID
    ) -> Optional[Booking]:
        """Get booking by booking number"""
        result = await self.db.execute(
            select(Booking).where(
                and_(
                    Booking.booking_number == booking_number,
                    Booking.site_id == site_id
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_bookings(
        self,
        site_id: UUID,
        filters: BookingFilters
    ) -> Tuple[List[Booking], int]:
        """List bookings with filters and pagination"""
        # Base conditions
        conditions = [Booking.site_id == site_id]

        # Apply filters
        if filters.booking_status:
            conditions.append(Booking.booking_status == filters.booking_status)

        if filters.payment_status:
            conditions.append(Booking.payment_status == filters.payment_status)

        if filters.provider_id:
            conditions.append(Booking.provider_id == filters.provider_id)

        if filters.service_id:
            conditions.append(Booking.service_id == filters.service_id)

        if filters.customer_phone:
            conditions.append(Booking.customer_phone == filters.customer_phone)

        if filters.date_from:
            conditions.append(Booking.booking_date >= filters.date_from)

        if filters.date_to:
            conditions.append(Booking.booking_date <= filters.date_to)

        # Count total
        count_query = select(func.count()).select_from(Booking).where(and_(*conditions))
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Build query
        query = (
            select(Booking)
            .where(and_(*conditions))
            .order_by(Booking.booking_date.desc(), Booking.start_time.desc())
        )

        # Pagination
        offset = (filters.page - 1) * filters.page_size
        query = query.offset(offset).limit(filters.page_size)

        # Execute
        result = await self.db.execute(query)
        bookings = list(result.scalars().all())

        return bookings, total

    async def update_booking(
        self,
        booking_id: UUID,
        site_id: UUID,
        booking_data: BookingUpdate
    ) -> Optional[Booking]:
        """Update booking (reschedule)"""
        booking = await self.get_booking(booking_id, site_id)
        if not booking:
            return None

        # Can only update confirmed bookings
        if booking.booking_status != 'confirmed':
            raise ValueError(f"Cannot update booking with status '{booking.booking_status}'")

        # If rescheduling, check availability
        if booking_data.booking_date or booking_data.start_time:
            new_date = booking_data.booking_date or booking.booking_date
            new_start = booking_data.start_time or booking.start_time

            # Calculate new end time
            start_dt = datetime.combine(new_date, new_start)
            end_dt = start_dt + timedelta(minutes=booking.duration_minutes)
            new_end = end_dt.time()

            await self._check_slot_availability(
                provider_id=booking.provider_id,
                booking_date=new_date,
                start_time=new_start,
                end_time=new_end,
                service_duration=booking.duration_minutes
            )

            # Update times
            booking.booking_date = new_date
            booking.start_time = new_start
            booking.end_time = new_end

        # Update other fields
        update_data = booking_data.model_dump(exclude_unset=True, exclude={'booking_date', 'start_time'})
        for field, value in update_data.items():
            setattr(booking, field, value)

        await self.db.flush()
        await self.db.refresh(booking)

        return booking

    async def update_booking_status(
        self,
        booking_id: UUID,
        site_id: UUID,
        status_data: BookingStatusUpdate,
        changed_by: Optional[UUID] = None
    ) -> Optional[Booking]:
        """Update booking status"""
        booking = await self.get_booking(booking_id, site_id)
        if not booking:
            return None

        old_status = booking.booking_status
        new_status = status_data.booking_status

        # Validate status transition
        if not self._is_valid_status_transition(old_status, new_status):
            raise ValueError(f"Invalid status transition: {old_status} -> {new_status}")

        # Update status
        booking.booking_status = new_status

        # Update timestamps
        if new_status == 'completed':
            booking.completed_at = datetime.utcnow()
        elif new_status.startswith('cancelled'):
            booking.cancelled_at = datetime.utcnow()

        await self.db.flush()
        await self.db.refresh(booking)

        # Create history entry
        await self._create_history(
            booking.booking_id,
            old_status=old_status,
            new_status=new_status,
            notes=status_data.notes,
            changed_by=changed_by
        )

        return booking

    async def cancel_booking(
        self,
        booking_id: UUID,
        site_id: UUID,
        cancellation_data: BookingCancellation,
        cancelled_by_customer: bool = True
    ) -> Optional[Booking]:
        """Cancel booking with policy enforcement"""
        booking = await self.get_booking(booking_id, site_id)
        if not booking:
            return None

        # Check if already cancelled
        if booking.booking_status.startswith('cancelled'):
            raise ValueError("Booking already cancelled")

        # Check if completed
        if booking.booking_status == 'completed':
            raise ValueError("Cannot cancel completed booking")

        # Check cancellation window
        booking_datetime = datetime.combine(booking.booking_date, booking.start_time)
        hours_before = (booking_datetime - datetime.utcnow()).total_seconds() / 3600

        if hours_before < settings.CANCELLATION_HOURS_BEFORE:
            # Apply cancellation fee
            cancellation_fee = cancellation_data.cancellation_fee
        else:
            # Free cancellation
            cancellation_fee = Decimal('0')

        # Update booking
        booking.booking_status = (
            'cancelled_by_customer' if cancelled_by_customer
            else 'cancelled_by_business'
        )
        booking.cancelled_at = datetime.utcnow()
        booking.cancellation_reason = cancellation_data.reason
        booking.cancellation_fee = cancellation_fee

        await self.db.flush()
        await self.db.refresh(booking)

        # Create history entry
        await self._create_history(
            booking.booking_id,
            old_status='confirmed',
            new_status=booking.booking_status,
            notes=f"Cancelled: {cancellation_data.reason}"
        )

        return booking

    def _is_valid_status_transition(
        self,
        old_status: str,
        new_status: str
    ) -> bool:
        """Validate status transition"""
        valid_transitions = {
            'confirmed': ['completed', 'cancelled_by_customer', 'cancelled_by_business', 'no_show'],
            'completed': [],  # Terminal state
            'cancelled_by_customer': [],  # Terminal state
            'cancelled_by_business': [],  # Terminal state
            'no_show': []  # Terminal state
        }

        allowed = valid_transitions.get(old_status, [])
        return new_status in allowed

    async def get_booking_history(
        self,
        booking_id: UUID
    ) -> List[BookingHistory]:
        """Get booking history"""
        result = await self.db.execute(
            select(BookingHistory)
            .where(BookingHistory.booking_id == booking_id)
            .order_by(BookingHistory.created_at)
        )
        return list(result.scalars().all())

    async def _create_history(
        self,
        booking_id: UUID,
        old_status: Optional[str],
        new_status: str,
        notes: Optional[str] = None,
        changed_by: Optional[UUID] = None
    ):
        """Create history entry"""
        history = BookingHistory(
            booking_id=booking_id,
            old_status=old_status,
            new_status=new_status,
            notes=notes,
            changed_by_user_id=changed_by
        )

        self.db.add(history)
        await self.db.flush()

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
