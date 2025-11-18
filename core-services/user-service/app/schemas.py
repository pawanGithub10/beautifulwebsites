"""
User Service Pydantic Schemas
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

from app.models import DeviceType, ActivityType, VerificationType, VerificationStatus


# ============================================================================
# User Profile Schemas
# ============================================================================

class UserProfileBase(BaseModel):
    """Base user profile schema"""
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = "en"
    country_code: Optional[str] = Field(None, max_length=2)
    website: Optional[str] = None
    twitter_handle: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = None


class UserProfileCreate(UserProfileBase):
    """Create user profile"""
    user_id: UUID


class UserProfileUpdate(BaseModel):
    """Update user profile"""
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    country_code: Optional[str] = Field(None, max_length=2)
    website: Optional[str] = None
    twitter_handle: Optional[str] = Field(None, max_length=50)
    linkedin_url: Optional[str] = None


class UserProfileResponse(UserProfileBase):
    """User profile response"""
    user_id: UUID
    avatar_url: Optional[str] = None
    cover_image_url: Optional[str] = None
    phone_verified: bool
    phone_verified_at: Optional[datetime] = None
    is_verified: bool
    verified_at: Optional[datetime] = None
    verification_badge: Optional[str] = None
    total_orders: int
    total_bookings: int
    total_spent: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# User Address Schemas
# ============================================================================

class UserAddressBase(BaseModel):
    """Base address schema"""
    address_type: str = Field(..., pattern="^(shipping|billing|both)$")
    label: Optional[str] = Field(None, max_length=50)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: Optional[str] = None
    address_line1: str = Field(..., min_length=1, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    country_code: str = Field(..., min_length=2, max_length=2)
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    is_default: bool = False


class UserAddressCreate(UserAddressBase):
    """Create address"""
    pass


class UserAddressUpdate(BaseModel):
    """Update address"""
    address_type: Optional[str] = Field(None, pattern="^(shipping|billing|both)$")
    label: Optional[str] = Field(None, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = None
    address_line1: Optional[str] = Field(None, max_length=255)
    address_line2: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    country_code: Optional[str] = Field(None, max_length=2)
    is_default: Optional[bool] = None


class UserAddressResponse(UserAddressBase):
    """Address response"""
    address_id: UUID
    user_id: UUID
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# User Preference Schemas
# ============================================================================

class UserPreferenceBase(BaseModel):
    """Base preference schema"""
    profile_visibility: Optional[str] = Field("public", pattern="^(public|private|friends)$")
    show_email: Optional[bool] = False
    show_phone: Optional[bool] = False
    email_notifications: Optional[bool] = True
    sms_notifications: Optional[bool] = False
    push_notifications: Optional[bool] = True
    marketing_emails: Optional[bool] = True
    newsletter: Optional[bool] = False
    theme: Optional[str] = Field("light", pattern="^(light|dark|auto)$")
    currency: Optional[str] = Field("USD", min_length=3, max_length=3)
    date_format: Optional[str] = "MM/DD/YYYY"
    time_format: Optional[str] = Field("12h", pattern="^(12h|24h)$")
    save_payment_methods: Optional[bool] = True


class UserPreferenceCreate(UserPreferenceBase):
    """Create preferences"""
    pass


class UserPreferenceUpdate(UserPreferenceBase):
    """Update preferences"""
    default_shipping_address_id: Optional[UUID] = None
    default_billing_address_id: Optional[UUID] = None
    custom_preferences: Optional[Dict[str, Any]] = None


class UserPreferenceResponse(UserPreferenceBase):
    """Preference response"""
    user_id: UUID
    default_shipping_address_id: Optional[UUID] = None
    default_billing_address_id: Optional[UUID] = None
    custom_preferences: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# User Device Schemas
# ============================================================================

class UserDeviceBase(BaseModel):
    """Base device schema"""
    device_type: DeviceType
    device_name: Optional[str] = None
    device_token: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    app_version: Optional[str] = None
    browser_name: Optional[str] = None
    browser_version: Optional[str] = None


class UserDeviceCreate(UserDeviceBase):
    """Create device"""
    pass


class UserDeviceUpdate(BaseModel):
    """Update device"""
    device_token: Optional[str] = None
    app_version: Optional[str] = None
    is_active: Optional[bool] = None


class UserDeviceResponse(UserDeviceBase):
    """Device response"""
    device_id: UUID
    user_id: UUID
    last_ip_address: Optional[str] = None
    last_location: Optional[str] = None
    is_active: bool
    last_active_at: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# User Activity Schemas
# ============================================================================

class UserActivityCreate(BaseModel):
    """Create activity log"""
    activity_type: ActivityType
    description: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = None


class UserActivityResponse(BaseModel):
    """Activity response"""
    activity_id: UUID
    user_id: UUID
    activity_type: ActivityType
    description: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    device_id: Optional[UUID] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# User Verification Schemas
# ============================================================================

class UserVerificationCreate(BaseModel):
    """Create verification"""
    verification_type: VerificationType
    document_number: Optional[str] = None
    issuing_country: Optional[str] = None
    expiry_date: Optional[datetime] = None


class UserVerificationUpdate(BaseModel):
    """Update verification (admin only)"""
    status: VerificationStatus
    rejection_reason: Optional[str] = None


class UserVerificationResponse(BaseModel):
    """Verification response"""
    verification_id: UUID
    user_id: UUID
    verification_type: VerificationType
    status: VerificationStatus
    document_number: Optional[str] = None
    issuing_country: Optional[str] = None
    expiry_date: Optional[datetime] = None
    front_image_url: Optional[str] = None
    back_image_url: Optional[str] = None
    selfie_image_url: Optional[str] = None
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Complete User Profile Schemas (with nested data)
# ============================================================================

class CompleteUserProfile(BaseModel):
    """Complete user profile with all related data"""
    profile: UserProfileResponse
    addresses: List[UserAddressResponse] = []
    preferences: Optional[UserPreferenceResponse] = None
    devices: List[UserDeviceResponse] = []

    class Config:
        from_attributes = True


# ============================================================================
# Avatar Upload Schema
# ============================================================================

class AvatarUploadResponse(BaseModel):
    """Avatar upload response"""
    avatar_url: str
    user_id: UUID
    uploaded_at: datetime
