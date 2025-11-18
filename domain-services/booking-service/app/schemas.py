"""
Pydantic schemas for request/response validation

Schemas for:
- Service categories
- Services
- Providers
- Provider schedules
- Bookings
- Availability queries
"""

from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date, time
from decimal import Decimal
import re


# ======================
# SERVICE CATEGORY SCHEMAS
# ======================

class ServiceCategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    icon: Optional[str] = None
    display_order: int = 0
    parent_id: Optional[UUID] = None

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v


class ServiceCategoryCreate(ServiceCategoryBase):
    pass


class ServiceCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    icon: Optional[str] = None
    display_order: Optional[int] = None
    parent_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class ServiceCategoryResponse(ServiceCategoryBase):
    category_id: UUID
    site_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ======================
# SERVICE SCHEMAS
# ======================

class ServiceBase(BaseModel):
    category_id: Optional[UUID] = None
    name: str = Field(..., min_length=1, max_length=300)
    slug: str = Field(..., min_length=1, max_length=300)
    sku: Optional[str] = Field(None, max_length=100)
    short_description: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    compare_at_price: Optional[Decimal] = Field(None, decimal_places=2)
    duration_minutes: int = Field(..., gt=0, le=1440)  # Max 24 hours
    buffer_minutes: int = Field(default=0, ge=0, le=120)
    images: List[str] = []
    tags: List[str] = []
    attributes: Dict[str, Any] = {}
    is_featured: bool = False
    requires_provider: bool = True
    max_bookings_per_slot: int = Field(default=1, ge=1, le=100)

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v):
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug must contain only lowercase letters, numbers, and hyphens')
        return v


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    category_id: Optional[UUID] = None
    name: Optional[str] = Field(None, min_length=1, max_length=300)
    slug: Optional[str] = Field(None, min_length=1, max_length=300)
    sku: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    compare_at_price: Optional[Decimal] = None
    duration_minutes: Optional[int] = None
    buffer_minutes: Optional[int] = None
    images: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    attributes: Optional[Dict[str, Any]] = None
    is_featured: Optional[bool] = None
    is_active: Optional[bool] = None
    requires_provider: Optional[bool] = None
    max_bookings_per_slot: Optional[int] = None


class ServiceResponse(ServiceBase):
    service_id: UUID
    site_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ======================
# PROVIDER SCHEMAS
# ======================

class ProviderBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    service_ids: List[UUID] = []
    attributes: Dict[str, Any] = {}
    accepts_bookings: bool = True


class ProviderCreate(ProviderBase):
    user_id: Optional[UUID] = None


class ProviderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    service_ids: Optional[List[UUID]] = None
    attributes: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    accepts_bookings: Optional[bool] = None


class ProviderResponse(ProviderBase):
    provider_id: UUID
    site_id: UUID
    user_id: Optional[UUID]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ======================
# SCHEDULE SCHEMAS
# ======================

class RecurringScheduleBase(BaseModel):
    day_of_week: int = Field(..., ge=0, le=6)  # 0=Monday, 6=Sunday
    start_time: time
    end_time: time

    @field_validator('end_time')
    @classmethod
    def validate_times(cls, v, info):
        if 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError('end_time must be after start_time')
        return v


class RecurringScheduleCreate(RecurringScheduleBase):
    pass


class RecurringScheduleUpdate(BaseModel):
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_active: Optional[bool] = None


class RecurringScheduleResponse(RecurringScheduleBase):
    schedule_id: UUID
    provider_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProviderScheduleBase(BaseModel):
    date: date
    start_time: time
    end_time: time
    is_available: bool = True
    notes: Optional[str] = None


class ProviderScheduleCreate(ProviderScheduleBase):
    pass


class ProviderScheduleUpdate(BaseModel):
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_available: Optional[bool] = None
    notes: Optional[str] = None


class ProviderScheduleResponse(ProviderScheduleBase):
    schedule_id: UUID
    provider_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlockedSlotBase(BaseModel):
    start_datetime: datetime
    end_datetime: datetime
    reason: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = None

    @field_validator('end_datetime')
    @classmethod
    def validate_datetimes(cls, v, info):
        if 'start_datetime' in info.data and v <= info.data['start_datetime']:
            raise ValueError('end_datetime must be after start_datetime')
        return v


class BlockedSlotCreate(BlockedSlotBase):
    provider_id: Optional[UUID] = None  # Null for site-wide blocks


class BlockedSlotResponse(BlockedSlotBase):
    blocked_slot_id: UUID
    site_id: UUID
    provider_id: Optional[UUID]
    created_at: datetime
    created_by_user_id: Optional[UUID]

    class Config:
        from_attributes = True


# ======================
# BOOKING SCHEMAS
# ======================

class BookingBase(BaseModel):
    service_id: UUID
    provider_id: Optional[UUID] = None
    booking_date: date
    start_time: time
    customer_name: str = Field(..., min_length=1, max_length=200)
    customer_email: Optional[str] = Field(None, max_length=200)
    customer_phone: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    customer_notes: Optional[str] = None
    payment_method: Optional[str] = Field(None, pattern=r'^(cash|card|online|wallet)$')


class BookingCreate(BookingBase):
    pass


class BookingUpdate(BaseModel):
    booking_date: Optional[date] = None
    start_time: Optional[time] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_notes: Optional[str] = None
    payment_method: Optional[str] = None
    internal_notes: Optional[str] = None


class BookingStatusUpdate(BaseModel):
    booking_status: str = Field(
        ...,
        pattern=r'^(confirmed|cancelled_by_customer|cancelled_by_business|completed|no_show)$'
    )
    notes: Optional[str] = None


class BookingCancellation(BaseModel):
    reason: str = Field(..., min_length=1)
    cancellation_fee: Decimal = Field(default=Decimal('0'), ge=0)


class BookingResponse(BaseModel):
    booking_id: UUID
    site_id: UUID
    user_id: Optional[UUID]
    booking_number: str
    service_id: UUID
    provider_id: Optional[UUID]
    booking_date: date
    start_time: time
    end_time: time
    duration_minutes: int
    customer_name: str
    customer_email: Optional[str]
    customer_phone: str
    customer_notes: Optional[str]
    service_price: Decimal
    service_name: str
    provider_name: Optional[str]
    payment_method: Optional[str]
    payment_status: str
    booking_status: str
    cancelled_at: Optional[datetime]
    cancellation_reason: Optional[str]
    cancellation_fee: Decimal
    confirmed_at: datetime
    completed_at: Optional[datetime]
    internal_notes: Optional[str]
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingHistoryResponse(BaseModel):
    history_id: UUID
    booking_id: UUID
    old_status: Optional[str]
    new_status: str
    notes: Optional[str]
    changed_by_user_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True


# ======================
# AVAILABILITY SCHEMAS
# ======================

class TimeSlot(BaseModel):
    """Available time slot"""
    start_time: time
    end_time: time
    provider_id: Optional[UUID] = None
    provider_name: Optional[str] = None
    available: bool = True


class AvailabilityQuery(BaseModel):
    """Query for available slots"""
    service_id: UUID
    date: date
    provider_id: Optional[UUID] = None  # If not specified, check all providers


class AvailabilityResponse(BaseModel):
    """Available slots for a date"""
    date: date
    service_id: UUID
    service_name: str
    duration_minutes: int
    slots: List[TimeSlot]


# ======================
# FILTER & PAGINATION SCHEMAS
# ======================

class ServiceFilters(BaseModel):
    category_id: Optional[UUID] = None
    search: Optional[str] = None
    tags: Optional[List[str]] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    is_featured: Optional[bool] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc", pattern=r'^(asc|desc)$')


class BookingFilters(BaseModel):
    booking_status: Optional[str] = None
    payment_status: Optional[str] = None
    provider_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    customer_phone: Optional[str] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int
