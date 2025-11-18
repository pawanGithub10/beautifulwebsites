# User Service

User profile management service for the multi-website platform. Handles user profiles, addresses, preferences, devices, activity tracking, and identity verification.

## Features

### User Profiles
- Extended profile information beyond authentication
- Avatar upload and management (S3 or local storage)
- Social links and bio
- Verification badges
- User statistics (orders, bookings, total spent)

### Address Management
- Multiple addresses per user
- Shipping and billing addresses
- Default address selection
- Address verification status
- Geocoding support (latitude/longitude)

### User Preferences
- Privacy settings (profile visibility)
- Communication preferences (email, SMS, push)
- Display preferences (theme, currency, date/time format)
- Default shipping/billing addresses
- Custom preference storage (JSONB)

### Device Management
- Multi-device support
- Device registration for push notifications
- Device activity tracking
- Device type detection (web, iOS, Android, etc.)
- Last seen and location tracking

### Activity Logging
- Comprehensive activity tracking
- Login/logout events
- Profile updates
- Order and booking events
- Review posts
- Custom metadata support

### Identity Verification
- Document upload support
- Multiple verification types (ID, passport, business license)
- Admin review workflow
- Status tracking (pending, approved, rejected)
- Expiry date management

## Tech Stack

- **FastAPI** - Async Python web framework
- **SQLAlchemy** - Async ORM with PostgreSQL
- **Pydantic** - Data validation
- **Pillow** - Image processing
- **boto3** - AWS S3 integration
- **Redis** - Caching layer

## Database Schema

### Tables

1. **user_profiles** - Extended user profile data
2. **user_addresses** - User addresses
3. **user_preferences** - User preferences and settings
4. **user_devices** - Registered devices
5. **user_activities** - Activity log
6. **user_verifications** - Identity verification documents

## API Endpoints

### Profile Management

```bash
# Create profile
POST /api/v1/profiles

# Get profile
GET /api/v1/profiles/{user_id}

# Get complete profile (with addresses, preferences, devices)
GET /api/v1/profiles/{user_id}/complete

# Update profile
PUT /api/v1/profiles/{user_id}

# Upload avatar
POST /api/v1/profiles/{user_id}/avatar
```

### Address Management

```bash
# Create address
POST /api/v1/users/{user_id}/addresses

# Get all addresses
GET /api/v1/users/{user_id}/addresses

# Update address
PUT /api/v1/addresses/{address_id}

# Delete address
DELETE /api/v1/addresses/{address_id}
```

### Preferences

```bash
# Get preferences
GET /api/v1/users/{user_id}/preferences

# Update preferences
PUT /api/v1/users/{user_id}/preferences
```

### Devices

```bash
# Register device
POST /api/v1/users/{user_id}/devices

# Get devices
GET /api/v1/users/{user_id}/devices?active_only=true
```

### Activity

```bash
# Get user activities
GET /api/v1/users/{user_id}/activities?activity_type=login&limit=50
```

### Verification

```bash
# Create verification request
POST /api/v1/users/{user_id}/verifications

# Upload verification document
POST /api/v1/verifications/{verification_id}/documents/{document_type}

# Get pending verifications (admin)
GET /api/v1/verifications/pending
```

## Usage Examples

### Create User Profile

```python
import httpx

# Create profile (typically called by Auth Service after signup)
response = await httpx.post(
    "http://localhost:8001/api/v1/profiles",
    json={
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "display_name": "John Doe",
        "bio": "Software developer and coffee enthusiast",
        "timezone": "America/New_York",
        "language": "en",
        "country_code": "US"
    }
)
```

### Upload Avatar

```python
import httpx

# Upload avatar
with open("avatar.jpg", "rb") as f:
    response = await httpx.post(
        f"http://localhost:8001/api/v1/profiles/{user_id}/avatar",
        files={"file": ("avatar.jpg", f, "image/jpeg")}
    )

print(response.json())
# {
#   "avatar_url": "https://bucket.s3.amazonaws.com/avatars/user-id/uuid.jpg",
#   "user_id": "550e8400-e29b-41d4-a716-446655440000",
#   "uploaded_at": "2024-01-15T10:30:00Z"
# }
```

### Add Address

```python
# Add shipping address
response = await httpx.post(
    f"http://localhost:8001/api/v1/users/{user_id}/addresses",
    json={
        "address_type": "shipping",
        "label": "Home",
        "full_name": "John Doe",
        "phone": "+1234567890",
        "address_line1": "123 Main Street",
        "address_line2": "Apt 4B",
        "city": "New York",
        "state": "NY",
        "postal_code": "10001",
        "country_code": "US",
        "is_default": True
    }
)
```

### Update Preferences

```python
# Update user preferences
response = await httpx.put(
    f"http://localhost:8001/api/v1/users/{user_id}/preferences",
    json={
        "theme": "dark",
        "currency": "USD",
        "email_notifications": True,
        "sms_notifications": False,
        "push_notifications": True,
        "marketing_emails": False,
        "profile_visibility": "public"
    }
)
```

### Register Device

```python
# Register mobile device
response = await httpx.post(
    f"http://localhost:8001/api/v1/users/{user_id}/devices",
    json={
        "device_type": "ios",
        "device_name": "iPhone 13 Pro",
        "device_token": "fcm_token_here",
        "os_name": "iOS",
        "os_version": "16.2",
        "app_version": "2.0.0"
    }
)
```

### Submit Verification

```python
# Create verification request
response = await httpx.post(
    f"http://localhost:8001/api/v1/users/{user_id}/verifications",
    json={
        "verification_type": "government_id",
        "document_number": "DL123456",
        "issuing_country": "US",
        "expiry_date": "2028-12-31T00:00:00Z"
    }
)

verification_id = response.json()["verification_id"]

# Upload front image
with open("id_front.jpg", "rb") as f:
    await httpx.post(
        f"http://localhost:8001/api/v1/verifications/{verification_id}/documents/front",
        files={"file": ("id_front.jpg", f, "image/jpeg")}
    )

# Upload back image
with open("id_back.jpg", "rb") as f:
    await httpx.post(
        f"http://localhost:8001/api/v1/verifications/{verification_id}/documents/back",
        files={"file": ("id_back.jpg", f, "image/jpeg")}
    )

# Upload selfie
with open("selfie.jpg", "rb") as f:
    await httpx.post(
        f"http://localhost:8001/api/v1/verifications/{verification_id}/documents/selfie",
        files={"file": ("selfie.jpg", f, "image/jpeg")}
    )
```

## Configuration

### Environment Variables

```bash
# Service
SERVICE_NAME=user-service
SERVICE_PORT=8001

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/user_db

# Redis
REDIS_URL=redis://redis:6379/2

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_S3_BUCKET=your-bucket
AWS_S3_REGION=us-east-1

# File Upload
MAX_UPLOAD_SIZE_MB=5

# Auth Integration
AUTH_SERVICE_URL=http://auth-service:8000
JWT_SECRET_KEY=your-secret-key

# Notification Integration
NOTIFICATION_SERVICE_URL=http://notification-service:8003
```

## Setup

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the service
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### Docker

```bash
# Build image
docker build -t user-service .

# Run container
docker run -d \
  -p 8001:8001 \
  --env-file .env \
  --name user-service \
  user-service
```

## File Storage

### S3 Configuration

1. Create an S3 bucket in AWS
2. Set up IAM user with S3 permissions
3. Configure bucket CORS for uploads:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": []
  }
]
```

4. Set environment variables:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_S3_BUCKET`
   - `AWS_S3_REGION`

### Local Storage

If S3 credentials are not configured, files will be stored locally in the `uploads/` directory. This is suitable for development but not recommended for production.

## Integration with Other Services

### Auth Service Integration

The User Service works closely with the Auth Service:

```python
# When Auth Service creates a new user, it should call User Service:
async def after_user_signup(user_id: UUID, email: str, first_name: str, last_name: str):
    # Create user profile
    await httpx.post(
        "http://user-service:8001/api/v1/profiles",
        json={
            "user_id": str(user_id),
            "display_name": f"{first_name} {last_name}"
        }
    )
```

### Notification Service Integration

When user preferences change, update notification preferences:

```python
# When user updates notification preferences
async def sync_notification_preferences(user_id: UUID, preferences: dict):
    await httpx.put(
        f"http://notification-service:8003/api/v1/preferences/{user_id}",
        json={
            "email_enabled": preferences["email_notifications"],
            "sms_enabled": preferences["sms_notifications"],
            "push_enabled": preferences["push_notifications"],
            "marketing_enabled": preferences["marketing_emails"]
        }
    )
```

## Architecture

### Service Flow

```
Client Request
    ↓
API Router (FastAPI)
    ↓
UserService (Business Logic)
    ↓
    ├→ Database (PostgreSQL)
    ├→ Redis (Cache)
    ├→ S3 (File Storage)
    └→ Other Services (Auth, Notification)
```

### Image Processing

Avatar images are automatically:
1. Validated (type and size)
2. Resized to max 1000x1000
3. Converted to JPEG
4. Optimized for web (85% quality)
5. Uploaded to S3 or local storage

### Caching Strategy

- User profiles cached for 5 minutes
- User preferences cached for 10 minutes
- Redis cache invalidated on updates

## Security

- **Authorization**: All endpoints should verify JWT token in production
- **File Validation**: Strict file type and size validation
- **SQL Injection**: Protected by SQLAlchemy ORM
- **XSS**: Sanitized input via Pydantic validation
- **CORS**: Configured for production domains

## Performance Considerations

- **Async I/O**: All database operations are async
- **Connection Pooling**: 10 connections with 20 overflow
- **Caching**: Redis caching for frequently accessed data
- **Image Optimization**: Automatic image resizing and compression
- **Indexing**: Database indexes on user_id and foreign keys

## Monitoring

### Health Check

```bash
curl http://localhost:8001/health
```

### Metrics to Monitor

- Profile creation rate
- Avatar upload success rate
- Address CRUD operations
- Device registration rate
- Verification request volume
- API response times

## Future Enhancements

- [ ] Profile completion percentage
- [ ] Social graph (friends, followers)
- [ ] Profile sharing and privacy controls
- [ ] Geolocation services for address autocomplete
- [ ] Face recognition for selfie verification
- [ ] Document OCR for automatic data extraction
- [ ] Profile badges and achievements
- [ ] User groups and communities

## Port

**8001** - User Service HTTP API

## Version

**2.0.0** - User profile management with addresses, preferences, and verification
