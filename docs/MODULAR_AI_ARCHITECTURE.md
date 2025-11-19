# Modular AI Architecture - Universal & Layered Design

**Version:** 2.0 (Modular & Portable)
**Date:** January 2025
**Design Philosophy:** Build once, use anywhere

---

## 🎯 Design Principles

### 1. **Extreme Modularity**
Every component is independently usable, testable, and deployable

### 2. **Clean Layered Architecture**
Clear separation of concerns following hexagonal/onion architecture

### 3. **Framework Agnostic**
Works with FastAPI, Flask, Django, Express.js, or any framework

### 4. **Provider Agnostic**
Easily switch between OpenAI, Claude, local models, or multiple providers

### 5. **Configuration-Driven**
Zero code changes to add new AI capabilities

### 6. **Plugin Architecture**
Add/remove features without modifying core code

---

## 📐 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      PRESENTATION LAYER                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   FastAPI    │  │    Flask     │  │   Express    │              │
│  │   Endpoints  │  │   Routes     │  │   Routes     │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         └─────────────────┼─────────────────┘                       │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────────┐
│                    APPLICATION LAYER                                │
│                  (Use Cases & Orchestration)                        │
│                                                                     │
│  ┌────────────────────────▼──────────────────────┐                 │
│  │         AI Feature Controllers                 │                 │
│  │  • ProductDescriptionController                │                 │
│  │  • ReviewResponseController                    │                 │
│  │  • SocialCalendarController                    │                 │
│  └────────────────────────┬──────────────────────┘                 │
│                           │                                         │
│  ┌────────────────────────▼──────────────────────┐                 │
│  │           Use Case Handlers                    │                 │
│  │  • GenerateDescriptionUseCase                  │                 │
│  │  • GenerateReviewResponseUseCase               │                 │
│  │  • GenerateContentCalendarUseCase              │                 │
│  └────────────────────────┬──────────────────────┘                 │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────────┐
│                      DOMAIN LAYER                                   │
│                  (Core Business Logic)                              │
│                                                                     │
│  ┌────────────────────────▼──────────────────────┐                 │
│  │         AI Core Engine (Pure Logic)            │                 │
│  │                                                │                 │
│  │  ┌──────────────────────────────────────┐     │                 │
│  │  │   Prompt Builder                     │     │                 │
│  │  │   • Template Management              │     │                 │
│  │  │   • Variable Substitution            │     │                 │
│  │  │   • Context Enrichment               │     │                 │
│  │  └──────────────────────────────────────┘     │                 │
│  │                                                │                 │
│  │  ┌──────────────────────────────────────┐     │                 │
│  │  │   Response Processor                 │     │                 │
│  │  │   • Parse & Validate                 │     │                 │
│  │  │   • Format & Transform               │     │                 │
│  │  │   • Error Handling                   │     │                 │
│  │  └──────────────────────────────────────┘     │                 │
│  │                                                │                 │
│  │  ┌──────────────────────────────────────┐     │                 │
│  │  │   Token Manager                      │     │                 │
│  │  │   • Usage Tracking                   │     │                 │
│  │  │   • Cost Calculation                 │     │                 │
│  │  │   • Quota Enforcement                │     │                 │
│  │  └──────────────────────────────────────┘     │                 │
│  └────────────────────────┬──────────────────────┘                 │
│                           │                                         │
│  ┌────────────────────────▼──────────────────────┐                 │
│  │    Domain Models & Interfaces (Ports)          │                 │
│  │  • IAIProvider (interface)                     │                 │
│  │  • IPromptTemplate (interface)                 │                 │
│  │  • ITokenTracker (interface)                   │                 │
│  │  • ICache (interface)                          │                 │
│  └────────────────────────┬──────────────────────┘                 │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                              │
│                    (External Integrations)                          │
│                                                                     │
│  ┌────────────────────────▼──────────────────────┐                 │
│  │      Provider Adapters (Implementations)       │                 │
│  │                                                │                 │
│  │  ┌──────────────┐  ┌──────────────┐          │                 │
│  │  │   OpenAI     │  │   Claude     │          │                 │
│  │  │   Adapter    │  │   Adapter    │  ...     │                 │
│  │  └──────────────┘  └──────────────┘          │                 │
│  │                                                │                 │
│  │  • Implements IAIProvider interface           │                 │
│  │  • Handles API-specific logic                 │                 │
│  │  • Retry & failover                           │                 │
│  └────────────────────────┬──────────────────────┘                 │
│                           │                                         │
│  ┌────────────────────────▼──────────────────────┐                 │
│  │         Storage Adapters                       │                 │
│  │  • PostgresRepository                          │                 │
│  │  • RedisCache                                  │                 │
│  │  • S3Storage                                   │                 │
│  └────────────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🧩 Modular Package Structure

```
ai-platform/
├── packages/
│   ├── ai-core/                    # Core AI engine (framework-agnostic)
│   │   ├── domain/
│   │   │   ├── interfaces/
│   │   │   │   ├── IAIProvider.py
│   │   │   │   ├── IPromptTemplate.py
│   │   │   │   ├── ITokenTracker.py
│   │   │   │   └── ICache.py
│   │   │   ├── models/
│   │   │   │   ├── AIRequest.py
│   │   │   │   ├── AIResponse.py
│   │   │   │   └── PromptContext.py
│   │   │   └── services/
│   │   │       ├── PromptBuilder.py
│   │   │       ├── ResponseProcessor.py
│   │   │       └── TokenManager.py
│   │   ├── application/
│   │   │   ├── AIEngine.py          # Main orchestrator
│   │   │   └── usecases/
│   │   │       └── GenerateCompletion.py
│   │   └── setup.py                  # Standalone package
│   │
│   ├── ai-providers/                # Provider adapters
│   │   ├── openai/
│   │   │   ├── OpenAIProvider.py    # Implements IAIProvider
│   │   │   └── config.py
│   │   ├── anthropic/
│   │   │   ├── ClaudeProvider.py    # Implements IAIProvider
│   │   │   └── config.py
│   │   ├── local/
│   │   │   ├── OllamaProvider.py    # Local LLMs
│   │   │   └── config.py
│   │   └── setup.py
│   │
│   ├── ai-features/                 # Feature plugins
│   │   ├── product-description/
│   │   │   ├── plugin.py            # Feature plugin interface
│   │   │   ├── prompts/
│   │   │   │   ├── base.yaml
│   │   │   │   ├── grocery.yaml
│   │   │   │   └── electronics.yaml
│   │   │   ├── handlers/
│   │   │   │   └── DescriptionHandler.py
│   │   │   └── setup.py
│   │   ├── review-response/
│   │   │   ├── plugin.py
│   │   │   ├── prompts/
│   │   │   │   ├── positive.yaml
│   │   │   │   └── negative.yaml
│   │   │   ├── handlers/
│   │   │   │   ├── SentimentAnalyzer.py
│   │   │   │   └── ResponseHandler.py
│   │   │   └── setup.py
│   │   ├── social-calendar/
│   │   │   ├── plugin.py
│   │   │   ├── prompts/
│   │   │   │   └── calendar.yaml
│   │   │   ├── handlers/
│   │   │   │   └── CalendarHandler.py
│   │   │   └── setup.py
│   │   └── setup.py
│   │
│   ├── ai-storage/                  # Storage adapters
│   │   ├── postgres/
│   │   │   └── PostgresRepository.py
│   │   ├── redis/
│   │   │   └── RedisCache.py
│   │   ├── memory/
│   │   │   └── InMemoryCache.py
│   │   └── setup.py
│   │
│   ├── ai-integrations/             # Framework integrations
│   │   ├── fastapi/
│   │   │   ├── middleware.py
│   │   │   ├── dependencies.py
│   │   │   └── routes.py
│   │   ├── flask/
│   │   │   ├── blueprint.py
│   │   │   └── decorators.py
│   │   ├── django/
│   │   │   ├── apps.py
│   │   │   └── views.py
│   │   └── setup.py
│   │
│   └── ai-sdk/                      # Client SDKs
│       ├── python/
│       │   └── ai_platform_sdk/
│       ├── javascript/
│       │   └── ai-platform-sdk/
│       └── rest-api/
│           └── openapi.yaml
│
├── services/
│   ├── ai-gateway-service/          # Optional: Standalone microservice
│   │   ├── main.py
│   │   ├── api/
│   │   ├── config.py
│   │   └── Dockerfile
│   │
│   └── examples/                     # Integration examples
│       ├── fastapi-example/
│       ├── flask-example/
│       └── standalone-example/
│
└── shared/
    ├── config/
    │   └── ai-config.yaml            # Central configuration
    └── schemas/
        └── api-schemas.json
```

---

## 🔌 Core Interfaces (Ports)

### 1. IAIProvider Interface

```python
# packages/ai-core/domain/interfaces/IAIProvider.py

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..models import AIRequest, AIResponse

class IAIProvider(ABC):
    """
    Abstract AI provider interface.
    Any LLM provider (OpenAI, Claude, local) must implement this.
    """

    @abstractmethod
    async def generate_completion(
        self,
        request: AIRequest
    ) -> AIResponse:
        """Generate AI completion"""
        pass

    @abstractmethod
    async def estimate_tokens(
        self,
        text: str
    ) -> int:
        """Estimate token count"""
        pass

    @abstractmethod
    async def check_health(self) -> bool:
        """Check provider availability"""
        pass

    @abstractmethod
    def get_pricing(self) -> Dict[str, float]:
        """Get current pricing per 1K tokens"""
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get provider capabilities"""
        pass
```

### 2. IPromptTemplate Interface

```python
# packages/ai-core/domain/interfaces/IPromptTemplate.py

from abc import ABC, abstractmethod
from typing import Dict, Any
from ..models import PromptContext

class IPromptTemplate(ABC):
    """Abstract prompt template interface"""

    @abstractmethod
    def render(
        self,
        context: PromptContext
    ) -> str:
        """Render prompt with context"""
        pass

    @abstractmethod
    def validate_context(
        self,
        context: PromptContext
    ) -> bool:
        """Validate required context variables"""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        """Get template metadata"""
        pass
```

### 3. ITokenTracker Interface

```python
# packages/ai-core/domain/interfaces/ITokenTracker.py

from abc import ABC, abstractmethod
from typing import Optional
from ..models import TokenUsage

class ITokenTracker(ABC):
    """Abstract token tracking interface"""

    @abstractmethod
    async def track_usage(
        self,
        site_id: str,
        feature: str,
        usage: TokenUsage
    ) -> None:
        """Track token usage"""
        pass

    @abstractmethod
    async def get_usage(
        self,
        site_id: str,
        period: str
    ) -> Dict[str, Any]:
        """Get usage statistics"""
        pass

    @abstractmethod
    async def check_quota(
        self,
        site_id: str
    ) -> bool:
        """Check if within quota"""
        pass

    @abstractmethod
    async def calculate_cost(
        self,
        usage: TokenUsage
    ) -> float:
        """Calculate cost for usage"""
        pass
```

### 4. ICache Interface

```python
# packages/ai-core/domain/interfaces/ICache.py

from abc import ABC, abstractmethod
from typing import Optional, Any
from datetime import timedelta

class ICache(ABC):
    """Abstract caching interface"""

    @abstractmethod
    async def get(
        self,
        key: str
    ) -> Optional[Any]:
        """Get cached value"""
        pass

    @abstractmethod
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[timedelta] = None
    ) -> None:
        """Set cached value"""
        pass

    @abstractmethod
    async def delete(
        self,
        key: str
    ) -> None:
        """Delete cached value"""
        pass

    @abstractmethod
    async def exists(
        self,
        key: str
    ) -> bool:
        """Check if key exists"""
        pass
```

---

## 🏗️ Core Domain Models

```python
# packages/ai-core/domain/models/AIRequest.py

from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class AIRequest:
    """Universal AI request model"""
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 500
    model: str = "gpt-4"
    response_format: str = "text"  # text, json
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "system_prompt": self.system_prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "model": self.model,
            "response_format": self.response_format,
            "metadata": self.metadata or {}
        }


@dataclass
class AIResponse:
    """Universal AI response model"""
    content: str
    tokens_used: int
    model: str
    finish_reason: str
    metadata: Dict[str, Any] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "tokens_used": self.tokens_used,
            "model": self.model,
            "finish_reason": self.finish_reason,
            "metadata": self.metadata or {}
        }


@dataclass
class PromptContext:
    """Context for prompt rendering"""
    variables: Dict[str, Any]
    site_id: Optional[str] = None
    user_id: Optional[str] = None
    feature: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class TokenUsage:
    """Token usage tracking"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model: str
    estimated_cost: float
```

---

## 🎯 Core AI Engine (Framework Agnostic)

```python
# packages/ai-core/application/AIEngine.py

from typing import Optional, Dict, Any
from ..domain.interfaces import IAIProvider, IPromptTemplate, ITokenTracker, ICache
from ..domain.models import AIRequest, AIResponse, PromptContext
import hashlib
import json

class AIEngine:
    """
    Core AI Engine - completely framework agnostic.
    Can be used in FastAPI, Flask, Django, or standalone scripts.
    """

    def __init__(
        self,
        provider: IAIProvider,
        cache: Optional[ICache] = None,
        token_tracker: Optional[ITokenTracker] = None
    ):
        self.provider = provider
        self.cache = cache
        self.token_tracker = token_tracker

    async def generate(
        self,
        request: AIRequest,
        context: Optional[PromptContext] = None,
        use_cache: bool = True
    ) -> AIResponse:
        """
        Generate AI completion with caching and tracking.

        This is the main entry point - completely provider-agnostic.
        """

        # Generate cache key
        if use_cache and self.cache:
            cache_key = self._generate_cache_key(request)
            cached = await self.cache.get(cache_key)
            if cached:
                return AIResponse(**cached)

        # Call provider
        response = await self.provider.generate_completion(request)

        # Track usage
        if self.token_tracker and context:
            from ..domain.models import TokenUsage
            usage = TokenUsage(
                prompt_tokens=response.tokens_used // 2,  # Estimate
                completion_tokens=response.tokens_used // 2,
                total_tokens=response.tokens_used,
                model=response.model,
                estimated_cost=await self.token_tracker.calculate_cost(
                    TokenUsage(
                        prompt_tokens=response.tokens_used // 2,
                        completion_tokens=response.tokens_used // 2,
                        total_tokens=response.tokens_used,
                        model=response.model,
                        estimated_cost=0.0
                    )
                )
            )
            await self.token_tracker.track_usage(
                site_id=context.site_id,
                feature=context.feature,
                usage=usage
            )

        # Cache response
        if use_cache and self.cache:
            await self.cache.set(
                cache_key,
                response.to_dict(),
                ttl=timedelta(days=7)
            )

        return response

    def _generate_cache_key(self, request: AIRequest) -> str:
        """Generate deterministic cache key"""
        key_data = {
            "prompt": request.prompt,
            "system_prompt": request.system_prompt,
            "model": request.model,
            "temperature": request.temperature
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return f"ai:cache:{hashlib.sha256(key_string.encode()).hexdigest()}"

    async def estimate_cost(self, text: str, model: str = "gpt-4") -> float:
        """Estimate cost for generating completion"""
        tokens = await self.provider.estimate_tokens(text)
        pricing = self.provider.get_pricing()
        return (tokens / 1000) * pricing.get(model, 0.03)

    async def health_check(self) -> Dict[str, Any]:
        """Check system health"""
        return {
            "provider": await self.provider.check_health(),
            "cache": await self.cache.exists("health") if self.cache else None,
            "capabilities": self.provider.get_capabilities()
        }
```

---

## 🔧 Provider Implementations

### OpenAI Provider

```python
# packages/ai-providers/openai/OpenAIProvider.py

from ai_core.domain.interfaces import IAIProvider
from ai_core.domain.models import AIRequest, AIResponse
import openai
from typing import Dict, Any

class OpenAIProvider(IAIProvider):
    """OpenAI GPT provider implementation"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        openai.api_key = api_key

    async def generate_completion(
        self,
        request: AIRequest
    ) -> AIResponse:
        """Generate completion using OpenAI"""

        messages = []
        if request.system_prompt:
            messages.append({
                "role": "system",
                "content": request.system_prompt
            })
        messages.append({
            "role": "user",
            "content": request.prompt
        })

        response = await openai.ChatCompletion.acreate(
            model=request.model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            response_format={"type": request.response_format}
        )

        return AIResponse(
            content=response.choices[0].message.content,
            tokens_used=response.usage.total_tokens,
            model=response.model,
            finish_reason=response.choices[0].finish_reason,
            metadata={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens
            }
        )

    async def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using tiktoken"""
        import tiktoken
        encoding = tiktoken.encoding_for_model("gpt-4")
        return len(encoding.encode(text))

    async def check_health(self) -> bool:
        """Check OpenAI API health"""
        try:
            await openai.Model.alist()
            return True
        except:
            return False

    def get_pricing(self) -> Dict[str, float]:
        """OpenAI pricing per 1K tokens"""
        return {
            "gpt-4": 0.03,
            "gpt-3.5-turbo": 0.001
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Provider capabilities"""
        return {
            "models": ["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"],
            "max_tokens": 8192,
            "supports_functions": True,
            "supports_vision": True
        }
```

### Claude Provider

```python
# packages/ai-providers/anthropic/ClaudeProvider.py

from ai_core.domain.interfaces import IAIProvider
from ai_core.domain.models import AIRequest, AIResponse
import anthropic
from typing import Dict, Any

class ClaudeProvider(IAIProvider):
    """Anthropic Claude provider implementation"""

    def __init__(self, api_key: str):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def generate_completion(
        self,
        request: AIRequest
    ) -> AIResponse:
        """Generate completion using Claude"""

        message = await self.client.messages.create(
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            system=request.system_prompt or "",
            messages=[{
                "role": "user",
                "content": request.prompt
            }]
        )

        return AIResponse(
            content=message.content[0].text,
            tokens_used=message.usage.input_tokens + message.usage.output_tokens,
            model=message.model,
            finish_reason=message.stop_reason,
            metadata={
                "prompt_tokens": message.usage.input_tokens,
                "completion_tokens": message.usage.output_tokens
            }
        )

    async def estimate_tokens(self, text: str) -> int:
        """Estimate tokens (rough approximation)"""
        return len(text) // 4

    async def check_health(self) -> bool:
        """Check Claude API health"""
        try:
            await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except:
            return False

    def get_pricing(self) -> Dict[str, float]:
        """Claude pricing per 1K tokens"""
        return {
            "claude-3-opus": 0.015,
            "claude-3-sonnet": 0.003,
            "claude-3-haiku": 0.00025
        }

    def get_capabilities(self) -> Dict[str, Any]:
        """Provider capabilities"""
        return {
            "models": ["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
            "max_tokens": 200000,
            "supports_functions": True,
            "supports_vision": True
        }
```

---

## 🧩 Feature Plugins

### Product Description Plugin

```python
# packages/ai-features/product-description/plugin.py

from ai_core.application import AIEngine
from ai_core.domain.models import AIRequest, PromptContext
from typing import Dict, Any
import yaml
import os

class ProductDescriptionPlugin:
    """
    Modular product description generator.
    Can be used in ANY service - just import and use!
    """

    def __init__(self, ai_engine: AIEngine):
        self.ai_engine = ai_engine
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, str]:
        """Load prompt templates from YAML files"""
        prompts = {}
        prompt_dir = os.path.join(os.path.dirname(__file__), "prompts")

        for filename in os.listdir(prompt_dir):
            if filename.endswith(".yaml"):
                with open(os.path.join(prompt_dir, filename)) as f:
                    data = yaml.safe_load(f)
                    prompts[data['name']] = data['template']

        return prompts

    async def generate_description(
        self,
        product_data: Dict[str, Any],
        category: str = "base",
        tone: str = "professional",
        length: str = "medium",
        site_id: str = None
    ) -> Dict[str, Any]:
        """
        Generate product description.

        Args:
            product_data: Product attributes (name, price, features, etc.)
            category: Product category (grocery, electronics, fashion, etc.)
            tone: Desired tone (professional, casual, luxury, playful)
            length: Desired length (short, medium, long)
            site_id: Site ID for tracking

        Returns:
            {
                "description": "Full description",
                "short_description": "Summary",
                "meta_title": "SEO title",
                "meta_description": "SEO description",
                "tags": ["tag1", "tag2"]
            }
        """

        # Select prompt template
        template_key = f"{category}_description" if category in self.prompts else "base_description"
        prompt_template = self.prompts.get(template_key, self.prompts["base_description"])

        # Build prompt
        prompt = prompt_template.format(
            product_name=product_data.get("name"),
            category=product_data.get("category"),
            price=product_data.get("price"),
            features=", ".join(product_data.get("features", [])),
            tone=tone,
            length=length
        )

        # Create AI request
        request = AIRequest(
            prompt=prompt,
            system_prompt="You are an expert e-commerce copywriter. Generate compelling product descriptions in JSON format.",
            model="gpt-4",
            temperature=0.7,
            max_tokens=500,
            response_format="json"
        )

        # Generate
        context = PromptContext(
            variables=product_data,
            site_id=site_id,
            feature="product_description"
        )

        response = await self.ai_engine.generate(request, context)

        # Parse and return
        import json
        return json.loads(response.content)
```

### Prompt Template (YAML)

```yaml
# packages/ai-features/product-description/prompts/grocery.yaml

name: grocery_description
category: grocery
template: |
  You are an expert grocery product copywriter. Generate a compelling product description.

  Product Information:
  - Name: {product_name}
  - Category: {category}
  - Price: {price}
  - Key Features: {features}

  Requirements:
  1. Tone: {tone}
  2. Length: {length} (short: 50-100 words, medium: 150-250 words, long: 300-500 words)
  3. Focus on: Freshness, quality, health benefits, source/origin
  4. Include SEO keywords naturally
  5. Create desire and urgency

  Output Format (JSON):
  {{
    "description": "Full product description",
    "short_description": "1-2 sentence summary",
    "meta_title": "SEO-optimized title (max 60 chars)",
    "meta_description": "SEO meta description (max 160 chars)",
    "tags": ["tag1", "tag2", "tag3"]
  }}
```

---

## 🚀 Usage Examples

### Example 1: Standalone Script

```python
# examples/standalone-example/generate_description.py

from ai_core.application import AIEngine
from ai_providers.openai import OpenAIProvider
from ai_features.product_description import ProductDescriptionPlugin
import asyncio

async def main():
    # Setup
    provider = OpenAIProvider(api_key="sk-...")
    engine = AIEngine(provider=provider)
    plugin = ProductDescriptionPlugin(ai_engine=engine)

    # Generate
    result = await plugin.generate_description(
        product_data={
            "name": "Organic Green Tea",
            "category": "Beverages",
            "price": 299,
            "features": ["organic", "antioxidant-rich", "imported"]
        },
        category="grocery",
        tone="professional",
        length="medium"
    )

    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

### Example 2: FastAPI Integration

```python
# examples/fastapi-example/main.py

from fastapi import FastAPI, Depends
from ai_core.application import AIEngine
from ai_providers.openai import OpenAIProvider
from ai_features.product_description import ProductDescriptionPlugin
from ai_integrations.fastapi import get_ai_engine
from pydantic import BaseModel

app = FastAPI()

# Dependency injection
def get_product_plugin(engine: AIEngine = Depends(get_ai_engine)):
    return ProductDescriptionPlugin(ai_engine=engine)

class ProductRequest(BaseModel):
    name: str
    category: str
    price: float
    features: list[str]

@app.post("/api/v1/products/generate-description")
async def generate_description(
    request: ProductRequest,
    plugin: ProductDescriptionPlugin = Depends(get_product_plugin)
):
    result = await plugin.generate_description(
        product_data=request.dict(),
        category="grocery"
    )
    return result
```

### Example 3: Flask Integration

```python
# examples/flask-example/app.py

from flask import Flask, jsonify, request
from ai_core.application import AIEngine
from ai_providers.openai import OpenAIProvider
from ai_features.product_description import ProductDescriptionPlugin

app = Flask(__name__)

# Initialize once
provider = OpenAIProvider(api_key="sk-...")
engine = AIEngine(provider=provider)
plugin = ProductDescriptionPlugin(ai_engine=engine)

@app.route('/api/v1/products/generate-description', methods=['POST'])
async def generate_description():
    data = request.json

    result = await plugin.generate_description(
        product_data=data,
        category=data.get('category', 'base')
    )

    return jsonify(result)

if __name__ == '__main__':
    app.run()
```

### Example 4: Add to Existing Storefront Service

```python
# domain-services/storefront-service/app/ai_integration.py

from ai_core.application import AIEngine
from ai_providers.openai import OpenAIProvider
from ai_features.product_description import ProductDescriptionPlugin
from ai_storage.postgres import PostgresTokenTracker
from ai_storage.redis import RedisCache
from app.config import settings

# Initialize AI components
provider = OpenAIProvider(api_key=settings.OPENAI_API_KEY)
cache = RedisCache(redis_url=settings.REDIS_URL)
tracker = PostgresTokenTracker(db_url=settings.DATABASE_URL)

engine = AIEngine(
    provider=provider,
    cache=cache,
    token_tracker=tracker
)

# Initialize feature plugins
product_description_plugin = ProductDescriptionPlugin(ai_engine=engine)

# Export for use in routers
__all__ = ['product_description_plugin']
```

```python
# domain-services/storefront-service/app/routers/products.py

from fastapi import APIRouter, HTTPException
from app.ai_integration import product_description_plugin
from app.schemas import ProductCreate

router = APIRouter()

@router.post("/api/v1/catalog/{site_id}/products")
async def create_product(
    site_id: str,
    product: ProductCreate,
    generate_ai_description: bool = False
):
    # Create product in database
    # ... existing code ...

    # Optionally generate AI description
    if generate_ai_description:
        ai_description = await product_description_plugin.generate_description(
            product_data=product.dict(),
            category=product.category,
            site_id=site_id
        )
        product.description = ai_description['description']
        product.short_description = ai_description['short_description']
        # ... save to database ...

    return product
```

---

## 📦 Configuration-Driven Setup

### Central Configuration

```yaml
# shared/config/ai-config.yaml

ai:
  # Provider selection
  default_provider: "openai"

  providers:
    openai:
      api_key: ${OPENAI_API_KEY}
      models:
        default: "gpt-4"
        fast: "gpt-3.5-turbo"
      rate_limit: 100  # requests per minute

    anthropic:
      api_key: ${ANTHROPIC_API_KEY}
      models:
        default: "claude-3-sonnet"
        fast: "claude-3-haiku"
      rate_limit: 50

    local:
      endpoint: "http://localhost:11434"  # Ollama
      models:
        default: "llama2"

  # Caching
  cache:
    enabled: true
    backend: "redis"  # redis, memory, none
    ttl_days: 7

  # Token tracking
  tracking:
    enabled: true
    backend: "postgres"  # postgres, none

  # Features
  features:
    product_description:
      enabled: true
      default_category: "base"
      default_tone: "professional"
      default_length: "medium"

    review_response:
      enabled: true
      auto_approve: false
      sentiment_threshold: 0.5

    social_calendar:
      enabled: true
      default_posts_per_week: 5
```

### Configuration Loader

```python
# packages/ai-core/config/loader.py

import yaml
import os
from typing import Dict, Any

class AIConfig:
    """Load and manage AI configuration"""

    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.getenv("AI_CONFIG_PATH", "ai-config.yaml")

        with open(config_path) as f:
            self.config = yaml.safe_load(f)

    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get provider configuration"""
        return self.config['ai']['providers'].get(provider, {})

    def get_feature_config(self, feature: str) -> Dict[str, Any]:
        """Get feature configuration"""
        return self.config['ai']['features'].get(feature, {})

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if feature is enabled"""
        return self.config['ai']['features'].get(feature, {}).get('enabled', False)
```

---

## 🎯 Dependency Injection Container

```python
# packages/ai-core/di/container.py

from typing import Optional
from ..application import AIEngine
from ..domain.interfaces import IAIProvider, ICache, ITokenTracker

class AIContainer:
    """
    Dependency injection container for AI components.
    Makes it easy to swap implementations.
    """

    def __init__(self):
        self._provider: Optional[IAIProvider] = None
        self._cache: Optional[ICache] = None
        self._tracker: Optional[ITokenTracker] = None
        self._engine: Optional[AIEngine] = None

    def register_provider(self, provider: IAIProvider):
        """Register AI provider"""
        self._provider = provider
        return self

    def register_cache(self, cache: ICache):
        """Register cache"""
        self._cache = cache
        return self

    def register_tracker(self, tracker: ITokenTracker):
        """Register token tracker"""
        self._tracker = tracker
        return self

    def get_engine(self) -> AIEngine:
        """Get configured AI engine"""
        if self._engine is None:
            if self._provider is None:
                raise ValueError("Provider must be registered first")

            self._engine = AIEngine(
                provider=self._provider,
                cache=self._cache,
                token_tracker=self._tracker
            )

        return self._engine

# Global container instance
container = AIContainer()
```

### Usage with DI

```python
# Initialize once at application startup
from ai_core.di import container
from ai_providers.openai import OpenAIProvider
from ai_storage.redis import RedisCache
from ai_storage.postgres import PostgresTokenTracker

# Setup
container.register_provider(OpenAIProvider(api_key="sk-..."))
container.register_cache(RedisCache(redis_url="redis://localhost"))
container.register_tracker(PostgresTokenTracker(db_url="postgresql://..."))

# Use anywhere in your application
engine = container.get_engine()
```

---

## 📊 Modular Benefits Summary

### ✅ Portability
- Use in ANY Python framework (FastAPI, Flask, Django)
- Use in JavaScript (create JS wrapper around REST API)
- Use as standalone CLI tool
- Deploy as microservice or library

### ✅ Testability
- Mock any interface for testing
- Test each layer independently
- No framework dependencies in core logic

### ✅ Maintainability
- Clear separation of concerns
- Easy to understand and modify
- Changes in one layer don't affect others

### ✅ Scalability
- Add new providers without changing core
- Add new features as plugins
- Horizontal scaling ready

### ✅ Flexibility
- Swap providers at runtime
- Use multiple providers simultaneously
- Configure everything without code changes

### ✅ Reusability
- Share AI capabilities across services
- Build once, use everywhere
- Create marketplace of feature plugins

---

## 🚀 Next Steps

1. **Implement Core Package** - `ai-core` with interfaces and engine
2. **Implement Provider Adapters** - OpenAI, Claude providers
3. **Implement Feature Plugins** - Product description, review response, social calendar
4. **Create Integration Libraries** - FastAPI, Flask middleware
5. **Build Example Services** - Show how to integrate
6. **Package & Distribute** - Publish to PyPI for easy installation

---

**This modular architecture allows:**
- Drop AI capabilities into ANY service in minutes
- Swap providers without code changes
- Scale horizontally across multiple services
- Test everything in isolation
- Build a marketplace of AI features

**Installation will be as simple as:**
```bash
pip install ai-platform-core
pip install ai-platform-openai
pip install ai-feature-product-description
```

**Usage will be as simple as:**
```python
from ai_platform import AIEngine, OpenAIProvider, ProductDescriptionPlugin

engine = AIEngine(OpenAIProvider())
plugin = ProductDescriptionPlugin(engine)
result = await plugin.generate(product_data)
```

Ready to implement this modular architecture! 🎯
