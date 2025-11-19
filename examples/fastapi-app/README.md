# FastAPI Example App

Complete production-ready FastAPI application demonstrating all AI features.

## Features

- ✅ All three AI features integrated
- ✅ Interactive Swagger UI documentation
- ✅ Error handling and logging
- ✅ Rate limiting (optional)
- ✅ CORS support
- ✅ Health checks
- ✅ Beautiful landing page

## Quick Start

### 1. Install Dependencies

```bash
cd examples/fastapi-app
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export OPENAI_API_KEY="sk-..."
export ENABLE_CACHE="true"
export ENABLE_TRACKING="false"
```

### 3. Run the Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload
```

### 4. Visit the App

- **Landing Page**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Product Description

```bash
curl -X POST "http://localhost:8000/api/product/description" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Organic Quinoa",
    "category": "grocery",
    "features": ["Organic", "High protein", "Gluten-free"],
    "tone": "professional",
    "length": "medium"
  }'
```

### Review Response

```bash
curl -X POST "http://localhost:8000/api/review/respond" \
  -H "Content-Type: application/json" \
  -d '{
    "review_text": "Amazing service!",
    "rating": 5,
    "business_name": "My Business"
  }'
```

### Social Calendar

```bash
curl -X POST "http://localhost:8000/api/social/calendar" \
  -H "Content-Type: application/json" \
  -d '{
    "month": "2025-02",
    "business_type": "coffee shop",
    "brand_voice": "cozy and welcoming",
    "posts_per_week": 5
  }'
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key (required) |
| `ENABLE_CACHE` | `true` | Enable Redis caching |
| `ENABLE_TRACKING` | `true` | Enable token tracking |
| `ENABLE_RATE_LIMIT` | `false` | Enable rate limiting |
| `RATE_LIMIT_REQUESTS` | `100` | Max requests per window |
| `RATE_LIMIT_WINDOW` | `3600` | Rate limit window (seconds) |
| `REDIS_URL` | - | Redis connection URL |
| `DATABASE_URL` | - | PostgreSQL connection URL |

## Docker

### Build and Run

```bash
docker build -t ai-api .
docker run -p 8000:8000 -e OPENAI_API_KEY=sk-... ai-api
```

### Docker Compose

```bash
docker-compose up
```

## Testing

```python
import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        # Test health
        response = await client.get("http://localhost:8000/health")
        print(response.json())

        # Test product description
        response = await client.post(
            "http://localhost:8000/api/product/description",
            json={
                "product_name": "Test Product",
                "category": "grocery",
                "features": ["Feature 1"],
                "tone": "professional",
                "length": "medium"
            }
        )
        print(response.json())

asyncio.run(test())
```

## Production Deployment

### Gunicorn

```bash
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### systemd Service

```ini
[Unit]
Description=AI API Service
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/ai-api
Environment="OPENAI_API_KEY=sk-..."
ExecStart=/usr/local/bin/gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

## License

Part of the Beautiful Websites AI Platform.
