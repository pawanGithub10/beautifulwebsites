# AI-Powered Features Architecture

**Version:** 1.0
**Date:** January 2025
**Status:** Design Phase

## Overview

This document outlines the architecture for three AI-powered microsaas features integrated into the Beautiful Websites platform:

1. **AI Product Description Generator** - Integrated with Storefront Service
2. **AI Customer Review Responder** - New Review Service
3. **AI Social Media Content Calendar** - Integrated with Content Service

## Design Principles

- **Modular**: Each AI feature is self-contained with clear boundaries
- **Scalable**: Supports async processing and queue-based operations
- **Extensible**: Easy to add new AI capabilities and prompts
- **Multi-tenant**: Complete site-level isolation
- **Cost-effective**: Token usage tracking and caching

---

## 🛍️ Feature 1: AI Product Description Generator

### Problem Statement
E-commerce stores need unique, SEO-optimized product descriptions for thousands of products. Writing manually is time-consuming and inconsistent.

### Solution
AI-powered description generator that creates compelling, SEO-friendly product descriptions from basic product attributes.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     STOREFRONT SERVICE (8011)                       │
│                                                                     │
│  ┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐  │
│  │   Products   │    │  AI Description  │    │   AI Prompts    │  │
│  │   Router     │───▶│     Router       │───▶│    Service      │  │
│  │              │    │                  │    │                 │  │
│  │ POST /api/v1/│    │ POST /generate   │    │ • Generate      │  │
│  │ catalog/{id}/│    │ POST /batch      │    │ • Validate      │  │
│  │ products     │    │ GET  /history    │    │ • Save          │  │
│  └──────┬───────┘    └────────┬─────────┘    └────────┬────────┘  │
│         │                     │                       │            │
│         │                     │                       │            │
│  ┌──────▼─────────────────────▼───────────────────────▼─────────┐  │
│  │                   Product Service                            │  │
│  │  • Create product with AI-generated description             │  │
│  │  • Regenerate description                                   │  │
│  │  • A/B test descriptions                                    │  │
│  └────────┬──────────────────────────────────┬─────────────────┘  │
└───────────┼──────────────────────────────────┼────────────────────┘
            │                                  │
            │                                  │
    ┌───────▼────────┐              ┌─────────▼──────────┐
    │   PostgreSQL   │              │   LLM Gateway      │
    │   (store_db)   │              │   (Port 8004)      │
    │                │              │                    │
    │ • products     │              │ • GPT-4 API        │
    │ • ai_generated │              │ • Claude API       │
    │   _descriptions│              │ • Prompt templates │
    │ • prompt_      │              │ • Token tracking   │
    │   templates    │              │ • Response cache   │
    └────────────────┘              └────────────────────┘
```

### Database Schema

```sql
-- New table: AI-generated descriptions tracking
CREATE TABLE ai_generated_descriptions (
    description_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL,
    product_id UUID NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,

    -- AI Generation metadata
    prompt_template_id UUID REFERENCES ai_prompt_templates(template_id),
    model_used VARCHAR(50) NOT NULL,  -- gpt-4, claude-3, etc.

    -- Generated content
    generated_description TEXT NOT NULL,
    short_description VARCHAR(500),
    meta_title VARCHAR(200),
    meta_description TEXT,
    tags TEXT[],

    -- Input data snapshot
    input_data JSONB NOT NULL,  -- Product attributes used

    -- Performance metrics
    tokens_used INTEGER,
    generation_time_ms INTEGER,

    -- Status
    status VARCHAR(20) DEFAULT 'generated',  -- generated, approved, rejected, active

    -- A/B testing
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT false,

    -- Performance tracking
    views INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    conversion_rate DECIMAL(5,2),

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by_user_id UUID,
    activated_at TIMESTAMPTZ,

    CONSTRAINT idx_ai_desc_site_product UNIQUE(site_id, product_id, version)
);

CREATE INDEX idx_ai_desc_product ON ai_generated_descriptions(product_id);
CREATE INDEX idx_ai_desc_status ON ai_generated_descriptions(status);
CREATE INDEX idx_ai_desc_active ON ai_generated_descriptions(is_active);


-- AI Prompt Templates
CREATE TABLE ai_prompt_templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID,  -- NULL for global templates

    -- Template info
    template_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,  -- product_description, social_post, review_response

    -- Prompt
    prompt_text TEXT NOT NULL,
    system_prompt TEXT,

    -- Configuration
    model VARCHAR(50) DEFAULT 'gpt-4',
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 500,

    -- Variables
    variables JSONB,  -- {product_name, category, price, attributes...}

    -- Status
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false,

    -- Performance
    usage_count INTEGER DEFAULT 0,
    avg_rating DECIMAL(3,2),

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ,
    created_by_user_id UUID
);

CREATE INDEX idx_prompt_template_category ON ai_prompt_templates(category);
CREATE INDEX idx_prompt_template_site ON ai_prompt_templates(site_id);


-- Token usage tracking for billing
CREATE TABLE ai_token_usage (
    usage_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL,

    -- Usage metadata
    feature VARCHAR(50) NOT NULL,  -- product_description, review_response, social_calendar
    model VARCHAR(50) NOT NULL,

    -- Token counts
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    total_tokens INTEGER NOT NULL,

    -- Cost (for billing)
    estimated_cost DECIMAL(10,6),

    -- Reference
    reference_type VARCHAR(50),  -- product, review, post
    reference_id UUID,

    -- Timestamp
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_month VARCHAR(7) GENERATED ALWAYS AS (TO_CHAR(created_at, 'YYYY-MM')) STORED
);

CREATE INDEX idx_token_usage_site_month ON ai_token_usage(site_id, created_month);
CREATE INDEX idx_token_usage_feature ON ai_token_usage(feature);
```

### API Endpoints

```yaml
# Generate description for new product
POST /api/v1/catalog/{site_id}/products/{product_id}/ai-description
Request:
  {
    "product_attributes": {
      "name": "Organic Green Tea",
      "category": "Beverages",
      "price": 299,
      "weight": "100g",
      "features": ["organic", "antioxidant-rich", "imported"],
      "target_audience": "health-conscious"
    },
    "template_id": "uuid",  # Optional, uses default if not provided
    "tone": "professional",  # professional, casual, luxury, playful
    "length": "medium",  # short, medium, long
    "include_seo": true
  }
Response:
  {
    "description_id": "uuid",
    "generated_description": "Discover the pure essence of nature...",
    "short_description": "Premium organic green tea...",
    "meta_title": "Organic Green Tea 100g - Antioxidant Rich | YourStore",
    "meta_description": "Buy premium organic green tea...",
    "tags": ["organic", "green tea", "health", "antioxidants"],
    "tokens_used": 450,
    "generation_time_ms": 1200,
    "status": "generated"
  }

# Batch generate descriptions
POST /api/v1/catalog/{site_id}/ai-descriptions/batch
Request:
  {
    "product_ids": ["uuid1", "uuid2", "uuid3"],
    "template_id": "uuid",
    "auto_activate": false
  }
Response:
  {
    "job_id": "uuid",
    "total_products": 3,
    "status": "processing",
    "estimated_time_seconds": 15
  }

# Get batch job status
GET /api/v1/catalog/{site_id}/ai-descriptions/batch/{job_id}
Response:
  {
    "job_id": "uuid",
    "status": "completed",  # processing, completed, failed
    "total": 3,
    "completed": 3,
    "failed": 0,
    "results": [
      {"product_id": "uuid1", "description_id": "uuid", "status": "success"},
      {"product_id": "uuid2", "description_id": "uuid", "status": "success"},
      {"product_id": "uuid3", "description_id": "uuid", "status": "success"}
    ]
  }

# List all AI-generated descriptions for a product (A/B testing)
GET /api/v1/catalog/{site_id}/products/{product_id}/ai-descriptions
Response:
  {
    "product_id": "uuid",
    "descriptions": [
      {
        "description_id": "uuid",
        "version": 1,
        "is_active": true,
        "generated_description": "...",
        "views": 1250,
        "conversions": 42,
        "conversion_rate": 3.36,
        "created_at": "2025-01-15T10:00:00Z"
      },
      {
        "description_id": "uuid",
        "version": 2,
        "is_active": false,
        "generated_description": "...",
        "views": 0,
        "conversions": 0,
        "conversion_rate": 0,
        "created_at": "2025-01-16T14:30:00Z"
      }
    ]
  }

# Activate a specific description version
PUT /api/v1/catalog/{site_id}/products/{product_id}/ai-descriptions/{description_id}/activate
Response:
  {
    "message": "Description activated successfully",
    "description_id": "uuid",
    "product_updated": true
  }

# Get token usage statistics
GET /api/v1/catalog/{site_id}/ai-token-usage?month=2025-01
Response:
  {
    "site_id": "uuid",
    "month": "2025-01",
    "by_feature": {
      "product_description": {
        "total_tokens": 125000,
        "estimated_cost": 2.50,
        "requests": 250
      }
    },
    "total_tokens": 125000,
    "total_cost": 2.50
  }
```

### Prompt Templates

```python
# Default product description prompt
PRODUCT_DESCRIPTION_PROMPT = """
You are an expert e-commerce copywriter. Generate a compelling product description.

Product Information:
- Name: {product_name}
- Category: {category}
- Price: {price} {currency}
- Key Features: {features}
- Target Audience: {target_audience}

Requirements:
1. Tone: {tone}
2. Length: {length} (short: 50-100 words, medium: 150-250 words, long: 300-500 words)
3. Include SEO keywords naturally
4. Highlight benefits, not just features
5. Create urgency or desire
6. End with a call-to-action

Output Format (JSON):
{
  "description": "Full product description",
  "short_description": "1-2 sentence summary",
  "meta_title": "SEO-optimized title (max 60 chars)",
  "meta_description": "SEO meta description (max 160 chars)",
  "tags": ["tag1", "tag2", "tag3"]
}
"""

# Category-specific prompts
GROCERY_PRODUCT_PROMPT = """
Focus on: Freshness, quality, health benefits, source/origin
"""

ELECTRONICS_PRODUCT_PROMPT = """
Focus on: Technical specs, compatibility, warranty, innovation
"""

FASHION_PRODUCT_PROMPT = """
Focus on: Style, material, fit, occasion, care instructions
"""
```

### Integration Flow

```
1. User creates product via API/UI
   └─▶ Product basic info saved to database

2. User requests AI description generation
   └─▶ Storefront Service validates request
       └─▶ Fetch prompt template
           └─▶ Build prompt with product attributes
               └─▶ Call LLM Gateway Service
                   └─▶ LLM Gateway calls OpenAI/Claude API
                       └─▶ Response received and parsed
                           └─▶ Save to ai_generated_descriptions table
                               └─▶ Track token usage
                                   └─▶ Return generated content to user

3. User reviews and activates description
   └─▶ Update product.description field
       └─▶ Set is_active = true for description
           └─▶ Track as A/B test variant

4. Analytics (background job)
   └─▶ Track product views and conversions
       └─▶ Calculate conversion rates per description
           └─▶ Auto-select best performing variant (optional)
```

---

## ⭐ Feature 2: AI Customer Review Responder

### Problem Statement
Businesses receive hundreds of reviews across multiple platforms (Google, Yelp, Facebook). Responding personally to each is time-consuming but crucial for reputation.

### Solution
AI-powered review response generator that creates personalized, empathetic responses based on review sentiment and content.

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                      REVIEW SERVICE (Port 8016)                      │
│                                                                      │
│  ┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐   │
│  │   Review     │    │  AI Response     │    │   Sentiment     │   │
│  │   Router     │───▶│    Generator     │───▶│    Analysis     │   │
│  │              │    │                  │    │                 │   │
│  │ POST /reviews│    │ • Generate       │    │ • Positive      │   │
│  │ POST /respond│    │ • Customize      │    │ • Neutral       │   │
│  │ GET  /pending│    │ • Approve        │    │ • Negative      │   │
│  └──────┬───────┘    └────────┬─────────┘    └────────┬────────┘   │
│         │                     │                       │             │
│         │                     │                       │             │
│  ┌──────▼─────────────────────▼───────────────────────▼──────────┐  │
│  │                   Review Service                              │  │
│  │  • Ingest reviews from platforms                             │  │
│  │  • Generate AI responses                                     │  │
│  │  • Approval workflow                                         │  │
│  │  • Auto-post responses                                       │  │
│  └────────┬──────────────────────────────────┬──────────────────┘  │
└───────────┼──────────────────────────────────┼─────────────────────┘
            │                                  │
            │                                  │
    ┌───────▼────────┐              ┌─────────▼──────────┐
    │   PostgreSQL   │              │   LLM Gateway      │
    │  (review_db)   │              │   (Port 8004)      │
    │                │              │                    │
    │ • reviews      │              │ • Sentiment API    │
    │ • ai_responses │              │ • Response gen     │
    │ • platforms    │              │ • Tone matching    │
    │ • webhooks     │              └────────┬───────────┘
    └────────┬───────┘                       │
             │                               │
             │          ┌────────────────────▼────────┐
             │          │  External Review Platforms  │
             └─────────▶│                             │
                        │  • Google My Business API   │
                        │  • Yelp Fusion API          │
                        │  • Facebook Graph API       │
                        │  • Trustpilot API           │
                        └─────────────────────────────┘
```

### Database Schema

```sql
-- Review platforms configuration
CREATE TABLE review_platforms (
    platform_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL,

    -- Platform info
    platform_name VARCHAR(50) NOT NULL,  -- google, yelp, facebook, trustpilot
    platform_account_id VARCHAR(255),

    -- API credentials (encrypted)
    api_credentials JSONB NOT NULL,  -- Encrypted API keys/tokens

    -- Settings
    is_active BOOLEAN DEFAULT true,
    auto_import BOOLEAN DEFAULT true,
    auto_respond BOOLEAN DEFAULT false,  -- Dangerous! Needs approval

    -- Webhook
    webhook_url VARCHAR(500),
    webhook_secret VARCHAR(255),

    -- Sync status
    last_sync_at TIMESTAMPTZ,
    next_sync_at TIMESTAMPTZ,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX idx_platform_site ON review_platforms(site_id);


-- Customer reviews
CREATE TABLE customer_reviews (
    review_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL,
    platform_id UUID REFERENCES review_platforms(platform_id),

    -- Review metadata
    external_review_id VARCHAR(255),  -- ID from platform
    platform_url VARCHAR(500),  -- Direct link to review

    -- Reviewer info
    reviewer_name VARCHAR(200),
    reviewer_email VARCHAR(255),
    reviewer_id VARCHAR(255),  -- Platform-specific

    -- Review content
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_title VARCHAR(300),
    review_text TEXT NOT NULL,
    review_images TEXT[],  -- URLs to images

    -- Sentiment analysis
    sentiment VARCHAR(20),  -- positive, neutral, negative
    sentiment_score DECIMAL(3,2),  -- -1.00 to 1.00
    keywords TEXT[],

    -- Product/service reference
    product_id UUID,  -- If review is for specific product
    booking_id UUID,  -- If review is for booking
    order_id UUID,  -- If review is for order

    -- Status
    status VARCHAR(20) DEFAULT 'pending',  -- pending, responded, archived
    is_featured BOOLEAN DEFAULT false,
    is_visible BOOLEAN DEFAULT true,

    -- Response tracking
    has_response BOOLEAN DEFAULT false,
    ai_response_generated BOOLEAN DEFAULT false,

    -- Timestamps
    reviewed_at TIMESTAMPTZ NOT NULL,
    imported_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT idx_review_external UNIQUE(platform_id, external_review_id)
);

CREATE INDEX idx_review_site_status ON customer_reviews(site_id, status);
CREATE INDEX idx_review_rating ON customer_reviews(rating);
CREATE INDEX idx_review_sentiment ON customer_reviews(sentiment);
CREATE INDEX idx_review_reviewed_at ON customer_reviews(reviewed_at DESC);


-- AI-generated review responses
CREATE TABLE ai_review_responses (
    response_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL REFERENCES customer_reviews(review_id) ON DELETE CASCADE,
    site_id UUID NOT NULL,

    -- AI generation
    prompt_template_id UUID REFERENCES ai_prompt_templates(template_id),
    model_used VARCHAR(50) NOT NULL,

    -- Generated response
    response_text TEXT NOT NULL,
    tone VARCHAR(50),  -- professional, friendly, apologetic, grateful

    -- Customization
    is_customized BOOLEAN DEFAULT false,
    customized_text TEXT,  -- If user edited the response

    -- Status
    status VARCHAR(20) DEFAULT 'draft',  -- draft, approved, posted, rejected

    -- Performance
    tokens_used INTEGER,
    generation_time_ms INTEGER,

    -- Approval workflow
    approved_by_user_id UUID,
    approved_at TIMESTAMPTZ,
    posted_at TIMESTAMPTZ,

    -- Platform posting
    posted_to_platform BOOLEAN DEFAULT false,
    platform_response_id VARCHAR(255),
    posting_error TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX idx_ai_response_review ON ai_review_responses(review_id);
CREATE INDEX idx_ai_response_status ON ai_review_responses(status);


-- Review analytics
CREATE TABLE review_analytics (
    analytics_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL,

    -- Time period
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    period_type VARCHAR(20) NOT NULL,  -- day, week, month

    -- Metrics
    total_reviews INTEGER DEFAULT 0,
    avg_rating DECIMAL(3,2),

    -- By rating
    rating_5_count INTEGER DEFAULT 0,
    rating_4_count INTEGER DEFAULT 0,
    rating_3_count INTEGER DEFAULT 0,
    rating_2_count INTEGER DEFAULT 0,
    rating_1_count INTEGER DEFAULT 0,

    -- By sentiment
    positive_count INTEGER DEFAULT 0,
    neutral_count INTEGER DEFAULT 0,
    negative_count INTEGER DEFAULT 0,

    -- Response metrics
    responded_count INTEGER DEFAULT 0,
    response_rate DECIMAL(5,2),
    avg_response_time_hours DECIMAL(10,2),

    -- AI metrics
    ai_generated_count INTEGER DEFAULT 0,
    ai_customized_count INTEGER DEFAULT 0,
    ai_acceptance_rate DECIMAL(5,2),

    -- Audit
    calculated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT idx_analytics_site_period UNIQUE(site_id, period_start, period_type)
);

CREATE INDEX idx_analytics_site_date ON review_analytics(site_id, period_start DESC);
```

### API Endpoints

```yaml
# Ingest review (webhook or manual)
POST /api/v1/{site_id}/reviews
Request:
  {
    "platform": "google",
    "external_review_id": "ChZDSUhNMG9nS0VJQ0FnSUQ3",
    "reviewer_name": "Sarah Johnson",
    "rating": 5,
    "review_text": "Amazing service! The staff was incredibly helpful...",
    "reviewed_at": "2025-01-15T10:30:00Z"
  }
Response:
  {
    "review_id": "uuid",
    "sentiment": "positive",
    "sentiment_score": 0.92,
    "keywords": ["amazing", "helpful", "service"],
    "ai_response_ready": true
  }

# Generate AI response for review
POST /api/v1/{site_id}/reviews/{review_id}/generate-response
Request:
  {
    "tone": "grateful",  # grateful, professional, apologetic
    "include_details": {
      "business_name": "Green Valley Salon",
      "owner_name": "Maria",
      "specific_mention": "haircut service"  # Extracted from review
    },
    "template_id": "uuid"  # Optional
  }
Response:
  {
    "response_id": "uuid",
    "response_text": "Thank you so much, Sarah! We're thrilled to hear...",
    "tone": "grateful",
    "tokens_used": 180,
    "status": "draft"
  }

# Batch generate responses for pending reviews
POST /api/v1/{site_id}/reviews/batch-generate
Request:
  {
    "rating_filter": [4, 5],  # Only for 4-5 star reviews
    "sentiment_filter": ["positive", "neutral"],
    "auto_approve": false,
    "limit": 50
  }
Response:
  {
    "job_id": "uuid",
    "total_reviews": 23,
    "status": "processing"
  }

# Approve and post response
PUT /api/v1/{site_id}/reviews/{review_id}/responses/{response_id}/approve
Request:
  {
    "customized_text": "Optional edited response...",
    "post_to_platform": true
  }
Response:
  {
    "message": "Response approved and posted",
    "response_id": "uuid",
    "posted_to_platform": true,
    "platform_response_id": "xyz123"
  }

# Get pending reviews needing responses
GET /api/v1/{site_id}/reviews/pending?sentiment=negative&limit=20
Response:
  {
    "total": 5,
    "reviews": [
      {
        "review_id": "uuid",
        "reviewer_name": "John Doe",
        "rating": 2,
        "review_text": "Service was slow and food was cold...",
        "sentiment": "negative",
        "reviewed_at": "2025-01-15T14:20:00Z",
        "has_ai_response": true,
        "ai_response_preview": "We sincerely apologize for your experience..."
      }
    ]
  }

# Get review analytics
GET /api/v1/{site_id}/reviews/analytics?period=month&start=2025-01-01
Response:
  {
    "period": "2025-01",
    "total_reviews": 156,
    "avg_rating": 4.3,
    "rating_distribution": {
      "5": 89,
      "4": 42,
      "3": 15,
      "2": 7,
      "1": 3
    },
    "sentiment_distribution": {
      "positive": 131,
      "neutral": 15,
      "negative": 10
    },
    "response_stats": {
      "total_responded": 142,
      "response_rate": 91.03,
      "avg_response_time_hours": 4.5,
      "ai_generated": 138,
      "ai_acceptance_rate": 94.52
    }
  }

# Platform integration endpoints
POST /api/v1/{site_id}/review-platforms
Request:
  {
    "platform_name": "google",
    "platform_account_id": "ChIJ...",
    "api_credentials": {
      "api_key": "encrypted_key",
      "location_id": "12345"
    },
    "auto_import": true,
    "auto_respond": false
  }

GET /api/v1/{site_id}/review-platforms/{platform_id}/sync
# Manually trigger review sync from platform
```

### Prompt Templates

```python
# Positive review response
POSITIVE_REVIEW_RESPONSE = """
Generate a warm, grateful response to this positive review.

Review Details:
- Rating: {rating}/5
- Reviewer: {reviewer_name}
- Review: "{review_text}"
- Keywords: {keywords}

Business Context:
- Business Name: {business_name}
- Owner/Manager: {owner_name}
- Specific Service/Product Mentioned: {specific_mention}

Guidelines:
1. Express genuine gratitude
2. Mention specific details from their review
3. Reinforce what they loved
4. Invite them back
5. Keep it personal but professional
6. Max 100 words

Tone: {tone}
"""

# Negative review response
NEGATIVE_REVIEW_RESPONSE = """
Generate an empathetic, solution-focused response to this negative review.

Review Details:
- Rating: {rating}/5
- Reviewer: {reviewer_name}
- Review: "{review_text}"
- Issues Mentioned: {issues}

Business Context:
- Business Name: {business_name}
- Owner/Manager: {owner_name}

Guidelines:
1. Acknowledge their frustration
2. Apologize sincerely (without over-apologizing)
3. Address specific issues they mentioned
4. Offer a solution or next steps
5. Provide contact info for follow-up
6. Keep it professional and caring
7. Max 150 words

Tone: apologetic but solution-oriented
"""
```

---

## 📱 Feature 3: AI Social Media Content Calendar

### Problem Statement
Businesses struggle to maintain consistent social media presence. Creating engaging content daily is time-consuming and requires creativity.

### Solution
AI-powered content calendar that generates a month's worth of social media posts tailored to the business, with variations for different platforms.

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                     CONTENT SERVICE (Port 8014)                      │
│                                                                      │
│  ┌──────────────┐    ┌──────────────────┐    ┌─────────────────┐   │
│  │   Social     │    │  AI Calendar     │    │   Post          │   │
│  │   Router     │───▶│    Generator     │───▶│   Scheduler     │   │
│  │              │    │                  │    │                 │   │
│  │ POST /calendar│   │ • Generate       │    │ • Schedule      │   │
│  │ GET  /posts   │   │ • Customize      │    │ • Auto-post     │   │
│  │ PUT  /schedule│   │ • Variations     │    │ • Track perf    │   │
│  └──────┬───────┘    └────────┬─────────┘    └────────┬────────┘   │
│         │                     │                       │             │
│         │                     │                       │             │
│  ┌──────▼─────────────────────▼───────────────────────▼──────────┐  │
│  │                   Social Media Service                        │  │
│  │  • Generate content calendar                                 │  │
│  │  • Create platform variations                                │  │
│  │  • Schedule posts                                            │  │
│  │  • Auto-publish via APIs                                     │  │
│  └────────┬──────────────────────────────────┬──────────────────┘  │
└───────────┼──────────────────────────────────┼─────────────────────┘
            │                                  │
            │                                  │
    ┌───────▼────────┐              ┌─────────▼──────────┐
    │   PostgreSQL   │              │   LLM Gateway      │
    │ (content_db)   │              │   (Port 8004)      │
    │                │              │                    │
    │ • social_posts │              │ • Content gen      │
    │ • calendars    │              │ • Image prompts    │
    │ • platforms    │              │ • Hashtags         │
    │ • performance  │              └────────┬───────────┘
    └────────┬───────┘                       │
             │                               │
             │          ┌────────────────────▼────────┐
             │          │    Social Media Platforms   │
             └─────────▶│                             │
                        │  • Facebook Graph API       │
                        │  • Instagram Graph API      │
                        │  • Twitter/X API            │
                        │  • LinkedIn API             │
                        └─────────────────────────────┘
```

### Database Schema

```sql
-- Social media accounts
CREATE TABLE social_media_accounts (
    account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL,

    -- Platform info
    platform VARCHAR(50) NOT NULL,  -- facebook, instagram, twitter, linkedin
    account_name VARCHAR(200),
    account_handle VARCHAR(100),
    account_url VARCHAR(500),

    -- API credentials (encrypted)
    api_credentials JSONB NOT NULL,

    -- Settings
    is_active BOOLEAN DEFAULT true,
    auto_post BOOLEAN DEFAULT false,

    -- Platform-specific settings
    platform_settings JSONB,  -- max_length, image_required, hashtag_limit, etc.

    -- Status
    last_post_at TIMESTAMPTZ,
    connection_status VARCHAR(20) DEFAULT 'active',  -- active, expired, error

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX idx_social_account_site ON social_media_accounts(site_id);


-- Content calendars
CREATE TABLE content_calendars (
    calendar_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL,

    -- Calendar info
    calendar_name VARCHAR(200) NOT NULL,
    month VARCHAR(7) NOT NULL,  -- YYYY-MM

    -- AI generation metadata
    generated_by_ai BOOLEAN DEFAULT true,
    prompt_used TEXT,
    brand_voice TEXT,  -- Professional, casual, playful, educational

    -- Business context
    business_type VARCHAR(100),
    target_audience VARCHAR(200),
    key_themes TEXT[],
    products_to_promote JSONB,  -- Product IDs and details

    -- Status
    status VARCHAR(20) DEFAULT 'draft',  -- draft, approved, active, archived
    total_posts INTEGER DEFAULT 0,
    published_posts INTEGER DEFAULT 0,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by_user_id UUID,
    approved_at TIMESTAMPTZ,
    approved_by_user_id UUID
);

CREATE INDEX idx_calendar_site_month ON content_calendars(site_id, month);


-- Social media posts
CREATE TABLE social_media_posts (
    post_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL,
    calendar_id UUID REFERENCES content_calendars(calendar_id) ON DELETE SET NULL,

    -- Post content
    post_text TEXT NOT NULL,
    hashtags TEXT[],
    mentions TEXT[],

    -- Media
    image_urls TEXT[],
    video_url VARCHAR(500),
    image_prompts TEXT[],  -- AI prompts used to generate images

    -- Scheduling
    scheduled_date DATE NOT NULL,
    scheduled_time TIME,
    scheduled_at TIMESTAMPTZ GENERATED ALWAYS AS (
        (scheduled_date || ' ' || COALESCE(scheduled_time::TEXT, '12:00:00'))::TIMESTAMPTZ
    ) STORED,

    -- Platform-specific versions
    platform_variations JSONB,  -- {facebook: {...}, instagram: {...}}

    -- AI metadata
    generated_by_ai BOOLEAN DEFAULT true,
    prompt_template_id UUID,
    tokens_used INTEGER,

    -- Customization
    is_customized BOOLEAN DEFAULT false,
    original_text TEXT,  -- Original AI-generated text

    -- Publishing status
    status VARCHAR(20) DEFAULT 'scheduled',  -- draft, scheduled, published, failed

    -- Platform publishing
    published_to JSONB,  -- {facebook: {post_id, url, status}, instagram: {...}}

    -- Performance (synced from platforms)
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    engagement_rate DECIMAL(5,2),

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    published_at TIMESTAMPTZ,
    last_synced_at TIMESTAMPTZ
);

CREATE INDEX idx_post_site_scheduled ON social_media_posts(site_id, scheduled_at);
CREATE INDEX idx_post_calendar ON social_media_posts(calendar_id);
CREATE INDEX idx_post_status ON social_media_posts(status);


-- Post templates (for recurring content)
CREATE TABLE post_templates (
    template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID,  -- NULL for global templates

    -- Template info
    template_name VARCHAR(200) NOT NULL,
    category VARCHAR(50),  -- promotional, educational, engagement, testimonial

    -- Content template
    template_text TEXT NOT NULL,
    variables JSONB,  -- {product_name, offer, date, etc.}

    -- Settings
    suggested_hashtags TEXT[],
    suggested_time TIME,
    suggested_day_of_week INTEGER,  -- 0=Sunday, 1=Monday, etc.

    -- Media
    requires_image BOOLEAN DEFAULT false,
    image_style VARCHAR(100),  -- product_photo, lifestyle, infographic, quote

    -- Status
    is_active BOOLEAN DEFAULT true,
    usage_count INTEGER DEFAULT 0,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX idx_post_template_site ON post_templates(site_id);


-- Content performance analytics
CREATE TABLE social_media_analytics (
    analytics_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    site_id UUID NOT NULL,
    post_id UUID REFERENCES social_media_posts(post_id),

    -- Time period
    date DATE NOT NULL,

    -- Platform
    platform VARCHAR(50) NOT NULL,

    -- Engagement metrics
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    views INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,

    -- Calculated metrics
    engagement_rate DECIMAL(5,2),
    reach INTEGER DEFAULT 0,
    impressions INTEGER DEFAULT 0,

    -- Audit
    synced_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT idx_analytics_post_platform_date UNIQUE(post_id, platform, date)
);

CREATE INDEX idx_social_analytics_site_date ON social_media_analytics(site_id, date DESC);
```

### API Endpoints

```yaml
# Generate AI content calendar
POST /api/v1/{site_id}/social-media/calendars/generate
Request:
  {
    "month": "2025-02",
    "business_context": {
      "business_type": "salon",
      "brand_voice": "friendly and professional",
      "target_audience": "women 25-45",
      "key_themes": ["haircare tips", "seasonal trends", "promotions"],
      "posting_frequency": 5,  # posts per week
      "preferred_days": ["mon", "wed", "fri", "sat"],
      "preferred_times": ["10:00", "15:00", "18:00"]
    },
    "products_to_feature": [
      {
        "product_id": "uuid",
        "product_name": "Keratin Treatment",
        "promotion": "20% off in February"
      }
    ],
    "include_image_prompts": true
  }
Response:
  {
    "calendar_id": "uuid",
    "month": "2025-02",
    "total_posts": 20,
    "posts_preview": [
      {
        "date": "2025-02-01",
        "time": "10:00",
        "post_text": "Happy February! 💇‍♀️ Start the month with...",
        "hashtags": ["#HairGoals", "#SalonLife", "#February"],
        "image_prompt": "A modern salon interior with...",
        "category": "engagement"
      },
      {
        "date": "2025-02-03",
        "time": "15:00",
        "post_text": "Did you know? Keratin treatments can...",
        "hashtags": ["#HairCareTips", "#KeratinTreatment"],
        "image_prompt": "Before and after keratin treatment...",
        "category": "educational"
      }
    ],
    "tokens_used": 2450,
    "status": "draft"
  }

# Get calendar details
GET /api/v1/{site_id}/social-media/calendars/{calendar_id}
Response:
  {
    "calendar_id": "uuid",
    "month": "2025-02",
    "status": "approved",
    "total_posts": 20,
    "published_posts": 5,
    "scheduled_posts": 15,
    "posts": [...]  # Full list of posts
  }

# Customize a specific post
PUT /api/v1/{site_id}/social-media/posts/{post_id}
Request:
  {
    "post_text": "Customized post text...",
    "hashtags": ["#Custom", "#Tags"],
    "scheduled_date": "2025-02-05",
    "scheduled_time": "16:00",
    "platform_variations": {
      "instagram": {
        "post_text": "Instagram-specific version...",
        "hashtags": ["#InstaBeauty", "#SalonVibes"]
      },
      "facebook": {
        "post_text": "Facebook-specific version..."
      }
    }
  }

# Approve and activate calendar
POST /api/v1/{site_id}/social-media/calendars/{calendar_id}/approve
Request:
  {
    "auto_publish": true,
    "platforms": ["facebook", "instagram"]
  }
Response:
  {
    "message": "Calendar approved and scheduled",
    "calendar_id": "uuid",
    "posts_scheduled": 20,
    "platforms": ["facebook", "instagram"]
  }

# Generate single post
POST /api/v1/{site_id}/social-media/posts/generate
Request:
  {
    "topic": "Valentine's Day special offer",
    "post_type": "promotional",
    "product_id": "uuid",
    "brand_voice": "romantic and exciting",
    "platforms": ["instagram", "facebook"],
    "include_image_prompt": true
  }
Response:
  {
    "post_id": "uuid",
    "post_text": "Love is in the air! 💕 This Valentine's Day...",
    "hashtags": ["#ValentinesDay", "#LoveYourHair"],
    "image_prompt": "Romantic salon setting with roses...",
    "platform_variations": {
      "instagram": {...},
      "facebook": {...}
    }
  }

# Get content performance
GET /api/v1/{site_id}/social-media/analytics?start=2025-01-01&end=2025-01-31
Response:
  {
    "period": {
      "start": "2025-01-01",
      "end": "2025-01-31"
    },
    "total_posts": 22,
    "by_platform": {
      "facebook": {
        "posts": 22,
        "total_likes": 1456,
        "total_comments": 234,
        "total_shares": 89,
        "avg_engagement_rate": 4.23
      },
      "instagram": {
        "posts": 22,
        "total_likes": 2341,
        "total_comments": 187,
        "total_shares": 45,
        "avg_engagement_rate": 6.12
      }
    },
    "best_performing_posts": [...]
  }

# Configure social media accounts
POST /api/v1/{site_id}/social-media/accounts
Request:
  {
    "platform": "instagram",
    "account_handle": "@greensalon",
    "api_credentials": {
      "access_token": "encrypted_token",
      "instagram_business_id": "12345"
    },
    "auto_post": true
  }
```

### Prompt Templates

```python
# Monthly content calendar generation
CONTENT_CALENDAR_PROMPT = """
Generate a month's worth of social media posts for a {business_type}.

Business Context:
- Brand Voice: {brand_voice}
- Target Audience: {target_audience}
- Key Themes: {key_themes}
- Products to Feature: {products}
- Posting Frequency: {posts_per_week} posts/week
- Preferred Days: {preferred_days}

Requirements:
1. Create {total_posts} posts for {month}
2. Mix of content types: 40% promotional, 30% educational, 20% engagement, 10% testimonial
3. Include seasonal/trending topics for {month}
4. Vary posting times throughout the day
5. Each post should include:
   - Engaging text (platform-optimized)
   - 3-5 relevant hashtags
   - Image description/prompt
   - Best time to post
   - Content category

Output Format (JSON array):
[
  {
    "date": "YYYY-MM-DD",
    "time": "HH:MM",
    "post_text": "...",
    "hashtags": ["tag1", "tag2"],
    "image_prompt": "...",
    "category": "promotional|educational|engagement|testimonial"
  }
]
"""

# Platform-specific variations
PLATFORM_VARIATION_PROMPT = """
Adapt this social media post for {platform}:

Original Post: "{original_post}"
Original Hashtags: {original_hashtags}

Platform Guidelines:
- {platform_guidelines}

Create a variation optimized for {platform} while maintaining the core message.
"""
```

---

## 🔧 Shared Components

### LLM Gateway Integration

```python
# shared/integrations/llm_gateway.py

from typing import Dict, Any, List
import httpx
from app.config import settings

class LLMGatewayClient:
    """Client for LLM Gateway Service"""

    BASE_URL = settings.LLM_GATEWAY_URL  # http://localhost:8004

    @staticmethod
    async def generate_completion(
        prompt: str,
        model: str = "gpt-4",
        system_prompt: str = None,
        temperature: float = 0.7,
        max_tokens: int = 500,
        response_format: str = "text"  # text or json
    ) -> Dict[str, Any]:
        """
        Generate AI completion

        Returns:
            {
                "completion": "...",
                "tokens_used": 450,
                "model": "gpt-4",
                "finish_reason": "stop"
            }
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LLMGatewayClient.BASE_URL}/api/v1/completions",
                json={
                    "prompt": prompt,
                    "system_prompt": system_prompt,
                    "model": model,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "response_format": response_format
                },
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()

    @staticmethod
    async def analyze_sentiment(text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text

        Returns:
            {
                "sentiment": "positive|neutral|negative",
                "score": 0.85,
                "keywords": ["great", "excellent"]
            }
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{LLMGatewayClient.BASE_URL}/api/v1/sentiment",
                json={"text": text},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
```

### Token Usage Tracking

```python
# shared/utils/token_tracker.py

from app.database import get_session
from app.models import AITokenUsage
from decimal import Decimal

async def track_token_usage(
    site_id: str,
    feature: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    reference_type: str = None,
    reference_id: str = None
):
    """Track AI token usage for billing"""

    # Token pricing (per 1K tokens)
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.001, "output": 0.002},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-sonnet": {"input": 0.003, "output": 0.015}
    }

    total_tokens = prompt_tokens + completion_tokens

    # Calculate cost
    pricing = PRICING.get(model, {"input": 0.01, "output": 0.02})
    cost = (
        (prompt_tokens / 1000) * pricing["input"] +
        (completion_tokens / 1000) * pricing["output"]
    )

    # Save to database
    async with get_session() as session:
        usage = AITokenUsage(
            site_id=site_id,
            feature=feature,
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost=Decimal(str(cost)),
            reference_type=reference_type,
            reference_id=reference_id
        )
        session.add(usage)
        await session.commit()
```

---

## 📊 System Integration

### Service Communication Flow

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ 1. Request AI generation
       ▼
┌──────────────────┐
│ Domain Service   │ (Storefront/Review/Content)
│                  │
│ • Validate input │
│ • Build prompt   │
│ • Check quota    │
└──────┬───────────┘
       │ 2. Call LLM Gateway
       ▼
┌──────────────────┐
│  LLM Gateway     │ (Port 8004)
│                  │
│ • Route to model │
│ • Execute prompt │
│ • Parse response │
│ • Track tokens   │
└──────┬───────────┘
       │ 3. Call AI API
       ▼
┌──────────────────┐
│ OpenAI/Claude    │
│      API         │
└──────┬───────────┘
       │ 4. Return completion
       ▼
┌──────────────────┐
│ Domain Service   │
│                  │
│ • Save result    │
│ • Track usage    │
│ • Return to user │
└──────┬───────────┘
       │ 5. Response
       ▼
┌──────────────────┐
│     Client       │
└──────────────────┘
```

---

## 🚀 Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] LLM Gateway Service setup
- [ ] Shared token tracking utilities
- [ ] Base AI prompt templates
- [ ] Database schemas for all three features

### Phase 2: Product Description Generator (Week 2)
- [ ] Database tables and models
- [ ] API endpoints implementation
- [ ] Prompt templates for different categories
- [ ] Batch generation queue
- [ ] A/B testing framework

### Phase 3: Review Responder (Week 3)
- [ ] Review Service implementation
- [ ] Sentiment analysis integration
- [ ] Response generation
- [ ] Approval workflow
- [ ] Platform integrations (Google, Yelp)

### Phase 4: Social Media Calendar (Week 4)
- [ ] Calendar generation
- [ ] Post scheduling
- [ ] Platform variations
- [ ] Auto-posting integration
- [ ] Performance analytics

### Phase 5: Testing & Optimization (Week 5)
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Cost optimization
- [ ] Documentation
- [ ] Deployment

---

## 💰 Pricing Strategy

### Token-Based Pricing

**Free Tier:**
- 10,000 tokens/month
- ~20 product descriptions OR
- ~50 review responses OR
- ~10 social posts

**Starter ($29/month):**
- 100,000 tokens/month
- ~200 product descriptions
- ~500 review responses
- ~100 social posts

**Professional ($99/month):**
- 500,000 tokens/month
- All AI features unlimited
- Priority processing
- Custom prompt templates

**Enterprise (Custom):**
- Unlimited tokens
- Dedicated AI resources
- Custom model fine-tuning
- White-label options

---

## 📈 Success Metrics

### Technical Metrics
- API response time < 2s for generation
- 99.9% uptime
- Token cost per generation
- Cache hit rate > 30%

### Business Metrics
- Active users per feature
- Tokens consumed per site
- Revenue per AI feature
- Customer retention rate

### Quality Metrics
- AI-generated content approval rate > 85%
- User customization rate < 30%
- Customer satisfaction score > 4.5/5

---

**Next Steps:** Implementation begins after design approval! 🚀
