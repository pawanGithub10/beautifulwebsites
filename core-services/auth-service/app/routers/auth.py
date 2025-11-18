"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import (
    UserCreate, UserResponse, LoginRequest, LoginResponse,
    RefreshTokenRequest, TokenResponse, LogoutRequest,
    PasswordChangeRequest, PasswordResetRequest, PasswordResetConfirm
)
from app.services.auth_service import AuthService
from app.config import settings

router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user account
    """
    auth_service = AuthService(db)
    user = await auth_service.create_user(user_data)
    return user


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return tokens
    """
    auth_service = AuthService(db)

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    access_token, refresh_token, user = await auth_service.login(
        login_data,
        ip_address=ip_address,
        user_agent=user_agent
    )

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.from_orm(user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate new access token from refresh token
    """
    auth_service = AuthService(db)
    access_token = await auth_service.refresh_access_token(refresh_data.refresh_token)

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    logout_data: LogoutRequest,
    # current_user would come from JWT dependency
    db: AsyncSession = Depends(get_db)
):
    """
    Logout user and revoke tokens
    """
    # In production, extract user_id from JWT token
    # For now, we'll use a placeholder
    auth_service = AuthService(db)
    # await auth_service.logout(logout_data.refresh_token, current_user_id)
    return None


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: PasswordChangeRequest,
    # current_user would come from JWT dependency
    db: AsyncSession = Depends(get_db)
):
    """
    Change user password
    """
    auth_service = AuthService(db)
    # await auth_service.change_password(current_user_id, password_data.current_password, password_data.new_password)
    return None


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Request password reset email
    """
    auth_service = AuthService(db)
    token = await auth_service.request_password_reset(reset_request.email)

    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db)
):
    """
    Reset password using token
    """
    auth_service = AuthService(db)
    await auth_service.reset_password(reset_data.token, reset_data.new_password)

    return {"message": "Password has been reset successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    # current_user would come from JWT dependency
    db: AsyncSession = Depends(get_db)
):
    """
    Get current authenticated user
    """
    # In production, this would return the authenticated user
    # For now, return placeholder
    raise HTTPException(status_code=501, detail="Not implemented")
