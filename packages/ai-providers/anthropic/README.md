# Anthropic Claude Provider

Anthropic Claude provider implementation for AI Platform.

## Installation

```bash
pip install anthropic
```

## Usage

### Basic Usage

```python
from ai_providers.anthropic import ClaudeProvider
from ai_core import AIEngine, AIRequest

# Initialize provider
provider = ClaudeProvider(api_key="sk-ant-...")

# Create engine
engine = AIEngine(provider=provider)

# Generate
request = AIRequest(
    prompt="Write a product description for organic tea",
    model="claude-3-sonnet-20240229",
    temperature=0.7
)

response = await engine.generate(request)
print(response.content)
```

### With Configuration

```python
from ai_providers.anthropic import ClaudeProvider, ClaudeConfig

config = ClaudeConfig(
    api_key="sk-ant-...",
    default_model="claude-3-opus-20240229",
    timeout=60
)

provider = ClaudeProvider(api_key=config.api_key)
```

### Model Aliases

```python
from ai_providers.anthropic import DEFAULT_MODELS

# Use convenience aliases
request = AIRequest(
    prompt="...",
    model=DEFAULT_MODELS["quality"]  # claude-3-opus
)
```

## Supported Models

- **Claude 3 Opus** - Most capable model, best for complex tasks
- **Claude 3 Sonnet** - Balanced performance and cost
- **Claude 3 Haiku** - Fastest and most affordable

All models support 200K token context window!

## Features

- ✅ 200K token context window
- ✅ Vision support (all Claude 3 models)
- ✅ Function calling
- ✅ Streaming (future)
- ✅ Long-form content generation
- ✅ Error handling and retries

## Pricing (per 1K tokens - INPUT)

- Claude 3 Opus: $0.015
- Claude 3 Sonnet: $0.003
- Claude 3 Haiku: $0.00025

Note: Output tokens are 3x the input price.

## Environment Variables

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

```python
import os
provider = ClaudeProvider(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

## Comparison with OpenAI

| Feature | Claude 3 | GPT-4 |
|---------|----------|-------|
| Context Window | 200K | 128K (turbo) |
| Vision Support | ✅ All models | ✅ GPT-4V |
| JSON Mode | ❌ | ✅ |
| Price (Quality) | $0.015 | $0.03 |
| Price (Fast) | $0.00025 | $0.001 |

## Best Practices

### For Long Documents

Claude excels at long-form content with its 200K context:

```python
request = AIRequest(
    prompt=f"Analyze this document: {long_document}",
    model="claude-3-opus-20240229",
    max_tokens=4000  # Claude can output longer responses
)
```

### For Cost Optimization

Use Haiku for simple tasks:

```python
request = AIRequest(
    prompt="Summarize this review",
    model="claude-3-haiku-20240307",  # 100x cheaper than Opus!
    temperature=0.3
)
```

### For Complex Reasoning

Use Opus for complex tasks:

```python
request = AIRequest(
    prompt="Analyze this complex business scenario...",
    model="claude-3-opus-20240229",
    temperature=0.5
)
```

## Error Handling

```python
try:
    response = await engine.generate(request)
except Exception as e:
    print(f"Generation failed: {e}")
    # Handle error (retry, fallback to GPT, etc.)
```

## Multi-Provider Fallback

```python
from ai_providers.openai import OpenAIProvider
from ai_providers.anthropic import ClaudeProvider

# Try Claude first, fallback to OpenAI
claude = ClaudeProvider(api_key="...")
openai = OpenAIProvider(api_key="...")

try:
    engine = AIEngine(provider=claude)
    response = await engine.generate(request)
except:
    engine = AIEngine(provider=openai)
    response = await engine.generate(request)
```
