"""
User Service Database Models
"""

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.database import Base


class UserProfile(Base):
    """
    Extended user profile information
    Complements the User table in Auth Service
    """
    __tablename__ = "user_profiles"

    user_id = Column(UUID(as_uuid=True), primary_key=True)  # Same as auth-service user_id
    display_name = Column(String(100), nullable=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    cover_image_url = Column(String(500), nullable=True)

    # Contact
    phone_verified = Column(Boolean, default=False)
    phone_verified_at = Column(DateTime, nullable=True)

    # Location
    timezone = Column(String(50), nullable=True)
    language = Column(String(10), default="en")
    country_code = Column(String(2), nullable=True)

    # Social Links
    website = Column(String(255), nullable=True)
    twitter_handle = Column(String(50), nullable=True)
    linkedin_url = Column(String(255), nullable=True)

    # Stats
    total_orders = Column(Integer, default=0)
    total_bookings = Column(Integer, default=0)
    total_spent = Column(Integer, default=0)  # In cents

    # Verification
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime, nullable=True)
    verification_badge = Column(String(20), nullable=True)  # 'email', 'phone', 'id', 'business'

    # Metadata
    metadata = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    addresses = relationship("UserAddress", back_populates="user", cascade="all, delete-orphan")
    devices = relationship("UserDevice", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserAddress(Base):
    """
    User addresses for shipping, billing, etc.
    """
    __tablename__ = "user_addresses"

    address_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.user_id"), nullable=False, index=True)

    # Address Type
    address_type = Column(String(20), nullable=False)  # 'shipping', 'billing', 'both'
    label = Column(String(50), nullable=True)  # 'Home', 'Work', 'Office', etc.

    # Address Details
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=False)
    country_code = Column(String(2), nullable=False)  # ISO 3166-1 alpha-2

    # Location
    latitude = Column(String(20), nullable=True)
    longitude = Column(String(20), nullable=True)

    # Flags
    is_default = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("UserProfile", back_populates="addresses")


class UserPreference(Base):
    """
    User preferences and settings
    """
    __tablename__ = "user_preferences"

    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.user_id"), primary_key=True)

    # Privacy Settings
    profile_visibility = Column(String(20), default="public")  # 'public', 'private', 'friends'
    show_email = Column(Boolean, default=False)
    show_phone = Column(Boolean, default=False)

    # Communication Preferences
    email_notifications = Column(Boolean, default=True)
    sms_notifications = Column(Boolean, default=False)
    push_notifications = Column(Boolean, default=True)
    marketing_emails = Column(Boolean, default=True)
    newsletter = Column(Boolean, default=False)

    # Display Preferences
    theme = Column(String(20), default="light")  # 'light', 'dark', 'auto'
    currency = Column(String(3), default="USD")  # ISO 4217
    date_format = Column(String(20), default="MM/DD/YYYY")
    time_format = Column(String(10), default="12h")  # '12h', '24h'

    # Order & Booking Preferences
    default_shipping_address_id = Column(UUID(as_uuid=True), nullable=True)
    default_billing_address_id = Column(UUID(as_uuid=True), nullable=True)
    save_payment_methods = Column(Boolean, default=True)

    # Custom Preferences
    custom_preferences = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("UserProfile", back_populates="preferences")


class DeviceType(str, enum.Enum):
    """Device types"""
    WEB = "web"
    IOS = "ios"
    ANDROID = "android"
    TABLET = "tablet"
    DESKTOP = "desktop"
    OTHER = "other"


class UserDevice(Base):
    """
    User devices for push notifications and security
    """
    __tablename__ = "user_devices"

    device_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.user_id"), nullable=False, index=True)

    # Device Info
    device_type = Column(SQLEnum(DeviceType), nullable=False)
    device_name = Column(String(100), nullable=True)  # 'iPhone 13', 'Chrome on MacOS', etc.
    device_token = Column(String(500), nullable=True)  # FCM/APNS token

    # Device Details
    os_name = Column(String(50), nullable=True)
    os_version = Column(String(50), nullable=True)
    app_version = Column(String(50), nullable=True)

    # Browser Info (for web)
    browser_name = Column(String(50), nullable=True)
    browser_version = Column(String(50), nullable=True)

    # Location
    last_ip_address = Column(String(45), nullable=True)
    last_location = Column(String(100), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    last_active_at = Column(DateTime, default=datetime.utcnow)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("UserProfile", back_populates="devices")


class ActivityType(str, enum.Enum):
    """Activity types"""
    LOGIN = "login"
    LOGOUT = "logout"
    PROFILE_UPDATE = "profile_update"
    PASSWORD_CHANGE = "password_change"
    EMAIL_CHANGE = "email_change"
    PHONE_CHANGE = "phone_change"
    ADDRESS_ADD = "address_add"
    ADDRESS_UPDATE = "address_update"
    ADDRESS_DELETE = "address_delete"
    PREFERENCE_UPDATE = "preference_update"
    AVATAR_UPLOAD = "avatar_upload"
    ORDER_PLACED = "order_placed"
    BOOKING_MADE = "booking_made"
    REVIEW_POSTED = "review_posted"
    OTHER = "other"


class UserActivity(Base):
    """
    User activity log for analytics and security
    """
    __tablename__ = "user_activities"

    activity_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Activity Details
    activity_type = Column(SQLEnum(ActivityType), nullable=False, index=True)
    description = Column(String(500), nullable=True)

    # Context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    device_id = Column(UUID(as_uuid=True), nullable=True)

    # Metadata
    metadata = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class VerificationType(str, enum.Enum):
    """Verification document types"""
    GOVERNMENT_ID = "government_id"
    PASSPORT = "passport"
    DRIVERS_LICENSE = "drivers_license"
    BUSINESS_LICENSE = "business_license"
    TAX_ID = "tax_id"
    OTHER = "other"


class VerificationStatus(str, enum.Enum):
    """Verification status"""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class UserVerification(Base):
    """
    User identity verification documents
    """
    __tablename__ = "user_verifications"

    verification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)

    # Verification Type
    verification_type = Column(SQLEnum(VerificationType), nullable=False)
    status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING, index=True)

    # Document Details
    document_number = Column(String(100), nullable=True)
    issuing_country = Column(String(2), nullable=True)
    expiry_date = Column(DateTime, nullable=True)

    # Files
    front_image_url = Column(String(500), nullable=True)
    back_image_url = Column(String(500), nullable=True)
    selfie_image_url = Column(String(500), nullable=True)

    # Review
    reviewed_by = Column(UUID(as_uuid=True), nullable=True)  # Admin user ID
    reviewed_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)

    # Metadata
    metadata = Column(JSONB, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
