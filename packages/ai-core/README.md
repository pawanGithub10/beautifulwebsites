# AI Core - Universal AI Engine

**Modular, framework-agnostic AI engine for any Python application.**

## 🎯 Features

- **Framework Agnostic** - Works with FastAPI, Flask, Django, or standalone
- **Provider Agnostic** - Easy switch between OpenAI, Claude, local models
- **Layered Architecture** - Clean separation of concerns
- **Dependency Injection** - Easy to test and extend
- **Caching Built-in** - Reduce API costs by 30-50%
- **Token Tracking** - Monitor usage and costs
- **Type Safe** - Full type hints

## 📦 Installation

```bash
# From source (for now)
cd packages/ai-core
pip install -e .

# With specific providers
pip install -e ".[openai]"
pip install -e ".[anthropic]"
pip install -e ".[all]"
```

## 🚀 Quick Start

### Standalone Usage

```python
from ai_core.application import AIEngine
from ai_core.domain.models import AIRequest
from ai_core.infrastructure import InMemoryCache

# For this example, you'd need to implement OpenAIProvider
# See packages/ai-providers/openai for implementation

# from ai_providers.openai import OpenAIProvider

# Setup
# provider = OpenAIProvider(api_key="sk-...")
# cache = InMemoryCache()
# engine = AIEngine(provider=provider, cache=cache)

# Generate
# request = AIRequest(
#     prompt="Write a product description for organic green tea",
#     temperature=0.7,
#     max_tokens=200
# )

# response = await engine.generate(request)
# print(response.content)
```

### With Dependency Injection

```python
from ai_core.di import container

# Setup once at app startup
container.register_provider(OpenAIProvider(api_key="..."))
container.register_cache(InMemoryCache())

# Use anywhere in your app
engine = container.get_engine()
response = await engine.generate(request)
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends
from ai_core.di import container
from ai_core.application import AIEngine

app = FastAPI()

def get_ai_engine() -> AIEngine:
    return container.get_engine()

@app.post("/generate")
async def generate(
    prompt: str,
    engine: AIEngine = Depends(get_ai_engine)
):
    from ai_core.domain.models import AIRequest

    request = AIRequest(prompt=prompt)
    response = await engine.generate(request)

    return {"content": response.content}
```

### Flask Integration

```python
from flask import Flask, request, jsonify
from ai_core.di import container

app = Flask(__name__)

# Setup
container.register_provider(OpenAIProvider(api_key="..."))
engine = container.get_engine()

@app.route('/generate', methods=['POST'])
async def generate():
    from ai_core.domain.models import AIRequest

    data = request.json
    ai_request = AIRequest(prompt=data['prompt'])
    response = await engine.generate(ai_request)

    return jsonify({"content": response.content})
```

## 🏗️ Architecture

```
ai-core/
├── domain/              # Core business logic (no dependencies)
│   ├── interfaces/      # Ports (abstractions)
│   │   ├── IAIProvider.py
│   │   ├── ICache.py
│   │   └── ITokenTracker.py
│   └── models/         # Domain models
│       ├── AIRequest.py
│       ├── AIResponse.py
│       └── TokenUsage.py
│
├── application/        # Use cases & orchestration
│   └── AIEngine.py     # Main engine
│
├── infrastructure/     # External implementations
│   └── InMemoryCache.py
│
└── di/                # Dependency injection
    └── container.py
```

## 🧩 Modular Design

### Layers

1. **Domain Layer** - Pure business logic, no external dependencies
2. **Application Layer** - Use cases and orchestration
3. **Infrastructure Layer** - External integrations (databases, APIs)
4. **Presentation Layer** - API endpoints (not included in core)

### Interfaces (Ports)

The system is built around interfaces:

- `IAIProvider` - Any AI provider (OpenAI, Claude, etc.)
- `ICache` - Any cache (Redis, Memcached, in-memory)
- `ITokenTracker` - Any storage for usage tracking
- `IPromptTemplate` - Any template engine

This makes it easy to:
- Swap implementations
- Test with mocks
- Add new providers
- Use multiple providers simultaneously

## 💡 Usage Patterns

### Pattern 1: Simple Generation

```python
engine = AIEngine(provider=OpenAIProvider())

request = AIRequest(prompt="Hello, world!")
response = await engine.generate(request)
```

### Pattern 2: With Caching

```python
engine = AIEngine(
    provider=OpenAIProvider(),
    cache=InMemoryCache()
)

# First call hits API
response1 = await engine.generate(request)

# Second call uses cache (instant, free!)
response2 = await engine.generate(request)
```

### Pattern 3: With Tracking

```python
from ai_core.domain.models import PromptContext

engine = AIEngine(
    provider=OpenAIProvider(),
    token_tracker=PostgresTracker()
)

context = PromptContext(
    variables={},
    site_id="site-123",
    feature="product_description"
)

response = await engine.generate(request, context)

# Usage is automatically tracked in database
```

### Pattern 4: Builder Pattern

```python
from ai_core.application import AIEngineBuilder

engine = (AIEngineBuilder()
    .with_provider(OpenAIProvider())
    .with_cache(RedisCache())
    .with_token_tracker(PostgresTracker())
    .with_cache_ttl_days(30)
    .build())
```

## 🧪 Testing

Mock any interface for easy testing:

```python
from unittest.mock import Mock
from ai_core.application import AIEngine
from ai_core.domain.models import AIRequest, AIResponse

# Create mock provider
mock_provider = Mock()
mock_provider.generate_completion.return_value = AIResponse(
    content="Mocked response",
    tokens_used=100,
    model="gpt-4",
    finish_reason="stop"
)

# Test your code
engine = AIEngine(provider=mock_provider)
response = await engine.generate(AIRequest(prompt="test"))

assert response.content == "Mocked response"
```

## 📊 Health Checks

```python
health = await engine.health_check()

# Returns:
# {
#     "provider": {
#         "name": "openai",
#         "healthy": True,
#         "capabilities": {...}
#     },
#     "cache": {
#         "enabled": True,
#         "healthy": True
#     },
#     "tracking": {
#         "enabled": True
#     }
# }
```

## 🔧 Configuration

The core package is minimal and has no configuration files.
All configuration is done via code (dependency injection).

For a complete configuration-driven setup, see the full platform documentation.

## 🚀 Next Steps

1. **Implement Providers** - See `packages/ai-providers/`
2. **Add Features** - See `packages/ai-features/`
3. **Integrate** - See `packages/ai-integrations/`

## 📝 License

Part of the Beautiful Websites platform.

---

**This is just the core engine. For complete AI features (product descriptions, review responses, social calendar), see the parent documentation.**
