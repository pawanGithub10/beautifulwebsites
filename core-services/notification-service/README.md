# Notification Service

Multi-channel notification service supporting Email, SMS, Push, and In-App notifications for the multi-website platform.

## Features

### Multi-Channel Support
- **Email** - SMTP-based email notifications with HTML support
- **SMS** - Twilio-powered SMS notifications
- **Push** - Firebase Cloud Messaging for mobile push notifications
- **In-App** - Database-stored notifications for in-app display

### Template System
- Jinja2-based template engine
- Reusable templates with variable substitution
- Support for both text and HTML email templates
- Template versioning and management

### User Preferences
- Per-user notification preferences
- Channel-specific opt-in/opt-out
- Marketing notification controls
- Quiet hours support
- Digest frequency settings

### Reliability
- Automatic retry for failed notifications
- Delivery status tracking
- Provider-agnostic architecture
- Comprehensive error handling

### Tracking & Analytics
- Delivery confirmation
- Open tracking (email)
- Click tracking (email)
- Bounce handling
- Provider message ID storage

## Tech Stack

- **FastAPI** - Async Python web framework
- **SQLAlchemy** - Async ORM with PostgreSQL
- **Pydantic** - Data validation
- **aiosmtplib** - Async SMTP client
- **Twilio** - SMS provider
- **Firebase Admin SDK** - Push notifications
- **Jinja2** - Template engine
- **Celery** - Distributed task queue (for batch processing)

## Database Schema

### Tables

1. **notifications** - Main notification records
2. **notification_templates** - Reusable templates
3. **notification_preferences** - User preferences
4. **notification_batches** - Batch notification jobs
5. **notification_events** - Tracking events (opens, clicks)
6. **notification_providers** - Provider configurations

## API Endpoints

### Send Notifications

```bash
# Send generic notification
POST /api/v1/notifications/send

# Send email
POST /api/v1/notifications/send/email

# Send SMS
POST /api/v1/notifications/send/sms

# Send push notification
POST /api/v1/notifications/send/push
```

### Notification Management

```bash
# Get notification status
GET /api/v1/notifications/{notification_id}

# Get user notifications
GET /api/v1/notifications/user/{user_id}

# Mark as read
POST /api/v1/notifications/{notification_id}/read

# Retry failed notifications
POST /api/v1/notifications/retry-failed
```

### Templates

```bash
# Create template
POST /api/v1/notifications/templates
```

### User Preferences

```bash
# Get user preferences
GET /api/v1/notifications/preferences/{user_id}

# Update preferences
PUT /api/v1/notifications/preferences/{user_id}
```

## Usage Examples

### Send Email Notification

```python
import httpx

# Send email
response = await httpx.post(
    "http://localhost:8003/api/v1/notifications/send/email",
    json={
        "to": "user@example.com",
        "subject": "Welcome to Platform!",
        "body": "Thank you for signing up.",
        "html": "<h1>Welcome!</h1><p>Thank you for signing up.</p>"
    }
)
```

### Send SMS Notification

```python
# Send SMS
response = await httpx.post(
    "http://localhost:8003/api/v1/notifications/send/sms",
    json={
        "to": "+1234567890",
        "body": "Your verification code is 123456"
    }
)
```

### Send Push Notification

```python
# Send push notification
response = await httpx.post(
    "http://localhost:8003/api/v1/notifications/send/push",
    json={
        "device_token": "fcm_device_token_here",
        "title": "New Message",
        "body": "You have a new message from John",
        "data": {
            "message_id": "123",
            "sender_id": "456"
        }
    }
)
```

### Use Template

```python
# Create template
template_response = await httpx.post(
    "http://localhost:8003/api/v1/notifications/templates",
    json={
        "template_key": "order_confirmation",
        "subject_template": "Order #{{ order_id }} Confirmed",
        "body_template": "Hello {{ customer_name }}, your order #{{ order_id }} has been confirmed!",
        "html_template": "<h1>Order Confirmed</h1><p>Hello {{ customer_name }}, your order #{{ order_id }} has been confirmed!</p>",
        "variables": ["customer_name", "order_id"]
    }
)

# Send notification using template
response = await httpx.post(
    "http://localhost:8003/api/v1/notifications/send",
    json={
        "notification_type": "email",
        "recipient_email": "customer@example.com",
        "template_id": template_response.json()["template_id"],
        "template_variables": {
            "customer_name": "John Doe",
            "order_id": "ORD-12345"
        }
    }
)
```

### Update User Preferences

```python
# Update preferences
response = await httpx.put(
    "http://localhost:8003/api/v1/notifications/preferences/user-id-here",
    json={
        "email_enabled": True,
        "sms_enabled": False,
        "push_enabled": True,
        "marketing_enabled": False,
        "quiet_hours_start": "22:00",
        "quiet_hours_end": "08:00"
    }
)
```

## Configuration

### Environment Variables

```bash
# Service
SERVICE_NAME=notification-service
SERVICE_PORT=8003

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/notification_db

# Email (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=noreply@platform.com

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_FROM_NUMBER=+1234567890

# Push (Firebase)
FIREBASE_CREDENTIALS_PATH=/path/to/credentials.json
```

## Setup

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# Run migrations (tables created automatically on startup)

# Start the service
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

### Docker

```bash
# Build image
docker build -t notification-service .

# Run container
docker run -d \
  -p 8003:8003 \
  --env-file .env \
  --name notification-service \
  notification-service
```

## Provider Setup

### SMTP (Email)

1. **Gmail** (recommended for development):
   - Enable 2FA on your Google account
   - Generate App Password: https://myaccount.google.com/apppasswords
   - Use App Password as `SMTP_PASSWORD`

2. **SendGrid** (recommended for production):
   - Sign up at https://sendgrid.com
   - Create API key
   - Use SMTP relay: smtp.sendgrid.net:587

### Twilio (SMS)

1. Sign up at https://www.twilio.com
2. Get Account SID and Auth Token from console
3. Purchase a phone number
4. Set in environment variables

### Firebase (Push)

1. Create Firebase project at https://console.firebase.google.com
2. Go to Project Settings > Service Accounts
3. Generate new private key (downloads JSON file)
4. Set `FIREBASE_CREDENTIALS_PATH` to the JSON file path

## Architecture

### Service Flow

```
Client Request
    ↓
API Router (FastAPI)
    ↓
NotificationService (Business Logic)
    ↓
    ├→ EmailService (SMTP)
    ├→ SMSService (Twilio)
    ├→ PushService (Firebase)
    └→ Database (PostgreSQL)
```

### Retry Logic

Failed notifications are automatically retried:
1. Initial send attempt
2. If failed, mark as FAILED and increment retry_count
3. Background job retries failed notifications (up to max_retries)
4. Exponential backoff between retries

### Status Lifecycle

```
PENDING → SENT → DELIVERED → OPENED/CLICKED
   ↓         ↓
FAILED ← BOUNCED
```

## Integration with Other Services

### Auth Service Integration

```python
# Send welcome email after signup
async def send_welcome_email(user_email: str, user_name: str):
    await httpx.post(
        "http://notification-service:8003/api/v1/notifications/send/email",
        json={
            "to": user_email,
            "subject": "Welcome to Platform!",
            "body": f"Hello {user_name}, welcome to our platform!",
            "template_id": "welcome_email_template_id",
            "template_variables": {"user_name": user_name}
        }
    )
```

### Booking Service Integration

```python
# Send booking confirmation
async def send_booking_confirmation(booking):
    await httpx.post(
        "http://notification-service:8003/api/v1/notifications/send",
        json={
            "notification_type": "email",
            "recipient_email": booking.customer_email,
            "template_id": "booking_confirmation_template_id",
            "template_variables": {
                "customer_name": booking.customer_name,
                "booking_id": str(booking.booking_id),
                "service_name": booking.service_name,
                "date": booking.date.isoformat()
            }
        }
    )
```

## Performance Considerations

- **Async I/O**: All email/SMS/push operations are async
- **Connection Pooling**: Database connection pool (10 connections)
- **Rate Limiting**: Built-in rate limiting (configurable)
- **Batch Processing**: Support for batch notifications via Celery
- **Caching**: Redis caching for templates and preferences

## Monitoring

### Health Check

```bash
curl http://localhost:8003/health
```

### Metrics to Monitor

- Notification success/failure rate by channel
- Average delivery time
- Retry count distribution
- Provider API response times
- Queue depth (for batch processing)

## Security

- **Authentication**: Requires valid JWT token from Auth Service
- **Rate Limiting**: Prevents abuse
- **Input Validation**: Pydantic schemas validate all inputs
- **SQL Injection**: Protected by SQLAlchemy ORM
- **Credential Storage**: Never log or expose provider credentials

## Future Enhancements

- [ ] Support for additional providers (SendGrid, Mailgun, etc.)
- [ ] Webhook support for delivery status callbacks
- [ ] A/B testing for notification content
- [ ] Notification scheduling
- [ ] Digest notifications (daily/weekly summaries)
- [ ] Unsubscribe link management
- [ ] Email preview and testing tools
- [ ] Advanced analytics dashboard

## Port

**8003** - Notification Service HTTP API

## Version

**2.0.0** - Multi-channel notification service with templates and preferences
