"""
Main User Service - Business logic for user profile management
"""

from typing import Optional, List, Dict, Any
import logging
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import selectinload

from app.models import (
    UserProfile, UserAddress, UserPreference, UserDevice,
    UserActivity, UserVerification, ActivityType, VerificationStatus
)
from app.schemas import (
    UserProfileCreate, UserProfileUpdate, UserProfileResponse,
    UserAddressCreate, UserAddressUpdate, UserAddressResponse,
    UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse,
    UserDeviceCreate, UserDeviceUpdate, UserDeviceResponse,
    UserActivityCreate, UserActivityResponse,
    UserVerificationCreate, UserVerificationUpdate, UserVerificationResponse,
    CompleteUserProfile
)

logger = logging.getLogger(__name__)


class UserService:
    """
    User profile management service
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========================================================================
    # User Profile Management
    # ========================================================================

    async def create_profile(self, profile_data: UserProfileCreate) -> UserProfile:
        """
        Create a new user profile

        Args:
            profile_data: Profile creation data

        Returns:
            Created user profile
        """
        # Check if profile already exists
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == profile_data.user_id)
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.warning(f"Profile already exists for user {profile_data.user_id}")
            return existing

        # Create profile
        profile = UserProfile(
            user_id=profile_data.user_id,
            display_name=profile_data.display_name,
            bio=profile_data.bio,
            timezone=profile_data.timezone,
            language=profile_data.language,
            country_code=profile_data.country_code,
            website=profile_data.website,
            twitter_handle=profile_data.twitter_handle,
            linkedin_url=profile_data.linkedin_url
        )

        self.db.add(profile)

        # Create default preferences
        preferences = UserPreference(user_id=profile_data.user_id)
        self.db.add(preferences)

        await self.db.commit()
        await self.db.refresh(profile)

        logger.info(f"Created profile for user {profile_data.user_id}")

        return profile

    async def get_profile(self, user_id: UUID) -> Optional[UserProfile]:
        """
        Get user profile by user ID

        Args:
            user_id: User ID

        Returns:
            User profile or None
        """
        result = await self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_profile(
        self,
        user_id: UUID,
        profile_data: UserProfileUpdate
    ) -> Optional[UserProfile]:
        """
        Update user profile

        Args:
            user_id: User ID
            profile_data: Update data

        Returns:
            Updated profile or None
        """
        # Get profile
        profile = await self.get_profile(user_id)
        if not profile:
            logger.error(f"Profile not found for user {user_id}")
            return None

        # Update fields
        update_data = profile_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)

        await self.db.commit()
        await self.db.refresh(profile)

        # Log activity
        await self._log_activity(
            user_id=user_id,
            activity_type=ActivityType.PROFILE_UPDATE,
            description="Profile updated"
        )

        logger.info(f"Updated profile for user {user_id}")

        return profile

    async def update_avatar(self, user_id: UUID, avatar_url: str) -> Optional[UserProfile]:
        """
        Update user avatar

        Args:
            user_id: User ID
            avatar_url: Avatar URL

        Returns:
            Updated profile or None
        """
        profile = await self.get_profile(user_id)
        if not profile:
            return None

        profile.avatar_url = avatar_url
        await self.db.commit()
        await self.db.refresh(profile)

        # Log activity
        await self._log_activity(
            user_id=user_id,
            activity_type=ActivityType.AVATAR_UPLOAD,
            description="Avatar uploaded"
        )

        return profile

    async def get_complete_profile(self, user_id: UUID) -> Optional[CompleteUserProfile]:
        """
        Get complete user profile with all related data

        Args:
            user_id: User ID

        Returns:
            Complete profile data
        """
        # Get profile with relationships
        result = await self.db.execute(
            select(UserProfile)
            .options(
                selectinload(UserProfile.addresses),
                selectinload(UserProfile.devices),
                selectinload(UserProfile.preferences)
            )
            .where(UserProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()

        if not profile:
            return None

        return CompleteUserProfile(
            profile=UserProfileResponse.from_orm(profile),
            addresses=[UserAddressResponse.from_orm(addr) for addr in profile.addresses],
            preferences=UserPreferenceResponse.from_orm(profile.preferences) if profile.preferences else None,
            devices=[UserDeviceResponse.from_orm(dev) for dev in profile.devices]
        )

    # ========================================================================
    # Address Management
    # ========================================================================

    async def create_address(
        self,
        user_id: UUID,
        address_data: UserAddressCreate
    ) -> UserAddress:
        """
        Create a new address for user

        Args:
            user_id: User ID
            address_data: Address data

        Returns:
            Created address
        """
        # If this is marked as default, unset other defaults
        if address_data.is_default:
            await self.db.execute(
                update(UserAddress)
                .where(UserAddress.user_id == user_id)
                .values(is_default=False)
            )

        # Create address
        address = UserAddress(
            user_id=user_id,
            **address_data.dict()
        )

        self.db.add(address)
        await self.db.commit()
        await self.db.refresh(address)

        # Log activity
        await self._log_activity(
            user_id=user_id,
            activity_type=ActivityType.ADDRESS_ADD,
            description=f"Address added: {address.label or address.address_type}"
        )

        logger.info(f"Created address for user {user_id}")

        return address

    async def get_addresses(self, user_id: UUID) -> List[UserAddress]:
        """
        Get all addresses for a user

        Args:
            user_id: User ID

        Returns:
            List of addresses
        """
        result = await self.db.execute(
            select(UserAddress)
            .where(UserAddress.user_id == user_id)
            .order_by(UserAddress.is_default.desc(), UserAddress.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_address(self, address_id: UUID) -> Optional[UserAddress]:
        """Get address by ID"""
        result = await self.db.execute(
            select(UserAddress).where(UserAddress.address_id == address_id)
        )
        return result.scalar_one_or_none()

    async def update_address(
        self,
        address_id: UUID,
        user_id: UUID,
        address_data: UserAddressUpdate
    ) -> Optional[UserAddress]:
        """
        Update an address

        Args:
            address_id: Address ID
            user_id: User ID (for authorization)
            address_data: Update data

        Returns:
            Updated address or None
        """
        # Get address
        address = await self.get_address(address_id)
        if not address or address.user_id != user_id:
            return None

        # If setting as default, unset other defaults
        if address_data.is_default:
            await self.db.execute(
                update(UserAddress)
                .where(
                    and_(
                        UserAddress.user_id == user_id,
                        UserAddress.address_id != address_id
                    )
                )
                .values(is_default=False)
            )

        # Update fields
        update_data = address_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(address, field, value)

        await self.db.commit()
        await self.db.refresh(address)

        # Log activity
        await self._log_activity(
            user_id=user_id,
            activity_type=ActivityType.ADDRESS_UPDATE,
            description=f"Address updated: {address.label or address.address_type}"
        )

        return address

    async def delete_address(self, address_id: UUID, user_id: UUID) -> bool:
        """
        Delete an address

        Args:
            address_id: Address ID
            user_id: User ID (for authorization)

        Returns:
            Success status
        """
        # Get address
        address = await self.get_address(address_id)
        if not address or address.user_id != user_id:
            return False

        await self.db.delete(address)
        await self.db.commit()

        # Log activity
        await self._log_activity(
            user_id=user_id,
            activity_type=ActivityType.ADDRESS_DELETE,
            description=f"Address deleted: {address.label or address.address_type}"
        )

        return True

    # ========================================================================
    # Preference Management
    # ========================================================================

    async def get_preferences(self, user_id: UUID) -> Optional[UserPreference]:
        """Get user preferences"""
        result = await self.db.execute(
            select(UserPreference).where(UserPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_preferences(
        self,
        user_id: UUID,
        preference_data: UserPreferenceUpdate
    ) -> UserPreference:
        """
        Update user preferences

        Args:
            user_id: User ID
            preference_data: Preference data

        Returns:
            Updated preferences
        """
        # Get or create preferences
        preferences = await self.get_preferences(user_id)

        if not preferences:
            preferences = UserPreference(user_id=user_id)
            self.db.add(preferences)

        # Update fields
        update_data = preference_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(preferences, field, value)

        await self.db.commit()
        await self.db.refresh(preferences)

        # Log activity
        await self._log_activity(
            user_id=user_id,
            activity_type=ActivityType.PREFERENCE_UPDATE,
            description="Preferences updated"
        )

        return preferences

    # ========================================================================
    # Device Management
    # ========================================================================

    async def register_device(
        self,
        user_id: UUID,
        device_data: UserDeviceCreate,
        ip_address: Optional[str] = None
    ) -> UserDevice:
        """
        Register a new device

        Args:
            user_id: User ID
            device_data: Device data
            ip_address: IP address

        Returns:
            Registered device
        """
        device = UserDevice(
            user_id=user_id,
            last_ip_address=ip_address,
            **device_data.dict()
        )

        self.db.add(device)
        await self.db.commit()
        await self.db.refresh(device)

        logger.info(f"Registered device for user {user_id}: {device.device_name}")

        return device

    async def get_devices(self, user_id: UUID, active_only: bool = False) -> List[UserDevice]:
        """
        Get user devices

        Args:
            user_id: User ID
            active_only: Return only active devices

        Returns:
            List of devices
        """
        query = select(UserDevice).where(UserDevice.user_id == user_id)

        if active_only:
            query = query.where(UserDevice.is_active == True)

        query = query.order_by(UserDevice.last_active_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_device_activity(
        self,
        device_id: UUID,
        ip_address: Optional[str] = None
    ) -> Optional[UserDevice]:
        """Update device last activity"""
        device = await self.db.get(UserDevice, device_id)
        if not device:
            return None

        device.last_active_at = datetime.utcnow()
        if ip_address:
            device.last_ip_address = ip_address

        await self.db.commit()
        await self.db.refresh(device)

        return device

    # ========================================================================
    # Activity Logging
    # ========================================================================

    async def _log_activity(
        self,
        user_id: UUID,
        activity_type: ActivityType,
        description: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        device_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Internal method to log user activity"""
        activity = UserActivity(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            device_id=device_id,
            metadata=metadata or {}
        )

        self.db.add(activity)
        await self.db.commit()

    async def get_user_activities(
        self,
        user_id: UUID,
        activity_type: Optional[ActivityType] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[UserActivity]:
        """
        Get user activity history

        Args:
            user_id: User ID
            activity_type: Optional filter by activity type
            limit: Number of results
            offset: Pagination offset

        Returns:
            List of activities
        """
        query = select(UserActivity).where(UserActivity.user_id == user_id)

        if activity_type:
            query = query.where(UserActivity.activity_type == activity_type)

        query = query.order_by(UserActivity.created_at.desc()).limit(limit).offset(offset)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    # ========================================================================
    # Verification Management
    # ========================================================================

    async def create_verification(
        self,
        user_id: UUID,
        verification_data: UserVerificationCreate
    ) -> UserVerification:
        """
        Create verification request

        Args:
            user_id: User ID
            verification_data: Verification data

        Returns:
            Created verification
        """
        verification = UserVerification(
            user_id=user_id,
            **verification_data.dict()
        )

        self.db.add(verification)
        await self.db.commit()
        await self.db.refresh(verification)

        logger.info(f"Created verification request for user {user_id}")

        return verification

    async def update_verification_status(
        self,
        verification_id: UUID,
        status: VerificationStatus,
        reviewed_by: UUID,
        rejection_reason: Optional[str] = None
    ) -> Optional[UserVerification]:
        """
        Update verification status (admin only)

        Args:
            verification_id: Verification ID
            status: New status
            reviewed_by: Admin user ID
            rejection_reason: Reason for rejection

        Returns:
            Updated verification
        """
        verification = await self.db.get(UserVerification, verification_id)
        if not verification:
            return None

        verification.status = status
        verification.reviewed_by = reviewed_by
        verification.reviewed_at = datetime.utcnow()

        if rejection_reason:
            verification.rejection_reason = rejection_reason

        # If approved, update user profile verification status
        if status == VerificationStatus.APPROVED:
            profile = await self.get_profile(verification.user_id)
            if profile:
                profile.is_verified = True
                profile.verified_at = datetime.utcnow()
                profile.verification_badge = verification.verification_type.value

        await self.db.commit()
        await self.db.refresh(verification)

        return verification

    async def get_pending_verifications(self, limit: int = 50) -> List[UserVerification]:
        """Get pending verification requests (admin)"""
        result = await self.db.execute(
            select(UserVerification)
            .where(UserVerification.status == VerificationStatus.PENDING)
            .order_by(UserVerification.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
