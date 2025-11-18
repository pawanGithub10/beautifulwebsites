"""
Bookings Router - API endpoints for booking management

Endpoints for:
- Booking creation
- Booking queries and listing
- Booking updates (reschedule)
- Status management
- Cancellation
- Booking history
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.database import get_db
from app.schemas import (
    BookingResponse, BookingCreate, BookingUpdate,
    BookingStatusUpdate, BookingCancellation,
    BookingHistoryResponse, BookingFilters
)
from app.services.booking_service import BookingManagementService

router = APIRouter()


# ======================
# BOOKING ENDPOINTS
# ======================

@router.post("/{site_id}/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    site_id: UUID,
    booking_data: BookingCreate,
    user_id: Optional[UUID] = None,  # TODO: Extract from auth token
    db: AsyncSession = Depends(get_db)
):
    """
    Create new booking

    Steps:
    1. Validates service exists and is active
    2. Validates provider (if specified)
    3. Checks slot availability (no double-booking)
    4. Generates unique booking number
    5. Creates booking with service/provider snapshots
    6. Creates initial history entry

    Returns created booking with all details.
    """
    service = BookingManagementService(db)

    try:
        booking = await service.create_booking(site_id, booking_data, user_id)
        await db.commit()
        return booking
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create booking: {str(e)}"
        )


@router.get("/{site_id}/bookings", response_model=List[BookingResponse])
async def list_bookings(
    site_id: UUID,
    booking_status: Optional[str] = Query(None),
    payment_status: Optional[str] = Query(None),
    provider_id: Optional[UUID] = Query(None),
    service_id: Optional[UUID] = Query(None),
    customer_phone: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    List bookings with filters and pagination

    Filters:
    - booking_status: confirmed, cancelled_by_customer, cancelled_by_business, completed, no_show
    - payment_status: pending, paid, failed, refunded
    - provider_id: Filter by provider
    - service_id: Filter by service
    - customer_phone: Find bookings by phone number
    - date_from, date_to: Date range filter
    """
    filters = BookingFilters(
        booking_status=booking_status,
        payment_status=payment_status,
        provider_id=provider_id,
        service_id=service_id,
        customer_phone=customer_phone,
        date_from=date_from,
        date_to=date_to,
        page=page,
        page_size=page_size
    )

    service = BookingManagementService(db)
    bookings, total = await service.list_bookings(site_id, filters)

    return bookings


@router.get("/{site_id}/bookings/{booking_id}", response_model=BookingResponse)
async def get_booking(
    site_id: UUID,
    booking_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get booking by ID"""
    service = BookingManagementService(db)
    booking = await service.get_booking(booking_id, site_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    return booking


@router.get("/{site_id}/bookings/by-number/{booking_number}", response_model=BookingResponse)
async def get_booking_by_number(
    site_id: UUID,
    booking_number: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get booking by booking number

    Useful for customer lookup (e.g., "What's your booking number?")
    """
    service = BookingManagementService(db)
    booking = await service.get_booking_by_number(booking_number, site_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking {booking_number} not found"
        )

    return booking


@router.put("/{site_id}/bookings/{booking_id}", response_model=BookingResponse)
async def update_booking(
    site_id: UUID,
    booking_id: UUID,
    booking_data: BookingUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update booking (reschedule)

    Can update:
    - Date and time (with availability check)
    - Customer details
    - Notes
    - Payment method

    Cannot update if booking is not in 'confirmed' status.
    """
    service = BookingManagementService(db)

    try:
        booking = await service.update_booking(booking_id, site_id, booking_data)

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        await db.commit()
        return booking
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update booking: {str(e)}"
        )


# ======================
# STATUS MANAGEMENT ENDPOINTS
# ======================

@router.put("/{site_id}/bookings/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    site_id: UUID,
    booking_id: UUID,
    status_data: BookingStatusUpdate,
    user_id: Optional[UUID] = None,  # TODO: Extract from auth token
    db: AsyncSession = Depends(get_db)
):
    """
    Update booking status

    Valid transitions:
    - confirmed → completed, cancelled_by_customer, cancelled_by_business, no_show

    Creates history entry for audit trail.
    """
    service = BookingManagementService(db)

    try:
        booking = await service.update_booking_status(
            booking_id, site_id, status_data, user_id
        )

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        await db.commit()
        return booking
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update booking status: {str(e)}"
        )


@router.post("/{site_id}/bookings/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    site_id: UUID,
    booking_id: UUID,
    cancellation_data: BookingCancellation,
    cancelled_by_customer: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel booking

    Enforces cancellation policy:
    - If cancelled within minimum hours before appointment, may apply cancellation fee
    - If cancelled outside the window, free cancellation

    Default minimum hours configured in settings (24 hours).

    Parameters:
    - cancelled_by_customer: True if customer cancelled, False if business cancelled
    """
    service = BookingManagementService(db)

    try:
        booking = await service.cancel_booking(
            booking_id, site_id, cancellation_data, cancelled_by_customer
        )

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        await db.commit()
        return booking
    except ValueError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel booking: {str(e)}"
        )


# ======================
# HISTORY ENDPOINTS
# ======================

@router.get("/{site_id}/bookings/{booking_id}/history", response_model=List[BookingHistoryResponse])
async def get_booking_history(
    site_id: UUID,
    booking_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete booking history

    Returns all status changes and modifications with timestamps and notes.
    """
    # Verify booking exists
    booking_service = BookingManagementService(db)
    booking = await booking_service.get_booking(booking_id, site_id)

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    history = await booking_service.get_booking_history(booking_id)
    return history
