# OpenAI Provider

OpenAI GPT provider implementation for AI Platform.

## Installation

```bash
pip install openai tiktoken
```

## Usage

### Basic Usage

```python
from ai_providers.openai import OpenAIProvider
from ai_core import AIEngine, AIRequest

# Initialize provider
provider = OpenAIProvider(api_key="sk-...")

# Create engine
engine = AIEngine(provider=provider)

# Generate
request = AIRequest(
    prompt="Write a product description for organic tea",
    model="gpt-4",
    temperature=0.7
)

response = await engine.generate(request)
print(response.content)
```

### With Configuration

```python
from ai_providers.openai import OpenAIProvider, OpenAIConfig

config = OpenAIConfig(
    api_key="sk-...",
    default_model="gpt-4-turbo",
    organization="org-...",
    timeout=60
)

provider = OpenAIProvider(
    api_key=config.api_key,
    organization=config.organization
)
```

### JSON Mode

```python
request = AIRequest(
    prompt="Generate product data for organic tea",
    model="gpt-4",
    response_format="json",  # Enable JSON mode
    system_prompt="You are a helpful assistant that outputs JSON"
)

response = await engine.generate(request)
# response.content will be valid JSON
```

## Supported Models

- `gpt-4` - Most capable model
- `gpt-4-turbo` - Faster and cheaper GPT-4
- `gpt-3.5-turbo` - Fast and cheap
- `gpt-3.5-turbo-16k` - Larger context window

## Features

- ✅ JSON mode support
- ✅ Function calling
- ✅ Vision support (GPT-4V)
- ✅ Streaming (future)
- ✅ Accurate token counting (tiktoken)
- ✅ Retry logic
- ✅ Error handling

## Pricing (per 1K tokens)

- GPT-4: $0.03
- GPT-4 Turbo: $0.01
- GPT-3.5 Turbo: $0.001

## Environment Variables

You can also configure via environment variables:

```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_ORG_ID="org-..."
```

```python
import os
provider = OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
```

## Error Handling

```python
try:
    response = await engine.generate(request)
except Exception as e:
    print(f"Generation failed: {e}")
    # Handle error (retry, fallback, etc.)
```

## Token Estimation

```python
text = "Long product description..."
tokens = await provider.estimate_tokens(text)
print(f"Estimated tokens: {tokens}")

# Estimate cost
pricing = provider.get_pricing()
cost = (tokens / 1000) * pricing["gpt-4"]
print(f"Estimated cost: ${cost:.4f}")
```

## Health Check

```python
is_healthy = await provider.check_health()
if is_healthy:
    print("OpenAI API is accessible")
```

## Capabilities

```python
capabilities = provider.get_capabilities()
print(f"Supported models: {capabilities['models']}")
print(f"Max tokens: {capabilities['max_tokens']}")
print(f"Supports JSON mode: {capabilities['supports_json_mode']}")
```
