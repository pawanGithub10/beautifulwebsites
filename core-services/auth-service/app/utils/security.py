"""
Security utilities for authentication
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
import secrets
import pyotp
import qrcode
import io
import base64
from app.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ===== PASSWORD FUNCTIONS =====

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ===== JWT FUNCTIONS =====

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify an access token and return payload
    """
    payload = decode_token(token)
    if payload and payload.get("type") == "access":
        return payload
    return None


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify a refresh token and return payload
    """
    payload = decode_token(token)
    if payload and payload.get("type") == "refresh":
        return payload
    return None


# ===== TOKEN GENERATION =====

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    return secrets.token_urlsafe(length)


def generate_verification_token() -> str:
    """Generate an email verification token"""
    return secrets.token_urlsafe(32)


def generate_password_reset_token() -> str:
    """Generate a password reset token"""
    return secrets.token_urlsafe(32)


# ===== TWO-FACTOR AUTHENTICATION =====

def generate_totp_secret() -> str:
    """Generate a TOTP secret for 2FA"""
    return pyotp.random_base32()


def generate_totp_uri(secret: str, email: str) -> str:
    """Generate a TOTP URI for QR code"""
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=email,
        issuer_name="Platform Auth"
    )


def generate_qr_code(uri: str) -> str:
    """
    Generate a QR code image and return as base64 data URL
    """
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


def verify_totp_code(secret: str, code: str) -> bool:
    """Verify a TOTP code"""
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=1)  # Allow 30s window


def generate_backup_codes(count: int = 10) -> list[str]:
    """Generate backup codes for 2FA"""
    return [secrets.token_hex(4).upper() for _ in range(count)]


# ===== EMAIL UTILITIES =====

def generate_email_verification_link(token: str) -> str:
    """Generate email verification link"""
    return settings.EMAIL_VERIFICATION_URL_TEMPLATE.format(
        frontend_url=settings.FRONTEND_URL,
        token=token
    )


def generate_password_reset_link(token: str) -> str:
    """Generate password reset link"""
    return settings.PASSWORD_RESET_URL_TEMPLATE.format(
        frontend_url=settings.FRONTEND_URL,
        token=token
    )


# ===== RATE LIMITING =====

def is_rate_limited(attempts: int, max_attempts: int) -> bool:
    """Check if user is rate limited"""
    return attempts >= max_attempts
