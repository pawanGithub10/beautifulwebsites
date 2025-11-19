# Modular AI Integration Guide

**How to add AI capabilities to ANY service in minutes**

## 🎯 Overview

The modular AI architecture allows you to add AI capabilities to any service with minimal code. Just install the package, configure the provider, and start generating!

## 📦 Package Structure

```
packages/
├── ai-core/                    ← Core engine (install this!)
│   ├── domain/                 ← Pure business logic
│   ├── application/            ← AIEngine
│   ├── infrastructure/         ← Simple implementations
│   └── di/                     ← Dependency injection
│
├── ai-providers/ (future)      ← Provider implementations
│   ├── openai/
│   ├── anthropic/
│   └── local/
│
├── ai-features/ (future)       ← Feature plugins
│   ├── product-description/
│   ├── review-response/
│   └── social-calendar/
│
└── ai-integrations/ (future)   ← Framework helpers
    ├── fastapi/
    ├── flask/
    └── django/
```

## 🚀 Integration Patterns

### Pattern 1: Add to Existing FastAPI Service

```python
# domain-services/storefront-service/app/ai.py

from ai_core import AIEngine, container
# from ai_providers.openai import OpenAIProvider  # Future
# from ai_storage.redis import RedisCache  # Future

# Initialize once at startup
def init_ai():
    # provider = OpenAIProvider(api_key="sk-...")
    # cache = RedisCache(url="redis://localhost")
    #
    # container.register_provider(provider)
    # container.register_cache(cache)
    pass

# Use in routes
def get_ai_engine() -> AIEngine:
    return container.get_engine()
```

```python
# domain-services/storefront-service/app/routers/products.py

from fastapi import APIRouter, Depends
from app.ai import get_ai_engine
from ai_core import AIEngine, AIRequest

router = APIRouter()

@router.post("/api/v1/catalog/{site_id}/products/{product_id}/ai-description")
async def generate_description(
    site_id: str,
    product_id: str,
    product_data: dict,
    engine: AIEngine = Depends(get_ai_engine)
):
    # Build prompt
    prompt = f"""Generate a product description for:
    Name: {product_data['name']}
    Category: {product_data['category']}
    Price: {product_data['price']}
    """

    # Generate
    request = AIRequest(
        prompt=prompt,
        model="gpt-4",
        temperature=0.7,
        response_format="json"
    )

    response = await engine.generate(request)

    return {"description": response.content}
```

### Pattern 2: Add to NEW Service

```python
# domain-services/review-service/main.py

from fastapi import FastAPI
from ai_core import container, InMemoryCache
# from ai_providers.openai import OpenAIProvider

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Setup AI
    # provider = OpenAIProvider(api_key="sk-...")
    # container.register_provider(provider)
    container.register_cache(InMemoryCache())

@app.post("/api/v1/{site_id}/reviews/{review_id}/generate-response")
async def generate_response(site_id: str, review_id: str, review_text: str):
    from ai_core import AIRequest

    engine = container.get_engine()

    prompt = f"Generate a professional response to this review: {review_text}"
    request = AIRequest(prompt=prompt)

    response = await engine.generate(request)

    return {"response": response.content}
```

### Pattern 3: Standalone Script

```python
# scripts/bulk-generate-descriptions.py

import asyncio
from ai_core import AIEngine, AIRequest
# from ai_providers.openai import OpenAIProvider

async def main():
    # Setup
    # provider = OpenAIProvider(api_key="sk-...")
    # engine = AIEngine(provider=provider)

    # Read products from database
    products = get_products_from_db()

    for product in products:
        request = AIRequest(
            prompt=f"Generate description for {product['name']}"
        )

        # response = await engine.generate(request)

        # Update database
        # update_product_description(product['id'], response.content)

        print(f"Generated description for {product['name']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Pattern 4: As a Microservice

```python
# services/ai-gateway-service/main.py

from fastapi import FastAPI
from ai_core import container, AIEngine, AIRequest
# from ai_providers.openai import OpenAIProvider
# from ai_storage.redis import RedisCache
# from ai_storage.postgres import PostgresTokenTracker

app = FastAPI(title="AI Gateway Service")

@app.on_event("startup")
async def startup():
    # Setup with all features
    # provider = OpenAIProvider(api_key="sk-...")
    # cache = RedisCache(url="redis://localhost")
    # tracker = PostgresTokenTracker(db_url="postgresql://...")
    #
    # container.register_provider(provider)
    # container.register_cache(cache)
    # container.register_token_tracker(tracker)
    pass

@app.post("/api/v1/completions")
async def generate_completion(request: dict):
    engine = container.get_engine()

    ai_request = AIRequest(
        prompt=request["prompt"],
        temperature=request.get("temperature", 0.7),
        model=request.get("model", "gpt-4")
    )

    response = await engine.generate(ai_request)

    return response.to_dict()

@app.get("/api/v1/health")
async def health():
    engine = container.get_engine()
    return await engine.health_check()
```

## 🔌 Layer-by-Layer Integration

### Layer 1: Core Engine Only

**Minimal setup - just AI generation**

```python
from ai_core import AIEngine, AIRequest
# from ai_providers.openai import OpenAIProvider

# provider = OpenAIProvider(api_key="sk-...")
# engine = AIEngine(provider=provider)

# request = AIRequest(prompt="Hello!")
# response = await engine.generate(request)
```

**Use Case:** Quick prototypes, scripts, testing

### Layer 2: Add Caching

**Reduce costs by 30-50%**

```python
from ai_core import AIEngine, InMemoryCache
# from ai_providers.openai import OpenAIProvider

# provider = OpenAIProvider(api_key="sk-...")
# cache = InMemoryCache()

# engine = AIEngine(provider=provider, cache=cache)

# First call hits API
# response1 = await engine.generate(request)

# Second call uses cache (free!)
# response2 = await engine.generate(request)
```

**Use Case:** Development, low-traffic apps

### Layer 3: Add Redis Cache

**Production caching across multiple instances**

```python
from ai_core import AIEngine
# from ai_providers.openai import OpenAIProvider
# from ai_storage.redis import RedisCache

# provider = OpenAIProvider(api_key="sk-...")
# cache = RedisCache(url="redis://localhost:6379")

# engine = AIEngine(provider=provider, cache=cache)
```

**Use Case:** Production apps with multiple instances

### Layer 4: Add Token Tracking

**Monitor usage and costs**

```python
from ai_core import AIEngine, PromptContext
# from ai_providers.openai import OpenAIProvider
# from ai_storage.redis import RedisCache
# from ai_storage.postgres import PostgresTokenTracker

# provider = OpenAIProvider(api_key="sk-...")
# cache = RedisCache(url="redis://localhost")
# tracker = PostgresTokenTracker(db_url="postgresql://...")

# engine = AIEngine(
#     provider=provider,
#     cache=cache,
#     token_tracker=tracker
# )

# context = PromptContext(
#     variables={},
#     site_id="site-123",
#     feature="product_description"
# )

# response = await engine.generate(request, context)

# Usage automatically tracked in database!
```

**Use Case:** SaaS platforms with billing, multi-tenant apps

### Layer 5: Full Production Stack

**Everything enabled**

```python
from ai_core import container, AIEngine
# from ai_providers.openai import OpenAIProvider
# from ai_providers.anthropic import ClaudeProvider
# from ai_storage.redis import RedisCache
# from ai_storage.postgres import PostgresTokenTracker

# Setup (once at startup)
# container.register_provider(OpenAIProvider(api_key="..."))
# container.register_cache(RedisCache(url="..."))
# container.register_token_tracker(PostgresTokenTracker(db_url="..."))

# Use anywhere
# engine = container.get_engine()

# Monitor health
# health = await engine.health_check()

# Check quotas
# quota = await engine.check_quota(site_id="site-123")

# Get usage stats
# stats = await engine.get_usage_stats(site_id="site-123", period="month")
```

**Use Case:** Production SaaS platforms

## 🎨 Feature Plugins (Future)

Once feature plugins are built, integration is even simpler:

```python
from ai_core import container
from ai_features.product_description import ProductDescriptionPlugin

# Get engine
engine = container.get_engine()

# Initialize feature plugin
plugin = ProductDescriptionPlugin(ai_engine=engine)

# Use plugin
result = await plugin.generate_description(
    product_data={
        "name": "Organic Green Tea",
        "category": "Beverages",
        "price": 299
    }
)

# Returns structured data
# {
#     "description": "Full description...",
#     "short_description": "Summary...",
#     "meta_title": "SEO title",
#     "tags": ["organic", "tea"]
# }
```

## 📋 Integration Checklist

### For ANY Service

- [ ] Install `ai-platform-core` package
- [ ] Choose provider (OpenAI, Claude, etc.)
- [ ] Initialize AI engine
- [ ] Create AI request
- [ ] Generate response
- [ ] Use response in your application

### For Production SaaS

- [ ] Install core + provider + storage packages
- [ ] Setup Redis cache
- [ ] Setup PostgreSQL token tracking
- [ ] Configure DI container
- [ ] Add health check endpoint
- [ ] Add quota check before generation
- [ ] Add usage dashboard
- [ ] Setup monitoring/alerts

## 🚀 Quick Start Examples

### Example 1: Add to Storefront Service

```bash
# Install (future)
# pip install ai-platform-core ai-platform-openai

# Add to requirements.txt
echo "ai-platform-core>=1.0.0" >> requirements.txt
```

```python
# app/ai.py
from ai_core import container
from config import settings

def init_ai():
    # from ai_providers.openai import OpenAIProvider
    # provider = OpenAIProvider(api_key=settings.OPENAI_API_KEY)
    # container.register_provider(provider)
    pass

# app/main.py
from fastapi import FastAPI
from app.ai import init_ai

app = FastAPI()

@app.on_event("startup")
async def startup():
    init_ai()

# app/routers/products.py
from ai_core import container, AIRequest

@router.post("/products/{id}/ai-description")
async def generate_description(id: str):
    engine = container.get_engine()
    # ... use engine
```

### Example 2: New Review Service

```bash
# Create new service
mkdir -p domain-services/review-service
cd domain-services/review-service

# Install
# pip install ai-platform-core ai-platform-openai
```

```python
# main.py
from fastapi import FastAPI
from ai_core import container
# from ai_providers.openai import OpenAIProvider

app = FastAPI()

@app.on_event("startup")
async def startup():
    # provider = OpenAIProvider(api_key="sk-...")
    # container.register_provider(provider)
    pass

@app.post("/reviews/{id}/generate-response")
async def generate_response(id: str, review_text: str):
    from ai_core import AIRequest

    engine = container.get_engine()
    request = AIRequest(prompt=f"Respond to: {review_text}")
    response = await engine.generate(request)

    return {"response": response.content}
```

## 💡 Benefits of Modular Approach

### ✅ Code Reusability
Write AI code once, use everywhere

### ✅ Easy Testing
Mock interfaces for unit tests

### ✅ Easy Swapping
Change providers without touching app code

### ✅ Incremental Adoption
Start simple, add features as needed

### ✅ Framework Independence
Works with any Python framework

### ✅ Clear Architecture
Layers make it easy to understand and maintain

## 📊 Comparison

### Before (Tight Coupling)

```python
# Tightly coupled to OpenAI
import openai

def generate_description(product):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"...{product}..."}]
    )
    return response.choices[0].message.content

# Problems:
# - Hard to test (need real API)
# - Hard to switch providers
# - Hard to add caching
# - Hard to track usage
# - Repeated across services
```

### After (Modular)

```python
# Clean, modular, testable
from ai_core import container, AIRequest

def generate_description(product):
    engine = container.get_engine()
    request = AIRequest(prompt=f"...{product}...")
    response = await engine.generate(request)
    return response.content

# Benefits:
# - Easy to test (mock engine)
# - Easy to switch providers (config change)
# - Caching built-in
# - Usage tracking built-in
# - Reusable across all services
```

## 🎯 Next Steps

1. **Review Architecture** - See `MODULAR_AI_ARCHITECTURE.md`
2. **Install Package** - `pip install ai-platform-core`
3. **Choose Provider** - OpenAI, Claude, or local
4. **Integrate** - Follow patterns above
5. **Add Features** - Use feature plugins when available

---

**The modular architecture makes AI integration trivial. Just import, configure, and use!** 🚀
