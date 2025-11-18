"""
Pydantic schemas for Auth Service
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
import re


# ===== USER SCHEMAS =====

class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    user_id: UUID
    email_verified: bool
    phone_verified: bool
    avatar_url: Optional[str]
    is_active: bool
    two_factor_enabled: bool
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


# ===== AUTHENTICATION SCHEMAS =====

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    two_factor_code: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # seconds
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class LogoutRequest(BaseModel):
    refresh_token: Optional[str] = None


# ===== PASSWORD SCHEMAS =====

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

    @validator('new_password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


# ===== EMAIL VERIFICATION SCHEMAS =====

class EmailVerificationRequest(BaseModel):
    email: EmailStr


class EmailVerificationConfirm(BaseModel):
    token: str


# ===== TWO-FACTOR AUTHENTICATION SCHEMAS =====

class TwoFactorEnableRequest(BaseModel):
    password: str


class TwoFactorEnableResponse(BaseModel):
    secret: str
    qr_code_url: str
    backup_codes: List[str]


class TwoFactorVerifyRequest(BaseModel):
    code: str


class TwoFactorDisableRequest(BaseModel):
    password: str
    code: str


# ===== OAUTH SCHEMAS =====

class OAuthLoginRequest(BaseModel):
    provider: str  # google, facebook, github
    code: str
    redirect_uri: str


class OAuthCallbackRequest(BaseModel):
    provider: str
    code: str
    state: Optional[str] = None


# ===== SESSION SCHEMAS =====

class SessionResponse(BaseModel):
    session_id: UUID
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    last_activity_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# ===== ROLE SCHEMAS =====

class RoleAssignment(BaseModel):
    role: str
    scope: Optional[str] = None


class UserRoleResponse(BaseModel):
    role_id: UUID
    user_id: UUID
    role: str
    scope: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ===== TOKEN VERIFICATION SCHEMAS =====

class TokenVerifyRequest(BaseModel):
    token: str


class TokenVerifyResponse(BaseModel):
    valid: bool
    user: Optional[UserResponse] = None
    error: Optional[str] = None


# ===== AUDIT LOG SCHEMAS =====

class AuditLogResponse(BaseModel):
    log_id: UUID
    user_id: Optional[UUID]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    ip_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
