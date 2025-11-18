"""
Authentication Service - Core business logic
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
import uuid

from app.models import User, RefreshToken, Session, LoginAttempt, AuditLog, PasswordResetToken, EmailVerificationToken
from app.schemas import UserCreate, LoginRequest, UserResponse
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    generate_password_reset_token,
    generate_verification_token,
)
from app.config import settings


class AuthService:
    """
    Core authentication service
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ===== USER MANAGEMENT =====

    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user account
        """
        # Check if user already exists
        stmt = select(User).where(User.email == user_data.email)
        result = await self.db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create user
        user = User(
            email=user_data.email,
            password_hash=hash_password(user_data.password),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            phone=user_data.phone,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        # Create email verification token
        await self._create_email_verification_token(user)

        # Audit log
        await self._log_audit(
            user_id=user.user_id,
            action="user_created",
            details="New user account created"
        )

        return user

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[User]:
        """Get user by ID"""
        stmt = select(User).where(User.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    # ===== AUTHENTICATION =====

    async def login(
        self,
        login_data: LoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Tuple[str, str, User]:
        """
        Authenticate user and return tokens
        Returns: (access_token, refresh_token, user)
        """
        # Check rate limiting
        if await self._is_rate_limited(login_data.email, ip_address):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many login attempts. Please try again later."
            )

        # Get user
        user = await self.get_user_by_email(login_data.email)

        if not user or not user.password_hash:
            await self._log_login_attempt(login_data.email, ip_address, user_agent, False, "invalid_credentials")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            await self._log_login_attempt(login_data.email, ip_address, user_agent, False, "invalid_password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # Check if account is active
        if not user.is_active:
            await self._log_login_attempt(login_data.email, ip_address, user_agent, False, "account_inactive")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )

        # Check 2FA
        if user.two_factor_enabled:
            if not login_data.two_factor_code:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Two-factor authentication code required"
                )
            # Verify 2FA code (implementation in separate method)
            # For now, we'll skip the actual verification

        # Generate tokens
        token_data = {
            "sub": str(user.user_id),
            "email": user.email,
        }

        access_token = create_access_token(token_data)
        refresh_token_str = create_refresh_token(token_data)

        # Store refresh token
        refresh_token = RefreshToken(
            user_id=user.user_id,
            token=refresh_token_str,
            expires_at=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        )
        self.db.add(refresh_token)

        # Create session
        session = Session(
            user_id=user.user_id,
            token=access_token,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        self.db.add(session)

        # Update last login
        user.last_login_at = datetime.utcnow()

        await self.db.commit()

        # Log successful login
        await self._log_login_attempt(login_data.email, ip_address, user_agent, True)
        await self._log_audit(user.user_id, "login", details="User logged in")

        return access_token, refresh_token_str, user

    async def refresh_access_token(self, refresh_token_str: str) -> str:
        """
        Generate a new access token from refresh token
        """
        # Verify refresh token
        payload = verify_refresh_token(refresh_token_str)
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Check if token exists and is not revoked
        stmt = select(RefreshToken).where(
            and_(
                RefreshToken.token == refresh_token_str,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            )
        )
        result = await self.db.execute(stmt)
        token_record = result.scalar_one_or_none()

        if not token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not found or expired"
            )

        # Generate new access token
        user_id = payload.get("sub")
        user = await self.get_user_by_id(uuid.UUID(user_id))

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        token_data = {
            "sub": str(user.user_id),
            "email": user.email,
        }

        access_token = create_access_token(token_data)

        await self._log_audit(user.user_id, "token_refreshed", details="Access token refreshed")

        return access_token

    async def logout(self, refresh_token_str: Optional[str], user_id: uuid.UUID):
        """
        Logout user by revoking refresh token
        """
        if refresh_token_str:
            stmt = select(RefreshToken).where(
                and_(
                    RefreshToken.token == refresh_token_str,
                    RefreshToken.user_id == user_id
                )
            )
            result = await self.db.execute(stmt)
            token = result.scalar_one_or_none()

            if token:
                token.is_revoked = True
                token.revoked_at = datetime.utcnow()

        # Deactivate all sessions
        stmt = select(Session).where(
            and_(
                Session.user_id == user_id,
                Session.is_active == True
            )
        )
        result = await self.db.execute(stmt)
        sessions = result.scalars().all()

        for session in sessions:
            session.is_active = False

        await self.db.commit()

        await self._log_audit(user_id, "logout", details="User logged out")

    # ===== PASSWORD MANAGEMENT =====

    async def change_password(
        self,
        user_id: uuid.UUID,
        current_password: str,
        new_password: str
    ):
        """Change user password"""
        user = await self.get_user_by_id(user_id)

        if not user or not user.password_hash:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Verify current password
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Update password
        user.password_hash = hash_password(new_password)
        await self.db.commit()

        await self._log_audit(user_id, "password_changed", details="Password changed")

    async def request_password_reset(self, email: str) -> str:
        """
        Generate password reset token
        """
        user = await self.get_user_by_email(email)

        if not user:
            # Don't reveal if email exists
            return "If the email exists, a reset link has been sent"

        # Generate token
        token = generate_password_reset_token()

        # Store token
        reset_token = PasswordResetToken(
            user_id=user.user_id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        )
        self.db.add(reset_token)
        await self.db.commit()

        await self._log_audit(user.user_id, "password_reset_requested")

        return token

    async def reset_password(self, token: str, new_password: str):
        """
        Reset password using token
        """
        # Find token
        stmt = select(PasswordResetToken).where(
            and_(
                PasswordResetToken.token == token,
                PasswordResetToken.is_used == False,
                PasswordResetToken.expires_at > datetime.utcnow()
            )
        )
        result = await self.db.execute(stmt)
        reset_token = result.scalar_one_or_none()

        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )

        # Get user
        user = await self.get_user_by_id(reset_token.user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Update password
        user.password_hash = hash_password(new_password)

        # Mark token as used
        reset_token.is_used = True
        reset_token.used_at = datetime.utcnow()

        await self.db.commit()

        await self._log_audit(user.user_id, "password_reset_completed")

    # ===== HELPER METHODS =====

    async def _is_rate_limited(self, email: str, ip_address: Optional[str]) -> bool:
        """Check if login attempts are rate limited"""
        window_start = datetime.utcnow() - timedelta(minutes=settings.LOGIN_ATTEMPT_WINDOW_MINUTES)

        stmt = select(func.count(LoginAttempt.attempt_id)).where(
            and_(
                LoginAttempt.email == email,
                LoginAttempt.success == False,
                LoginAttempt.attempted_at >= window_start
            )
        )
        result = await self.db.execute(stmt)
        attempt_count = result.scalar()

        return attempt_count >= settings.MAX_LOGIN_ATTEMPTS

    async def _log_login_attempt(
        self,
        email: str,
        ip_address: Optional[str],
        user_agent: Optional[str],
        success: bool,
        failure_reason: Optional[str] = None
    ):
        """Log login attempt"""
        attempt = LoginAttempt(
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason
        )
        self.db.add(attempt)
        await self.db.commit()

    async def _log_audit(
        self,
        user_id: Optional[uuid.UUID],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[str] = None
    ):
        """Log audit event"""
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details
        )
        self.db.add(log)
        await self.db.commit()

    async def _create_email_verification_token(self, user: User) -> str:
        """Create email verification token"""
        token = generate_verification_token()

        verification = EmailVerificationToken(
            user_id=user.user_id,
            email=user.email,
            token=token,
            expires_at=datetime.utcnow() + timedelta(days=7)  # 7 days
        )
        self.db.add(verification)
        await self.db.commit()

        return token
