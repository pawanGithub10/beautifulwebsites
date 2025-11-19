# Redis Cache

Production-ready Redis cache implementation for AI Platform.

## Installation

```bash
pip install redis[hiredis]
```

## Usage

### Basic Usage

```python
from ai_storage.redis import RedisCache
from ai_core import AIEngine
from ai_providers.openai import OpenAIProvider

# Initialize cache
cache = RedisCache(url="redis://localhost:6379/0")

# Use with AIEngine
provider = OpenAIProvider(api_key="sk-...")
engine = AIEngine(provider=provider, cache=cache)

# Generate (first call hits API)
response = await engine.generate(request)

# Generate again (second call uses cache - instant!)
response = await engine.generate(request)
```

### Custom Configuration

```python
cache = RedisCache(
    url="redis://localhost:6379/0",
    prefix="myapp:",  # Custom prefix for keys
    decode_responses=True
)
```

### Direct Cache Operations

```python
# Set with TTL
from datetime import timedelta

await cache.set(
    "product:123",
    {"name": "Tea", "price": 299},
    ttl=timedelta(hours=1)
)

# Get
product = await cache.get("product:123")

# Delete
await cache.delete("product:123")

# Clear by pattern
await cache.clear("product:*")

# Counter operations
count = await cache.increment("api:calls", amount=1)
```

## Features

- ✅ Async/await support
- ✅ Automatic JSON serialization
- ✅ TTL support
- ✅ Pattern-based deletion
- ✅ Connection pooling
- ✅ Namespace prefixing
- ✅ Counter operations

## Configuration

### Connection URL Format

```
redis://[:password@]host[:port][/database]
```

Examples:
```python
# Local
cache = RedisCache(url="redis://localhost:6379/0")

# With password
cache = RedisCache(url="redis://:password@localhost:6379/0")

# Remote
cache = RedisCache(url="redis://redis.example.com:6379/0")

# Redis Cloud
cache = RedisCache(url="redis://:password@redis-12345.cloud.redislabs.com:12345")
```

### Environment Variables

```bash
export REDIS_URL="redis://localhost:6379/0"
```

```python
import os
cache = RedisCache(url=os.getenv("REDIS_URL"))
```

## Performance

### Cache Hit Rates

With proper caching:
- 30-50% cost reduction
- 10-100x faster responses
- Reduced API rate limiting

### Benchmarks

```python
# Without cache
response = await engine.generate(request)  # 1-2 seconds, $0.03

# With cache (cache hit)
response = await engine.generate(request)  # <10ms, $0.00
```

## Best Practices

### Set Appropriate TTLs

```python
# Short-lived (minutes)
await cache.set("session:token", value, ttl=timedelta(minutes=15))

# Medium-lived (hours)
await cache.set("ai:response", value, ttl=timedelta(hours=24))

# Long-lived (days)
await cache.set("ai:template", value, ttl=timedelta(days=7))
```

### Use Namespacing

```python
# Separate by feature
product_cache = RedisCache(prefix="ai:product:")
review_cache = RedisCache(prefix="ai:review:")
social_cache = RedisCache(prefix="ai:social:")
```

### Handle Cache Failures Gracefully

```python
try:
    cached = await cache.get("key")
    if cached:
        return cached
except:
    # Cache failed, generate fresh
    pass

# Proceed with generation
response = await engine.generate(request)
```

## Monitoring

### Cache Stats

```python
# Monitor in production
info = await cache.redis.info("stats")
hits = info["keyspace_hits"]
misses = info["keyspace_misses"]
hit_rate = hits / (hits + misses) * 100

print(f"Cache hit rate: {hit_rate:.2f}%")
```

## Docker Deployment

```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

## Cleanup

```python
# Close connection when done
await cache.close()
```
