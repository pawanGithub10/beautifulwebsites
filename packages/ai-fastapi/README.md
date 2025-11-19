# FastAPI Integration for AI Platform 🚀

Ready-to-use FastAPI routers, Pydantic models, and middleware for integrating AI features into FastAPI applications.

## Features

- **Pre-built Routers**: Plug-and-play routers for all AI features
- **Pydantic Models**: Request/response validation with OpenAPI schemas
- **Error Handling**: Consistent error responses across all endpoints
- **Rate Limiting**: Built-in rate limiting middleware
- **Logging**: Request/response logging for monitoring
- **Dependency Injection**: Clean DI pattern for AI components
- **Auto Documentation**: Interactive Swagger UI out of the box

## Quick Start

### Installation

```bash
pip install fastapi uvicorn ai-platform-core ai-platform-openai
```

### Basic Setup

```python
from fastapi import FastAPI
from ai_fastapi import (
    product_description_router,
    review_response_router,
    social_calendar_router,
    add_ai_middleware
)
from ai_fastapi.dependencies import configure_ai_platform

# Create FastAPI app
app = FastAPI(
    title="AI Platform API",
    description="AI-powered features for Beautiful Websites",
    version="1.0.0"
)

# Configure AI platform at startup
@app.on_event("startup")
async def startup():
    configure_ai_platform(
        provider_type="openai",
        enable_cache=True,
        enable_tracking=True
    )

# Add AI middleware
app = add_ai_middleware(
    app,
    enable_error_handler=True,
    enable_logging=True,
    enable_rate_limit=True
)

# Include routers
app.include_router(product_description_router)
app.include_router(review_response_router)
app.include_router(social_calendar_router)

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Run with: uvicorn main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation!

## Configuration

### Environment Variables

```bash
# AI Provider
OPENAI_API_KEY=sk-...              # Required for OpenAI
ANTHROPIC_API_KEY=sk-...           # Required for Claude

# Caching (optional)
REDIS_URL=redis://localhost:6379   # For production caching

# Token Tracking (optional)
DATABASE_URL=postgresql://...       # For usage tracking and quotas
```

### Advanced Configuration

```python
from ai_fastapi.dependencies import configure_ai_platform

@app.on_event("startup")
async def startup():
    configure_ai_platform(
        provider_type="openai",           # or "claude"
        api_key="sk-...",                 # or use env var
        enable_cache=True,                # Enable Redis caching
        enable_tracking=True,             # Enable PostgreSQL tracking
        redis_url="redis://localhost:6379",
        postgres_url="postgresql://user:pass@localhost/db"
    )
```

## API Endpoints

### Product Description

Generate AI-powered product descriptions with SEO optimization.

**Endpoint:** `POST /api/product/description`

```python
import httpx

response = httpx.post("http://localhost:8000/api/product/description", json={
    "product_name": "Organic Quinoa",
    "category": "grocery",
    "features": ["Organic certified", "High protein", "Gluten-free"],
    "price": "$8.99",
    "target_audience": "Health-conscious shoppers",
    "tone": "professional",
    "length": "medium"
})

result = response.json()
print(result["description"])
print(result["meta_title"])
print(result["tags"])
```

**Response:**

```json
{
    "product_name": "Organic Quinoa",
    "description": "Discover the ancient superfood...",
    "short_description": "Premium organic quinoa...",
    "meta_title": "Organic Quinoa - High Protein Superfood",
    "meta_description": "Premium organic quinoa...",
    "tags": ["organic", "quinoa", "superfood"],
    "category": "grocery",
    "tone": "professional",
    "length": "medium",
    "tokens_used": 450,
    "model": "gpt-4",
    "generated_at": "2025-01-19T12:00:00Z"
}
```

**Additional Endpoints:**
- `GET /api/product/categories` - Get available categories
- `GET /api/product/examples` - Get example descriptions

### Review Response

Generate sentiment-aware responses to customer reviews.

**Endpoint:** `POST /api/review/respond`

```python
response = httpx.post("http://localhost:8000/api/review/respond", json={
    "review_text": "Amazing service! Professional team and great results.",
    "rating": 5,
    "reviewer_name": "Sarah",
    "business_name": "Bella Beauty Salon",
    "business_type": "beauty salon",
    "platform": "google"
})

result = response.json()
print(result["response_text"])
print(f"Sentiment: {result['sentiment']} ({result['sentiment_score']})")
```

**Response:**

```json
{
    "response_text": "Thank you so much for your wonderful review, Sarah!...",
    "sentiment": "positive",
    "sentiment_score": 0.95,
    "keywords": ["amazing", "professional", "great"],
    "platform_variations": {
        "google": "Thank you so much...",
        "yelp": "We appreciate..."
    },
    "review_rating": 5,
    "tokens_used": 320,
    "model": "gpt-4",
    "generated_at": "2025-01-19T12:00:00Z"
}
```

**Additional Endpoints:**
- `POST /api/review/analyze` - Analyze sentiment only
- `GET /api/review/examples` - Get example responses
- `GET /api/review/best-practices` - Get review response tips

### Social Media Calendar

Generate 30-day social media content calendars.

**Endpoint:** `POST /api/social/calendar`

```python
response = httpx.post("http://localhost:8000/api/social/calendar", json={
    "month": "2025-02",
    "business_type": "coffee shop",
    "brand_voice": "cozy and welcoming",
    "target_audience": "coffee lovers and remote workers",
    "posts_per_week": 5,
    "themes": ["Valentine's specials", "new roasts"],
    "products_to_feature": [
        {"name": "Valentine's Latte", "price": "$5.50"}
    ]
})

result = response.json()
print(f"Generated {result['total_posts']} posts")
for post in result['posts'][:3]:
    print(f"{post['date']} {post['time']}: {post['post_text']}")
```

**Response:**

```json
{
    "calendar_id": "cal_2025-02_20250119120000",
    "month": "2025-02",
    "business_type": "coffee shop",
    "total_posts": 20,
    "posts": [
        {
            "date": "2025-02-01",
            "time": "09:00",
            "post_text": "Start your weekend with our new Valentine's Latte ❤️☕",
            "hashtags": ["#CoffeeLovers", "#ValentinesDay"],
            "image_prompt": "Beautiful heart-shaped latte art",
            "category": "promotional"
        }
    ],
    "content_mix": {
        "promotional": 8,
        "educational": 6,
        "engagement": 4,
        "testimonial": 2
    },
    "tokens_used": 2850,
    "model": "gpt-4",
    "generated_at": "2025-01-19T12:00:00Z"
}
```

**Single Post Generation:**

```python
response = httpx.post("http://localhost:8000/api/social/post", json={
    "topic": "New organic coffee bean launch",
    "business_type": "coffee shop",
    "brand_voice": "artisanal and passionate",
    "post_type": "promotional",
    "platforms": ["instagram", "facebook"]
})
```

**Additional Endpoints:**
- `POST /api/social/post` - Generate single post
- `GET /api/social/content-mix` - Get recommended content distribution
- `GET /api/social/platform-specs` - Get platform specifications
- `GET /api/social/examples` - Get example calendars

## Middleware

### Error Handler

Consistent error responses across all AI endpoints.

```python
from ai_fastapi.middleware import AIErrorHandler

app.add_middleware(AIErrorHandler)
```

**Error Response Format:**

```json
{
    "error": "Validation Error",
    "detail": "Product name is required",
    "status_code": 400
}
```

### Request Logging

Log all AI requests with performance metrics.

```python
from ai_fastapi.middleware import RequestLoggingMiddleware

app.add_middleware(RequestLoggingMiddleware)
```

Logs include:
- Request method and path
- Response status code
- Processing time
- Client IP address

### Rate Limiting

Prevent API abuse with rate limiting.

```python
from ai_fastapi.middleware import RateLimitMiddleware

app.add_middleware(
    RateLimitMiddleware,
    max_requests=100,      # 100 requests
    window_seconds=3600    # per hour
)
```

Response headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Timestamp when limit resets

### All Middleware at Once

```python
from ai_fastapi.middleware import add_ai_middleware

app = add_ai_middleware(
    app,
    enable_error_handler=True,
    enable_logging=True,
    enable_rate_limit=True,
    rate_limit_requests=100,
    rate_limit_window=3600
)
```

## Dependency Injection

### Using Dependencies

```python
from fastapi import Depends
from ai_fastapi.dependencies import (
    get_ai_engine,
    get_product_plugin,
    get_review_plugin,
    get_calendar_plugin
)
from ai_core.application.AIEngine import AIEngine

@app.get("/custom-endpoint")
async def custom_endpoint(
    engine: AIEngine = Depends(get_ai_engine)
):
    # Use AI engine directly
    healthy = await engine.provider.check_health()
    return {"healthy": healthy}
```

### Custom Dependencies

```python
from ai_fastapi.dependencies import get_site_id_from_token

@app.post("/product/description")
async def generate(
    request: ProductDescriptionRequest,
    site_id: str = Depends(get_site_id_from_token)
):
    # site_id extracted from auth token
    request.site_id = site_id
    # ... rest of logic
```

## Pydantic Models

All request/response models are fully typed with Pydantic.

### Product Description Models

```python
from ai_fastapi.models import (
    ProductDescriptionRequest,
    ProductDescriptionResponse,
    ToneType,
    LengthType
)

# Request with validation
request = ProductDescriptionRequest(
    product_name="Organic Quinoa",
    category="grocery",
    features=["Organic", "High protein"],
    tone=ToneType.PROFESSIONAL,
    length=LengthType.MEDIUM
)
```

### Review Response Models

```python
from ai_fastapi.models import (
    ReviewResponseRequest,
    ReviewResponseResponse
)

request = ReviewResponseRequest(
    review_text="Great service!",
    rating=5,
    business_name="My Business"
)
```

### Social Calendar Models

```python
from ai_fastapi.models import (
    SocialCalendarRequest,
    SinglePostRequest,
    PostType,
    SocialPlatform
)

request = SocialCalendarRequest(
    month="2025-02",
    business_type="restaurant",
    brand_voice="warm and inviting",
    posts_per_week=5
)
```

## Complete Example App

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ai_fastapi import (
    product_description_router,
    review_response_router,
    social_calendar_router,
    add_ai_middleware
)
from ai_fastapi.dependencies import configure_ai_platform, get_ai_engine
from ai_fastapi.models import HealthResponse
from ai_core.application.AIEngine import AIEngine
from datetime import datetime

# Create app
app = FastAPI(
    title="Beautiful Websites AI API",
    description="AI-powered features for website generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Configure AI on startup
@app.on_event("startup")
async def startup():
    print("🚀 Starting AI Platform...")
    configure_ai_platform(
        provider_type="openai",
        enable_cache=True,
        enable_tracking=True
    )
    print("✅ AI Platform ready!")

# Add AI middleware
app = add_ai_middleware(
    app,
    enable_error_handler=True,
    enable_logging=True,
    enable_rate_limit=True,
    rate_limit_requests=100
)

# Include routers
app.include_router(product_description_router)
app.include_router(review_response_router)
app.include_router(social_calendar_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "Beautiful Websites AI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Health check
@app.get("/health", response_model=HealthResponse)
async def health(engine: AIEngine = Depends(get_ai_engine)):
    try:
        provider_healthy = await engine.provider.check_health()
        provider_name = engine.provider.__class__.__name__

        return HealthResponse(
            status="healthy" if provider_healthy else "degraded",
            ai_provider=provider_name,
            provider_healthy=provider_healthy,
            cache_enabled=engine.enable_cache,
            tracking_enabled=engine.token_tracker is not None,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

# Run app
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
```

Save as `main.py` and run:

```bash
uvicorn main:app --reload
```

Visit:
- http://localhost:8000 - Root endpoint
- http://localhost:8000/docs - Interactive API documentation
- http://localhost:8000/health - Health check

## Testing

### Manual Testing with HTTPie

```bash
# Product Description
http POST localhost:8000/api/product/description \
    product_name="Organic Quinoa" \
    category="grocery" \
    features:='["Organic", "High protein"]' \
    tone="professional"

# Review Response
http POST localhost:8000/api/review/respond \
    review_text="Great service!" \
    rating:=5 \
    business_name="My Business"

# Social Calendar
http POST localhost:8000/api/social/calendar \
    month="2025-02" \
    business_type="restaurant" \
    brand_voice="warm" \
    posts_per_week:=5
```

### Testing with Python

```python
import httpx
import asyncio

async def test_api():
    async with httpx.AsyncClient() as client:
        # Test product description
        response = await client.post(
            "http://localhost:8000/api/product/description",
            json={
                "product_name": "Test Product",
                "category": "grocery",
                "features": ["Feature 1", "Feature 2"],
                "tone": "professional",
                "length": "medium"
            }
        )
        print(response.json())

asyncio.run(test_api())
```

## Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/ai_platform
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=ai_platform
    ports:
      - "5432:5432"
```

### Environment Configuration

```bash
# .env file
OPENAI_API_KEY=sk-...
REDIS_URL=redis://redis:6379
DATABASE_URL=postgresql://postgres:password@postgres:5432/ai_platform
LOG_LEVEL=INFO
ENABLE_CACHE=true
ENABLE_TRACKING=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
```

## Performance

### Caching

With Redis caching enabled:
- **30-50% cost reduction** on repeated requests
- **3-5x faster** response times for cached content
- Automatic cache invalidation

### Rate Limiting

Default limits:
- **100 requests per hour** per IP
- Configurable window and limits
- Graceful error responses

### Token Usage

Average token usage:
- **Product Description**: 400-600 tokens (~$0.01)
- **Review Response**: 250-400 tokens (~$0.006)
- **Social Calendar (30 posts)**: 2500-3500 tokens (~$0.10)
- **Single Post**: 350-500 tokens (~$0.01)

## Troubleshooting

**Issue: "AI Platform not configured" error**

- Solution: Call `configure_ai_platform()` in startup event handler

**Issue: Rate limit exceeded**

- Solution: Increase `rate_limit_requests` or implement per-user quotas

**Issue: Slow responses**

- Solution: Enable Redis caching with `enable_cache=True`

**Issue: High token costs**

- Solution: Use GPT-3.5 Turbo for drafts, enable caching

## Architecture

The FastAPI integration follows clean architecture principles:

```
ai-fastapi/
├── routers/           # FastAPI route handlers
│   ├── product_description.py
│   ├── review_response.py
│   └── social_calendar.py
├── models.py          # Pydantic request/response models
├── dependencies.py    # Dependency injection
├── middleware.py      # Error handling, logging, rate limiting
└── __init__.py        # Package exports
```

## License

Part of the Beautiful Websites AI Platform.

## Support

For issues or questions, see the main platform documentation.
