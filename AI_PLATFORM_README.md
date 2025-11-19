# Modular AI Platform for Beautiful Websites 🚀

A production-ready, framework-agnostic AI platform with three powerful microsaas features: Product Description Generator, Review Response Generator, and Social Media Calendar Generator.

## 🌟 Features

### 1. Product Description Generator 📝
- **SEO-optimized** product descriptions
- **Category-specific prompts** (grocery, electronics, fashion)
- **Multiple tones** (professional, casual, luxury, technical, friendly)
- **Configurable length** (short, medium, long)
- Automatic meta tags and keyword generation

### 2. Review Response Generator 💬
- **Sentiment-aware** responses (positive, neutral, negative)
- **Tone-matched** templates for each sentiment level
- **Platform-specific** variations (Google, Yelp, Facebook)
- Automatic keyword extraction
- Personalization with reviewer names

### 3. Social Media Calendar Generator 📱
- **30-day content calendars** with strategic planning
- **Content mix strategy** (40% promo, 30% edu, 20% engage, 10% testimonial)
- **Multi-platform support** (Instagram, Facebook, Twitter, LinkedIn)
- **Optimal posting times** throughout the day
- AI-generated hashtags and image prompts

## 📦 Architecture

The platform uses **clean architecture** principles with extreme modularity:

```
packages/
├── ai-core/                    # Framework-agnostic core
│   ├── domain/                 # Business logic & interfaces
│   ├── application/            # AIEngine orchestrator
│   ├── infrastructure/         # Cache & storage implementations
│   └── di/                     # Dependency injection
│
├── ai-providers/               # AI provider implementations
│   ├── openai/                 # OpenAI GPT integration
│   ├── anthropic/              # Claude integration
│   └── mock/                   # Mock provider for testing
│
├── ai-storage/                 # Storage implementations
│   ├── redis/                  # Redis caching
│   └── postgres/               # PostgreSQL token tracking
│
├── ai-features/                # Feature plugins
│   ├── product-description/    # Product description generator
│   ├── review-response/        # Review response generator
│   └── social-calendar/        # Social media calendar
│
└── ai-fastapi/                 # FastAPI integration (optional)
    ├── routers/                # Pre-built API routers
    ├── models.py               # Pydantic request/response models
    ├── middleware.py           # Error handling, logging, rate limiting
    └── dependencies.py         # DI for FastAPI

examples/
├── fastapi-app/                # Complete FastAPI application
├── flask-app/                  # Flask integration example
└── standalone/                 # Standalone Python scripts

tests/
├── test_product_description.py # Unit tests for product plugin
├── test_review_response.py     # Unit tests for review plugin
└── test_social_calendar.py     # Unit tests for calendar plugin
```

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/beautifulwebsites.git
cd beautifulwebsites

# Install core packages
pip install -e packages/ai-core
pip install -e packages/ai-providers/openai
pip install -e packages/ai-fastapi  # Optional: for FastAPI integration

# Set API key
export OPENAI_API_KEY="sk-..."
```

### Standalone Usage

```python
import asyncio
from ai_core.application.AIEngine import AIEngineBuilder
from ai_providers.openai.OpenAIProvider import OpenAIProvider
from ai_features.product_description.plugin import ProductDescriptionPlugin

async def main():
    # Setup AI engine
    provider = OpenAIProvider(api_key="sk-...")
    builder = AIEngineBuilder()
    builder.with_provider(provider)
    engine = builder.build()

    # Use plugin
    plugin = ProductDescriptionPlugin(ai_engine=engine)
    result = await plugin.generate_description(
        product_data={
            "name": "Organic Quinoa",
            "features": "Organic, High protein, Gluten-free"
        },
        category="grocery",
        tone="professional"
    )

    print(result["description"])

asyncio.run(main())
```

### FastAPI Integration

```python
from fastapi import FastAPI
from ai_fastapi import (
    product_description_router,
    review_response_router,
    social_calendar_router,
    add_ai_middleware
)
from ai_fastapi.dependencies import configure_ai_platform

app = FastAPI()

# Configure on startup
@app.on_event("startup")
async def startup():
    configure_ai_platform(
        provider_type="openai",
        enable_cache=True,
        enable_tracking=True
    )

# Add middleware and routers
app = add_ai_middleware(app)
app.include_router(product_description_router)
app.include_router(review_response_router)
app.include_router(social_calendar_router)

# Run: uvicorn main:app --reload
```

Visit http://localhost:8000/docs for interactive API documentation!

### Flask Integration

```python
from flask import Flask, request, jsonify
import asyncio
from ai_core.application.AIEngine import AIEngineBuilder
from ai_providers.openai.OpenAIProvider import OpenAIProvider
from ai_features.product_description.plugin import ProductDescriptionPlugin

app = Flask(__name__)

# Initialize
provider = OpenAIProvider(api_key="sk-...")
engine = AIEngineBuilder().with_provider(provider).build()
plugin = ProductDescriptionPlugin(ai_engine=engine)

@app.route('/api/product/description', methods=['POST'])
def generate():
    data = request.json
    result = asyncio.run(plugin.generate_description(
        product_data=data['product_data'],
        category=data.get('category')
    ))
    return jsonify(result)

app.run()
```

## 📚 Documentation

### Core Documentation
- [Modular Architecture](docs/MODULAR_AI_ARCHITECTURE.md) - Complete architecture design
- [Integration Guide](docs/MODULAR_INTEGRATION_GUIDE.md) - Integration patterns
- [Implementation Progress](docs/AI_IMPLEMENTATION_PROGRESS.md) - Development roadmap

### Package Documentation
- [AI Core](packages/ai-core/README.md) - Core engine and interfaces
- [OpenAI Provider](packages/ai-providers/openai/README.md) - GPT integration
- [Claude Provider](packages/ai-providers/anthropic/README.md) - Claude integration
- [FastAPI Integration](packages/ai-fastapi/README.md) - FastAPI helpers

### Plugin Documentation
- [Product Description Plugin](packages/ai-features/product-description/README.md)
- [Review Response Plugin](packages/ai-features/review-response/README.md)
- [Social Calendar Plugin](packages/ai-features/social-calendar/README.md)

### Examples
- [FastAPI Example](examples/fastapi-app/README.md) - Complete FastAPI app
- [Flask Example](examples/flask-app/README.md) - Flask integration
- [Standalone Examples](examples/standalone/) - Python scripts

## 🧪 Testing

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=packages --cov-report=html

# Run specific test file
pytest tests/test_product_description.py

# Run with mock provider (no API key needed)
pytest -v
```

All tests use the **MockProvider** for testing without API calls!

## 🔧 Configuration

### Environment Variables

```bash
# AI Provider (choose one)
OPENAI_API_KEY=sk-...              # For OpenAI GPT
ANTHROPIC_API_KEY=sk-...           # For Claude

# Optional: Caching
REDIS_URL=redis://localhost:6379   # For production caching
ENABLE_CACHE=true                  # Enable/disable cache

# Optional: Token Tracking
DATABASE_URL=postgresql://...       # For usage tracking
ENABLE_TRACKING=true               # Enable/disable tracking

# Optional: Rate Limiting
ENABLE_RATE_LIMIT=true
RATE_LIMIT_REQUESTS=100            # Requests per window
RATE_LIMIT_WINDOW=3600             # Window in seconds
```

### Provider Configuration

```python
# OpenAI
from ai_providers.openai import OpenAIProvider
provider = OpenAIProvider(api_key="sk-...")

# Claude
from ai_providers.anthropic import ClaudeProvider
provider = ClaudeProvider(api_key="sk-...")

# Mock (for testing)
from ai_providers.mock import MockProvider
provider = MockProvider()
```

### Advanced Configuration

```python
from ai_core.application.AIEngine import AIEngineBuilder
from ai_storage.redis import RedisCache
from ai_storage.postgres import PostgresTokenTracker

# Build engine with all features
builder = AIEngineBuilder()
builder.with_provider(provider)
builder.with_cache(RedisCache(redis_url="redis://localhost"))
builder.with_token_tracker(PostgresTokenTracker(database_url="postgresql://..."))
builder.with_cache_enabled(True)
builder.with_cache_ttl(3600)

engine = builder.build()
```

## 💰 Cost Optimization

### Estimated Costs (GPT-4)

| Feature | Avg Tokens | Cost per Request |
|---------|------------|------------------|
| Product Description | 400-600 | ~$0.01 |
| Review Response | 250-400 | ~$0.006 |
| Social Calendar (30 posts) | 2500-3500 | ~$0.10 |
| Single Post | 350-500 | ~$0.01 |

### Cost-Saving Tips

1. **Enable Caching**: 30-50% cost reduction
```python
builder.with_cache_enabled(True)
```

2. **Use GPT-3.5 for Drafts**:
```python
result = await plugin.generate_description(..., model="gpt-3.5-turbo")
```

3. **Batch Requests**: Generate multiple items in one request

4. **Track Usage**: Monitor with PostgreSQL tracker
```python
builder.with_token_tracker(PostgresTokenTracker(...))
```

## 🏗️ Production Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:password@postgres/ai
    depends_on:
      - redis
      - postgres

  redis:
    image: redis:7-alpine

  postgres:
    image: postgres:15-alpine
```

### Kubernetes

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: ai-api:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-secrets
              key: openai-key
```

## 📊 Performance

### With Caching Enabled

- **30-50% cost reduction** on repeated requests
- **3-5x faster** response times for cached content
- Automatic cache invalidation

### Scalability

- **Stateless design** - easy horizontal scaling
- **Provider-agnostic** - switch AI providers instantly
- **Framework-agnostic** - use with any Python web framework

## 🤝 Contributing

Contributions are welcome! Please see our contributing guidelines.

## 📄 License

Part of the Beautiful Websites platform.

## 🆘 Support

- **Documentation**: See docs/ directory
- **Examples**: See examples/ directory
- **Tests**: See tests/ directory
- **Issues**: https://github.com/yourusername/beautifulwebsites/issues

## 🎯 Use Cases

### E-commerce Platforms
- Generate product descriptions at scale
- Respond to customer reviews automatically
- Maintain social media presence

### Website Builders
- Offer AI features to your users
- White-label AI capabilities
- Monetize through AI-powered tools

### Digital Agencies
- Speed up content creation
- Automate client communications
- Scale social media management

### SaaS Applications
- Add AI features to existing products
- Create AI-powered microsaas
- Enhance user experience with AI

## ✨ Why This Platform?

✅ **Modular** - Use what you need, when you need it
✅ **Framework-Agnostic** - Works with FastAPI, Flask, Django, or standalone
✅ **Provider-Agnostic** - Easy switching between OpenAI, Claude, or custom providers
✅ **Production-Ready** - Error handling, logging, rate limiting built-in
✅ **Cost-Optimized** - Built-in caching and usage tracking
✅ **Well-Tested** - Comprehensive test suite with mock provider
✅ **Documented** - Extensive documentation and examples

## 🚀 What's Next?

- [ ] Add more AI providers (Google PaLM, local models)
- [ ] Add more features (Email writer, Blog post generator)
- [ ] Add admin dashboard for analytics
- [ ] Add webhook support for async operations
- [ ] Add multi-language support

---

Built with ❤️ for the Beautiful Websites platform
