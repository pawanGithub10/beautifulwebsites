"""
Providers Router - API endpoints for provider management

Endpoints for:
- Provider CRUD
- Recurring schedules
- Specific date schedules
- Blocked slots
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import date

from app.database import get_db
from app.schemas import (
    ProviderResponse, ProviderCreate, ProviderUpdate,
    RecurringScheduleResponse, RecurringScheduleCreate, RecurringScheduleUpdate,
    ProviderScheduleResponse, ProviderScheduleCreate, ProviderScheduleUpdate,
    BlockedSlotResponse, BlockedSlotCreate
)
from app.services.provider_service import ProviderManagementService

router = APIRouter()


# ======================
# PROVIDER ENDPOINTS
# ======================

@router.post("/{site_id}/providers", response_model=ProviderResponse, status_code=status.HTTP_201_CREATED)
async def create_provider(
    site_id: UUID,
    provider_data: ProviderCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new provider"""
    service = ProviderManagementService(db)
    provider = await service.create_provider(site_id, provider_data)
    return provider


@router.get("/{site_id}/providers", response_model=List[ProviderResponse])
async def list_providers(
    site_id: UUID,
    service_id: Optional[UUID] = Query(None),
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """List providers for site"""
    service = ProviderManagementService(db)
    providers = await service.list_providers(
        site_id,
        service_id=service_id,
        active_only=active_only
    )
    return providers


@router.get("/{site_id}/providers/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    site_id: UUID,
    provider_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get provider by ID"""
    service = ProviderManagementService(db)
    provider = await service.get_provider(provider_id, site_id)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )

    return provider


@router.put("/{site_id}/providers/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    site_id: UUID,
    provider_id: UUID,
    provider_data: ProviderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update provider"""
    service = ProviderManagementService(db)
    provider = await service.update_provider(provider_id, site_id, provider_data)

    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )

    return provider


@router.delete("/{site_id}/providers/{provider_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_provider(
    site_id: UUID,
    provider_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete provider (soft delete)"""
    service = ProviderManagementService(db)
    success = await service.delete_provider(provider_id, site_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )

    return None


# ======================
# RECURRING SCHEDULE ENDPOINTS
# ======================

@router.post(
    "/{site_id}/providers/{provider_id}/recurring-schedules",
    response_model=RecurringScheduleResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_recurring_schedule(
    site_id: UUID,
    provider_id: UUID,
    schedule_data: RecurringScheduleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create recurring weekly schedule for provider"""
    service = ProviderManagementService(db)
    try:
        schedule = await service.create_recurring_schedule(
            provider_id, site_id, schedule_data
        )
        return schedule
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{site_id}/providers/{provider_id}/recurring-schedules",
    response_model=List[RecurringScheduleResponse]
)
async def list_recurring_schedules(
    site_id: UUID,
    provider_id: UUID,
    day_of_week: Optional[int] = Query(None, ge=0, le=6),
    db: AsyncSession = Depends(get_db)
):
    """List recurring schedules for provider"""
    service = ProviderManagementService(db)

    # Verify provider exists
    provider = await service.get_provider(provider_id, site_id)
    if not provider:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Provider not found"
        )

    schedules = await service.get_recurring_schedules(provider_id, day_of_week)
    return schedules


@router.put(
    "/{site_id}/providers/{provider_id}/recurring-schedules/{schedule_id}",
    response_model=RecurringScheduleResponse
)
async def update_recurring_schedule(
    site_id: UUID,
    provider_id: UUID,
    schedule_id: UUID,
    schedule_data: RecurringScheduleUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update recurring schedule"""
    service = ProviderManagementService(db)
    schedule = await service.update_recurring_schedule(schedule_id, schedule_data)

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    return schedule


@router.delete(
    "/{site_id}/providers/{provider_id}/recurring-schedules/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_recurring_schedule(
    site_id: UUID,
    provider_id: UUID,
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete recurring schedule"""
    service = ProviderManagementService(db)
    success = await service.delete_recurring_schedule(schedule_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    return None


# ======================
# SPECIFIC DATE SCHEDULE ENDPOINTS
# ======================

@router.post(
    "/{site_id}/providers/{provider_id}/schedules",
    response_model=ProviderScheduleResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_provider_schedule(
    site_id: UUID,
    provider_id: UUID,
    schedule_data: ProviderScheduleCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create specific date schedule override"""
    service = ProviderManagementService(db)
    try:
        schedule = await service.create_provider_schedule(
            provider_id, site_id, schedule_data
        )
        return schedule
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{site_id}/providers/{provider_id}/schedules/{schedule_date}",
    response_model=ProviderScheduleResponse
)
async def get_provider_schedule(
    site_id: UUID,
    provider_id: UUID,
    schedule_date: date,
    db: AsyncSession = Depends(get_db)
):
    """Get provider schedule for specific date"""
    service = ProviderManagementService(db)
    schedule = await service.get_provider_schedule(provider_id, schedule_date)

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found for this date"
        )

    return schedule


@router.delete(
    "/{site_id}/providers/{provider_id}/schedules/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_provider_schedule(
    site_id: UUID,
    provider_id: UUID,
    schedule_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete specific date schedule"""
    service = ProviderManagementService(db)
    success = await service.delete_provider_schedule(schedule_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )

    return None


# ======================
# BLOCKED SLOT ENDPOINTS
# ======================

@router.post("/{site_id}/blocked-slots", response_model=BlockedSlotResponse, status_code=status.HTTP_201_CREATED)
async def create_blocked_slot(
    site_id: UUID,
    blocked_data: BlockedSlotCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create blocked time slot"""
    service = ProviderManagementService(db)
    try:
        blocked_slot = await service.create_blocked_slot(site_id, blocked_data)
        return blocked_slot
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{site_id}/blocked-slots", response_model=List[BlockedSlotResponse])
async def list_blocked_slots(
    site_id: UUID,
    provider_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List blocked slots"""
    service = ProviderManagementService(db)
    blocked_slots = await service.get_blocked_slots(site_id, provider_id)
    return blocked_slots


@router.delete("/{site_id}/blocked-slots/{blocked_slot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blocked_slot(
    site_id: UUID,
    blocked_slot_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete blocked slot"""
    service = ProviderManagementService(db)
    success = await service.delete_blocked_slot(blocked_slot_id, site_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blocked slot not found"
        )

    return None
