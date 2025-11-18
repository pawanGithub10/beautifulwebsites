"""
Database models for Booking Service

Tables:
- service_categories: Categories for services
- services: Services offered (haircut, massage, consultation, etc.)
- providers: Staff/professionals who provide services
- provider_schedules: Working hours for providers
- recurring_schedules: Weekly recurring availability patterns
- blocked_slots: Blocked time slots (holidays, breaks, etc.)
- bookings: Actual bookings/appointments
- booking_history: Audit trail for booking status changes
"""

from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime, Text,
    ForeignKey, Numeric, Date, Time, Index, UniqueConstraint,
    ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class ServiceCategory(Base):
    """Service categories (e.g., Haircuts, Facials, Massages)"""
    __tablename__ = "service_categories"

    category_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("service_categories.category_id"), nullable=True)

    name = Column(String(200), nullable=False)
    slug = Column(String(200), nullable=False)
    description = Column(Text)
    icon = Column(String(200))  # Icon/image for category
    display_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True, index=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = relationship("ServiceCategory", remote_side=[category_id], back_populates="children")
    children = relationship("ServiceCategory", back_populates="parent")
    services = relationship("Service", back_populates="category")

    __table_args__ = (
        Index('ix_service_categories_site_slug', 'site_id', 'slug'),
        Index('ix_service_categories_parent', 'parent_id'),
    )


class Service(Base):
    """Services offered (e.g., Men's Haircut, Swedish Massage)"""
    __tablename__ = "services"

    service_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("service_categories.category_id"), nullable=True)

    name = Column(String(300), nullable=False)
    slug = Column(String(300), nullable=False)
    sku = Column(String(100), unique=True)
    short_description = Column(String(500))
    description = Column(Text)

    # Pricing
    price = Column(Numeric(10, 2), nullable=False)
    compare_at_price = Column(Numeric(10, 2))  # Original price (for discounts)

    # Duration
    duration_minutes = Column(Integer, nullable=False)  # Service duration
    buffer_minutes = Column(Integer, default=0)  # Buffer after service (cleanup time)

    # Media
    images = Column(JSONB, default=list)  # Array of image URLs

    # Metadata
    tags = Column(JSONB, default=list)  # Array of tags for search
    attributes = Column(JSONB, default=dict)  # Flexible attributes (e.g., {"skill_level": "advanced"})

    # Settings
    is_featured = Column(Boolean, default=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    requires_provider = Column(Boolean, default=True)  # Some services might not need specific provider
    max_bookings_per_slot = Column(Integer, default=1)  # For group services

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = relationship("ServiceCategory", back_populates="services")
    bookings = relationship("Booking", back_populates="service")

    __table_args__ = (
        Index('ix_services_site_category', 'site_id', 'category_id'),
        Index('ix_services_slug', 'slug'),
        Index('ix_services_sku', 'sku'),
        Index('ix_services_featured', 'is_featured'),
    )


class Provider(Base):
    """Service providers (staff, professionals)"""
    __tablename__ = "providers"

    provider_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Link to User Service

    name = Column(String(200), nullable=False)
    email = Column(String(200))
    phone = Column(String(20))
    bio = Column(Text)
    profile_image = Column(String(500))

    # Settings
    is_active = Column(Boolean, default=True, index=True)
    accepts_bookings = Column(Boolean, default=True)

    # Services this provider can perform (JSONB array of service_ids)
    service_ids = Column(JSONB, default=list)

    # Metadata
    attributes = Column(JSONB, default=dict)  # {"specialization": "Hair Coloring", "experience_years": 5}

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    schedules = relationship("ProviderSchedule", back_populates="provider", cascade="all, delete-orphan")
    recurring_schedules = relationship("RecurringSchedule", back_populates="provider", cascade="all, delete-orphan")
    blocked_slots = relationship("BlockedSlot", back_populates="provider", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="provider")

    __table_args__ = (
        Index('ix_providers_site_active', 'site_id', 'is_active'),
    )


class RecurringSchedule(Base):
    """Recurring weekly availability for providers"""
    __tablename__ = "recurring_schedules"

    schedule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.provider_id"), nullable=False)

    day_of_week = Column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    provider = relationship("Provider", back_populates="recurring_schedules")

    __table_args__ = (
        Index('ix_recurring_schedules_provider_day', 'provider_id', 'day_of_week'),
    )


class ProviderSchedule(Base):
    """Specific date overrides for provider availability"""
    __tablename__ = "provider_schedules"

    schedule_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.provider_id"), nullable=False)

    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    is_available = Column(Boolean, default=True)  # Can be used to mark as unavailable
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    provider = relationship("Provider", back_populates="schedules")

    __table_args__ = (
        Index('ix_provider_schedules_provider_date', 'provider_id', 'date'),
        UniqueConstraint('provider_id', 'date', name='uq_provider_date'),
    )


class BlockedSlot(Base):
    """Blocked time slots (breaks, holidays, etc.)"""
    __tablename__ = "blocked_slots"

    blocked_slot_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.provider_id"), nullable=True)  # Null = site-wide

    start_datetime = Column(DateTime, nullable=False)
    end_datetime = Column(DateTime, nullable=False)
    reason = Column(String(200))
    notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    created_by_user_id = Column(UUID(as_uuid=True))

    # Relationships
    provider = relationship("Provider", back_populates="blocked_slots")

    __table_args__ = (
        Index('ix_blocked_slots_site_datetime', 'site_id', 'start_datetime'),
        Index('ix_blocked_slots_provider_datetime', 'provider_id', 'start_datetime'),
    )


class Booking(Base):
    """Customer bookings/appointments"""
    __tablename__ = "bookings"

    booking_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)  # Null for guest bookings

    booking_number = Column(String(50), unique=True, nullable=False, index=True)

    # Service details
    service_id = Column(UUID(as_uuid=True), ForeignKey("services.service_id"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("providers.provider_id"), nullable=True)

    # Timing
    booking_date = Column(Date, nullable=False, index=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)

    # Customer details (stored for guest bookings)
    customer_name = Column(String(200), nullable=False)
    customer_email = Column(String(200))
    customer_phone = Column(String(20), nullable=False, index=True)
    customer_notes = Column(Text)  # Special requests

    # Pricing (snapshot at booking time)
    service_price = Column(Numeric(10, 2), nullable=False)
    service_name = Column(String(300), nullable=False)  # Snapshot
    provider_name = Column(String(200))  # Snapshot

    # Payment
    payment_method = Column(String(50))  # cash, card, online, wallet
    payment_status = Column(String(20), default='pending', index=True)  # pending, paid, failed, refunded

    # Status
    booking_status = Column(String(20), default='confirmed', index=True)
    # confirmed, cancelled_by_customer, cancelled_by_business, completed, no_show

    # Cancellation
    cancelled_at = Column(DateTime)
    cancellation_reason = Column(Text)
    cancellation_fee = Column(Numeric(10, 2), default=0)

    # Timestamps
    confirmed_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # Admin notes
    internal_notes = Column(Text)

    # Reminders sent
    reminder_sent = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    service = relationship("Service", back_populates="bookings")
    provider = relationship("Provider", back_populates="bookings")
    history = relationship("BookingHistory", back_populates="booking", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_bookings_site_date', 'site_id', 'booking_date'),
        Index('ix_bookings_provider_date', 'provider_id', 'booking_date'),
        Index('ix_bookings_service', 'service_id'),
        Index('ix_bookings_status', 'booking_status'),
        Index('ix_bookings_customer_phone', 'customer_phone'),
    )


class BookingHistory(Base):
    """Audit trail for booking status changes"""
    __tablename__ = "booking_history"

    history_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.booking_id"), nullable=False)

    old_status = Column(String(20))
    new_status = Column(String(20), nullable=False)
    notes = Column(Text)

    changed_by_user_id = Column(UUID(as_uuid=True))  # Who made the change

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    booking = relationship("Booking", back_populates="history")

    __table_args__ = (
        Index('ix_booking_history_booking', 'booking_id'),
    )
