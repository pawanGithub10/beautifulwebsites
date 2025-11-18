# Auth Service

Authentication and authorization service for the multi-website platform.

## Features

✅ **User Authentication**
- Email/password signup and login
- JWT access and refresh tokens
- Session management
- Secure password hashing (bcrypt)

✅ **Security**
- Rate limiting on login attempts
- Account lockout after failed attempts
- Password strength validation
- Audit logging

✅ **Password Management**
- Password change (authenticated)
- Password reset via email token
- Secure token generation

✅ **Two-Factor Authentication**
- TOTP (Time-based One-Time Password)
- QR code generation
- Backup codes

✅ **OAuth Integration** (Ready for implementation)
- Google Sign-In
- Facebook Login
- GitHub OAuth

✅ **Email Verification**
- Email verification tokens
- Verification link generation
- Account activation

## API Endpoints

### Authentication
```
POST   /api/v1/auth/signup              - Create new user account
POST   /api/v1/auth/login               - Login and get tokens
POST   /api/v1/auth/refresh             - Refresh access token
POST   /api/v1/auth/logout              - Logout and revoke tokens
GET    /api/v1/auth/me                  - Get current user
```

### Password Management
```
POST   /api/v1/auth/change-password     - Change password (authenticated)
POST   /api/v1/auth/forgot-password     - Request password reset
POST   /api/v1/auth/reset-password      - Reset password with token
```

### Health
```
GET    /health                          - Health check
GET    /                                - Service info
```

## Database Schema

### Tables
- `users` - User accounts
- `user_roles` - Role assignments (RBAC)
- `refresh_tokens` - JWT refresh tokens
- `sessions` - Active user sessions
- `password_reset_tokens` - Password reset tokens
- `email_verification_tokens` - Email verification tokens
- `oauth_accounts` - OAuth provider accounts
- `login_attempts` - Login attempt history
- `audit_logs` - Security audit logs

## Running Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your configuration

# Run the service
python -m app.main

# Or with uvicorn
uvicorn app.main:app --reload --port 8000
```

Access API docs at: http://localhost:8000/docs

## Running with Docker

```bash
# Build image
docker build -t auth-service .

# Run container
docker run -p 8000:8000 --env-file .env auth-service
```

## Configuration

See `.env.example` for all configuration options.

Key configurations:
- **JWT_SECRET_KEY**: Must be at least 32 characters
- **DATABASE_URL**: PostgreSQL connection string
- **REDIS_URL**: Redis connection for sessions
- **SMTP_***: Email server configuration for password reset

## Security Best Practices

✅ Strong password requirements (min 8 chars, uppercase, lowercase, digit)
✅ Rate limiting on authentication endpoints
✅ Bcrypt password hashing with 12 rounds
✅ JWT tokens with short expiry (30 min access, 30 days refresh)
✅ Secure token generation (secrets.token_urlsafe)
✅ Audit logging for all security events
✅ HTTPS only in production (configure reverse proxy)

## Integration

### From Frontend (JavaScript/TypeScript)

```typescript
// Login
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'Password123'
  })
});

const { access_token, refresh_token, user } = await response.json();

// Store tokens
localStorage.setItem('access_token', access_token);
localStorage.setItem('refresh_token', refresh_token);

// Use access token for authenticated requests
const authResponse = await fetch('http://localhost:8000/api/v1/auth/me', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

### From Other Services (Python)

```python
import httpx

# Verify token
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://auth-service:8000/api/v1/auth/verify",
        json={"token": access_token}
    )

    if response.status_code == 200:
        user_data = response.json()
        user_id = user_data["user"]["user_id"]
```

## Development

### Project Structure

```
app/
├── models.py           # Database models
├── schemas.py          # Pydantic schemas
├── config.py           # Configuration
├── database.py         # Database setup
├── main.py             # FastAPI application
├── routers/
│   └── auth.py         # API endpoints
├── services/
│   └── auth_service.py # Business logic
├── middleware/         # Custom middleware
└── utils/
    └── security.py     # Security utilities
```

## TODO for Production

- [ ] Implement JWT token blacklist (Redis)
- [ ] Add OAuth provider implementations
- [ ] Email service integration
- [ ] Rate limiting middleware
- [ ] API key authentication
- [ ] WebAuthn/FIDO2 support
- [ ] Account recovery options
- [ ] GDPR compliance features

## Testing

```bash
# Run tests (when implemented)
pytest

# With coverage
pytest --cov=app tests/
```

## Version

**v2.0.0** - Part of Version 2.0 platform release
