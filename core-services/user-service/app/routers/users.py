"""
User API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app.schemas import (
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    UserAddressCreate, UserAddressUpdate, UserAddressResponse,
    UserPreferenceUpdate, UserPreferenceResponse,
    UserDeviceCreate, UserDeviceResponse,
    UserActivityResponse, UserVerificationCreate, UserVerificationResponse,
    CompleteUserProfile, AvatarUploadResponse, ActivityType
)
from app.services.user_service import UserService
from app.services.upload_service import UploadService

router = APIRouter()


# ============================================================================
# Profile Endpoints
# ============================================================================

@router.post("/profiles", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: UserProfileCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user profile

    This is typically called by the Auth Service after user registration.
    """
    user_service = UserService(db)
    profile = await user_service.create_profile(profile_data)

    return UserProfileResponse.from_orm(profile)


@router.get("/profiles/{user_id}", response_model=UserProfileResponse)
async def get_profile(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user profile by user ID
    """
    user_service = UserService(db)
    profile = await user_service.get_profile(user_id)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return UserProfileResponse.from_orm(profile)


@router.get("/profiles/{user_id}/complete", response_model=CompleteUserProfile)
async def get_complete_profile(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete user profile with addresses, preferences, and devices
    """
    user_service = UserService(db)
    complete_profile = await user_service.get_complete_profile(user_id)

    if not complete_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return complete_profile


@router.put("/profiles/{user_id}", response_model=UserProfileResponse)
async def update_profile(
    user_id: UUID,
    profile_data: UserProfileUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update user profile
    """
    user_service = UserService(db)
    profile = await user_service.update_profile(user_id, profile_data)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return UserProfileResponse.from_orm(profile)


@router.post("/profiles/{user_id}/avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    user_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload user avatar image

    Accepts: JPEG, PNG, GIF, WebP
    Max size: 5MB (configurable)
    Image will be resized and optimized automatically
    """
    # Read file content
    file_content = await file.read()

    # Upload file
    upload_service = UploadService()
    success, avatar_url, error = await upload_service.upload_avatar(
        file_content=file_content,
        filename=file.filename,
        user_id=str(user_id),
        content_type=file.content_type
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error or "Failed to upload avatar"
        )

    # Update profile with new avatar URL
    user_service = UserService(db)
    profile = await user_service.update_avatar(user_id, avatar_url)

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    return AvatarUploadResponse(
        avatar_url=avatar_url,
        user_id=user_id,
        uploaded_at=profile.updated_at
    )


# ============================================================================
# Address Endpoints
# ============================================================================

@router.post("/users/{user_id}/addresses", response_model=UserAddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    user_id: UUID,
    address_data: UserAddressCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new address for user
    """
    user_service = UserService(db)
    address = await user_service.create_address(user_id, address_data)

    return UserAddressResponse.from_orm(address)


@router.get("/users/{user_id}/addresses", response_model=List[UserAddressResponse])
async def get_addresses(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all addresses for a user
    """
    user_service = UserService(db)
    addresses = await user_service.get_addresses(user_id)

    return [UserAddressResponse.from_orm(addr) for addr in addresses]


@router.put("/addresses/{address_id}", response_model=UserAddressResponse)
async def update_address(
    address_id: UUID,
    address_data: UserAddressUpdate,
    user_id: UUID = None,  # In production, extract from JWT token
    db: AsyncSession = Depends(get_db)
):
    """
    Update an address

    Note: In production, user_id should be extracted from JWT token
    to ensure users can only update their own addresses.
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID required"
        )

    user_service = UserService(db)
    address = await user_service.update_address(address_id, user_id, address_data)

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found or unauthorized"
        )

    return UserAddressResponse.from_orm(address)


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: UUID,
    user_id: UUID = None,  # In production, extract from JWT token
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an address
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID required"
        )

    user_service = UserService(db)
    success = await user_service.delete_address(address_id, user_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found or unauthorized"
        )

    return None


# ============================================================================
# Preference Endpoints
# ============================================================================

@router.get("/users/{user_id}/preferences", response_model=UserPreferenceResponse)
async def get_preferences(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user preferences
    """
    user_service = UserService(db)
    preferences = await user_service.get_preferences(user_id)

    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preferences not found"
        )

    return UserPreferenceResponse.from_orm(preferences)


@router.put("/users/{user_id}/preferences", response_model=UserPreferenceResponse)
async def update_preferences(
    user_id: UUID,
    preference_data: UserPreferenceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update user preferences
    """
    user_service = UserService(db)
    preferences = await user_service.update_preferences(user_id, preference_data)

    return UserPreferenceResponse.from_orm(preferences)


# ============================================================================
# Device Endpoints
# ============================================================================

@router.post("/users/{user_id}/devices", response_model=UserDeviceResponse, status_code=status.HTTP_201_CREATED)
async def register_device(
    user_id: UUID,
    device_data: UserDeviceCreate,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new device for push notifications
    """
    ip_address = request.client.host if request.client else None

    user_service = UserService(db)
    device = await user_service.register_device(user_id, device_data, ip_address)

    return UserDeviceResponse.from_orm(device)


@router.get("/users/{user_id}/devices", response_model=List[UserDeviceResponse])
async def get_devices(
    user_id: UUID,
    active_only: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user devices
    """
    user_service = UserService(db)
    devices = await user_service.get_devices(user_id, active_only)

    return [UserDeviceResponse.from_orm(dev) for dev in devices]


# ============================================================================
# Activity Endpoints
# ============================================================================

@router.get("/users/{user_id}/activities", response_model=List[UserActivityResponse])
async def get_activities(
    user_id: UUID,
    activity_type: Optional[ActivityType] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    Get user activity history
    """
    user_service = UserService(db)
    activities = await user_service.get_user_activities(
        user_id=user_id,
        activity_type=activity_type,
        limit=limit,
        offset=offset
    )

    return [UserActivityResponse.from_orm(activity) for activity in activities]


# ============================================================================
# Verification Endpoints
# ============================================================================

@router.post("/users/{user_id}/verifications", response_model=UserVerificationResponse, status_code=status.HTTP_201_CREATED)
async def create_verification(
    user_id: UUID,
    verification_data: UserVerificationCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit identity verification request
    """
    user_service = UserService(db)
    verification = await user_service.create_verification(user_id, verification_data)

    return UserVerificationResponse.from_orm(verification)


@router.post("/verifications/{verification_id}/documents/{document_type}", response_model=dict)
async def upload_verification_document(
    verification_id: UUID,
    document_type: str,  # 'front', 'back', 'selfie'
    file: UploadFile = File(...),
    user_id: UUID = None,  # In production, extract from JWT
    db: AsyncSession = Depends(get_db)
):
    """
    Upload verification document image

    document_type: 'front', 'back', or 'selfie'
    """
    if document_type not in ['front', 'back', 'selfie']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document type. Must be 'front', 'back', or 'selfie'"
        )

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID required"
        )

    # Read file content
    file_content = await file.read()

    # Upload file
    upload_service = UploadService()
    success, url, error = await upload_service.upload_verification_document(
        file_content=file_content,
        filename=file.filename,
        user_id=str(user_id),
        document_type=document_type,
        content_type=file.content_type
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error or "Failed to upload document"
        )

    # Update verification record
    # This would require additional logic to update the specific field

    return {
        "verification_id": verification_id,
        "document_type": document_type,
        "url": url,
        "uploaded_at": datetime.utcnow()
    }


@router.get("/verifications/pending", response_model=List[UserVerificationResponse])
async def get_pending_verifications(
    limit: int = 50,
    # In production, verify admin role from JWT
    db: AsyncSession = Depends(get_db)
):
    """
    Get pending verification requests (admin only)
    """
    user_service = UserService(db)
    verifications = await user_service.get_pending_verifications(limit)

    return [UserVerificationResponse.from_orm(v) for v in verifications]
