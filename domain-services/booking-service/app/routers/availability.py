"""
Availability Router - API endpoints for checking availability

Endpoints for:
- Checking available time slots for services
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.database import get_db
from app.schemas import AvailabilityQuery, AvailabilityResponse, TimeSlot
from app.services.availability_service import AvailabilityService
from app.services.service_service import ServiceManagementService

router = APIRouter()


@router.post("/{site_id}/availability", response_model=AvailabilityResponse)
async def check_availability(
    site_id: UUID,
    query: AvailabilityQuery,
    db: AsyncSession = Depends(get_db)
):
    """
    Check available time slots for a service

    Returns all available slots for the specified service on the given date.
    If provider_id is specified, only shows slots for that provider.
    Otherwise, shows slots for all providers who can provide the service.

    The availability calculation considers:
    - Provider working hours (recurring schedules + specific date overrides)
    - Existing bookings
    - Blocked time slots
    - Service duration + buffer time
    """
    # Get service first to include in response
    service_mgmt = ServiceManagementService(db)
    service = await service_mgmt.get_service(query.service_id, site_id)

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service not found"
        )

    # Get available slots
    availability_service = AvailabilityService(db)
    slots = await availability_service.get_available_slots(site_id, query)

    return AvailabilityResponse(
        date=query.date,
        service_id=service.service_id,
        service_name=service.name,
        duration_minutes=service.duration_minutes,
        slots=slots
    )
