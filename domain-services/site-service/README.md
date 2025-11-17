# Site Service

Domain service for managing website configurations in the multi-website platform.

## Overview

The Site Service manages:
- **Sites**: Website instances with unique slugs and configurations
- **Templates**: Reusable website templates for different business types
- **Sections**: Dynamic page sections (hero, product grid, testimonials, etc.)

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+ (for caching and events)

### Local Development Setup

1. **Create Python virtual environment:**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your database credentials
nano .env
```

4. **Create database:**

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE site_service_db;
CREATE USER platform_user WITH PASSWORD 'platform_pass';
GRANT ALL PRIVILEGES ON DATABASE site_service_db TO platform_user;
\q
```

5. **Run the service:**

```bash
uvicorn app.main:app --reload --port 8010
```

6. **Seed templates (optional):**

```bash
python seed_templates.py
```

7. **Access the API:**

- **API Docs:** http://localhost:8010/docs
- **Health Check:** http://localhost:8010/health
- **Readiness Check:** http://localhost:8010/ready

## API Endpoints

### Sites

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/v1/sites` | Create new site | Yes |
| GET | `/v1/sites` | List all sites for org | Yes |
| GET | `/v1/sites/{id}` | Get site by ID | Yes |
| PUT | `/v1/sites/{id}` | Update site | Yes |
| PATCH | `/v1/sites/{id}/status` | Update site status | Yes |
| DELETE | `/v1/sites/{id}` | Soft delete site | Yes |
| GET | `/v1/sites/by-slug/{slug}` | Get site by slug | No (Public) |
| GET | `/v1/sites/by-domain/{domain}` | Get site by domain | No (Public) |

### Templates

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/v1/templates` | List templates | No |
| GET | `/v1/templates/{id}` | Get template by ID | No |

### Sections

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/v1/sites/{id}/sections` | Add section to page | Yes |
| GET | `/v1/sites/{id}/pages/{path}` | Get page sections | No (Public) |
| PUT | `/v1/sites/{id}/sections/{id}` | Update section | Yes |
| DELETE | `/v1/sites/{id}/sections/{id}` | Delete section | Yes |
| POST | `/v1/sites/{id}/sections/reorder` | Reorder sections | Yes |

## Example Usage

### 1. Create a Site

```bash
curl -X POST http://localhost:8010/v1/sites \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "rams-grocery",
    "site_type": "departmental_store",
    "meta_title": "Ram'\''s Grocery - Fresh & Quality",
    "primary_color": "#3b82f6",
    "secondary_color": "#10b981"
  }'
```

### 2. Get Site by Slug

```bash
curl http://localhost:8010/v1/sites/by-slug/rams-grocery
```

### 3. List Templates

```bash
curl http://localhost:8010/v1/templates
```

### 4. Publish Site

```bash
curl -X PATCH http://localhost:8010/v1/sites/{site_id}/status \
  -H "Content-Type: application/json" \
  -d '{"status": "published"}'
```

### 5. Add Section to Page

```bash
curl -X POST http://localhost:8010/v1/sites/{site_id}/sections \
  -H "Content-Type: application/json" \
  -d '{
    "page_path": "/",
    "section_type": "hero",
    "section_order": 0,
    "section_config": {
      "title": "Welcome to Our Store",
      "subtitle": "Quality products at great prices",
      "cta_text": "Shop Now",
      "cta_link": "/products"
    }
  }'
```

## Docker

### Build Image

```bash
docker build -t site-service:latest .
```

### Run Container

```bash
docker run -d \
  --name site-service \
  -p 8010:8010 \
  -e DATABASE_URL=postgresql+asyncpg://platform_user:platform_pass@host.docker.internal:5432/site_service_db \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  site-service:latest
```

### Using Docker Compose

See `../../docker-compose.yml` in project root.

## Database Schema

### Sites Table

```sql
CREATE TABLE sites (
  site_id UUID PRIMARY KEY,
  org_id UUID NOT NULL,
  slug VARCHAR(100) UNIQUE NOT NULL,
  domain VARCHAR(255) UNIQUE,
  site_type VARCHAR(50) NOT NULL,
  template_id UUID,
  status VARCHAR(20) DEFAULT 'draft',
  meta_title VARCHAR(200),
  meta_description TEXT,
  favicon_url VARCHAR(500),
  logo_url VARCHAR(500),
  primary_color VARCHAR(7) DEFAULT '#3b82f6',
  secondary_color VARCHAR(7) DEFAULT '#10b981',
  font_family VARCHAR(100) DEFAULT 'Inter, sans-serif',
  config JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);
```

### Templates Table

```sql
CREATE TABLE templates (
  template_id UUID PRIMARY KEY,
  template_name VARCHAR(100) NOT NULL,
  site_type VARCHAR(50) NOT NULL,
  layout_config JSONB NOT NULL,
  style_config JSONB,
  preview_url VARCHAR(500),
  is_premium BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Site Sections Table

```sql
CREATE TABLE site_sections (
  section_id UUID PRIMARY KEY,
  site_id UUID NOT NULL,
  page_path VARCHAR(200) DEFAULT '/',
  section_type VARCHAR(50) NOT NULL,
  section_order INT NOT NULL,
  section_config JSONB NOT NULL,
  is_visible BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP
);
```

## Testing

### Run Tests

```bash
pytest tests/
```

### Manual Testing with Swagger UI

Visit http://localhost:8010/docs to access interactive API documentation.

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SERVICE_NAME` | Service name | site-service |
| `SERVICE_PORT` | Port to run on | 8010 |
| `DEBUG` | Enable debug mode | False |
| `LOG_LEVEL` | Logging level | INFO |
| `DATABASE_URL` | PostgreSQL connection URL | Required |
| `REDIS_URL` | Redis connection URL | redis://localhost:6379/0 |
| `SECRET_KEY` | JWT secret key | Required |
| `CORS_ORIGINS` | Allowed CORS origins | http://localhost:3000 |

## Architecture

### Layers

```
┌─────────────────────────────────────┐
│         API Layer (FastAPI)         │
│  - Routers (sites, templates)       │
│  - Request/Response validation      │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│      Service Layer (Business)       │
│  - SiteService                      │
│  - Business logic and validation    │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│       Data Layer (SQLAlchemy)       │
│  - Models (Site, Template, Section) │
│  - Database operations              │
└─────────────────────────────────────┘
```

### Key Design Patterns

- **Repository Pattern**: Service layer abstracts database operations
- **Dependency Injection**: FastAPI's `Depends()` for clean dependencies
- **Async/Await**: Full async support for database and HTTP operations
- **Validation**: Pydantic schemas for request/response validation
- **Multi-Tenancy**: Org-level data isolation

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
pg_isready

# Test connection
psql -U platform_user -d site_service_db -h localhost
```

### Port Already in Use

```bash
# Find process using port 8010
lsof -i :8010

# Kill process
kill -9 <PID>
```

### Import Errors

```bash
# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

## Development Workflow

1. **Create feature branch**
2. **Make changes**
3. **Test locally**
4. **Run tests**: `pytest`
5. **Commit**: `git commit -m "feat: description"`
6. **Push**: `git push`

## Contributing

Follow the guidelines in `../../ARCHITECTURE.md` and `../../docs/IMPLEMENTATION_GUIDE.md`.

## License

Copyright © 2025. All rights reserved.
