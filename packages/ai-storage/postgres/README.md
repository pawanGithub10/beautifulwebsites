# PostgreSQL Token Tracker

Production PostgreSQL token usage tracking for AI Platform.

## Installation

```bash
pip install asyncpg sqlalchemy[asyncio]
```

## Database Setup

### 1. Create Database

```sql
CREATE DATABASE ai_platform;
```

### 2. Run Schema

```python
from ai_storage.postgres.schema import init_database

await init_database("postgresql://localhost/ai_platform")
```

Or use the SQL directly:

```sql
-- See schema.py for complete SQL
```

## Usage

### Basic Usage

```python
from ai_storage.postgres import PostgresTokenTracker
from ai_core import AIEngine, PromptContext
from ai_providers.openai import OpenAIProvider

# Initialize tracker
tracker = PostgresTokenTracker(
    db_url="postgresql+asyncpg://user:pass@localhost/ai_platform"
)

# Use with AIEngine
provider = OpenAIProvider(api_key="sk-...")
engine = AIEngine(
    provider=provider,
    token_tracker=tracker
)

# Generate with automatic tracking
context = PromptContext(
    variables={},
    site_id="site-123",
    feature="product_description"
)

response = await engine.generate(request, context)
# Usage automatically tracked in database!
```

### Get Usage Statistics

```python
# Get monthly usage
stats = await tracker.get_usage(
    site_id="site-123",
    period="month"
)

print(f"Total tokens: {stats['total_tokens']}")
print(f"Total cost: ${stats['total_cost']:.2f}")
print(f"By feature: {stats['by_feature']}")
```

### Check Quota

```python
quota = await tracker.check_quota(site_id="site-123")

if not quota["within_quota"]:
    return {"error": "Token quota exceeded"}

print(f"Used: {quota['used']}/{quota['limit']} tokens")
print(f"Percentage: {quota['percentage']:.1f}%")
print(f"Remaining: {quota['remaining']} tokens")
```

### Monthly Reports

```python
report = await tracker.get_monthly_report(
    site_id="site-123",
    year=2025,
    month=1
)

print(f"Total cost: ${report['summary']['total_cost']:.2f}")
print(f"By feature: {report['by_feature']}")
print(f"By model: {report['by_model']}")
```

## Database Schema

### ai_token_usage Table

```sql
CREATE TABLE ai_token_usage (
    usage_id UUID PRIMARY KEY,
    site_id UUID NOT NULL,
    feature VARCHAR(50),
    model VARCHAR(50),
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    estimated_cost NUMERIC(10, 6),
    reference_type VARCHAR(50),
    reference_id UUID,
    created_at TIMESTAMPTZ,
    created_month VARCHAR(7)  -- YYYY-MM for fast queries
);

-- Indexes
CREATE INDEX idx_token_usage_site_month ON ai_token_usage(site_id, created_month);
CREATE INDEX idx_token_usage_feature ON ai_token_usage(feature);
```

### site_quotas Table

```sql
CREATE TABLE site_quotas (
    quota_id UUID PRIMARY KEY,
    site_id UUID UNIQUE,
    monthly_token_limit INTEGER,
    tier VARCHAR(20),  -- free, starter, professional, enterprise
    is_active BOOLEAN,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
```

## Quota Tiers

### Configure Quotas

```python
# Insert quota for a site
# INSERT INTO site_quotas (site_id, monthly_token_limit, tier)
# VALUES ('site-123', 100000, 'starter');

# Tiers:
# - free: 10,000 tokens/month
# - starter: 100,000 tokens/month
# - professional: 500,000 tokens/month
# - enterprise: unlimited
```

## Analytics Queries

### Usage by Feature

```sql
SELECT
    feature,
    SUM(total_tokens) as tokens,
    SUM(estimated_cost) as cost,
    COUNT(*) as requests
FROM ai_token_usage
WHERE site_id = 'site-123'
  AND created_month = '2025-01'
GROUP BY feature
ORDER BY cost DESC;
```

### Daily Usage Trend

```sql
SELECT
    DATE(created_at) as date,
    SUM(total_tokens) as tokens,
    SUM(estimated_cost) as cost
FROM ai_token_usage
WHERE site_id = 'site-123'
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date;
```

### Top Sites by Usage

```sql
SELECT
    site_id,
    SUM(total_tokens) as tokens,
    SUM(estimated_cost) as cost
FROM ai_token_usage
WHERE created_month = '2025-01'
GROUP BY site_id
ORDER BY cost DESC
LIMIT 10;
```

## Monitoring & Alerts

### Check Sites Near Quota

```python
# Query to find sites near quota limit
# SELECT
#     sq.site_id,
#     sq.monthly_token_limit,
#     COALESCE(SUM(atu.total_tokens), 0) as used_tokens,
#     (COALESCE(SUM(atu.total_tokens), 0)::float / sq.monthly_token_limit * 100) as percentage
# FROM site_quotas sq
# LEFT JOIN ai_token_usage atu ON sq.site_id = atu.site_id
#     AND atu.created_month = '2025-01'
# GROUP BY sq.site_id, sq.monthly_token_limit
# HAVING (COALESCE(SUM(atu.total_tokens), 0)::float / sq.monthly_token_limit * 100) > 80
# ORDER BY percentage DESC;
```

## Performance

### Partitioning (for large scale)

```sql
-- Partition by month for better performance
CREATE TABLE ai_token_usage_2025_01 PARTITION OF ai_token_usage
FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE ai_token_usage_2025_02 PARTITION OF ai_token_usage
FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

### Indexes

Already included:
- `idx_token_usage_site_month` - Fast site + month queries
- `idx_token_usage_feature` - Fast feature breakdown
- `idx_token_usage_created` - Fast time-based queries

## Cleanup

```python
await tracker.close()
```

## Docker Deployment

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ai_platform
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```
