# Review Response Generator Plugin

AI-powered review response generator with sentiment analysis.

## Features

- ✅ Automatic sentiment analysis (positive, neutral, negative)
- ✅ Tone-matched responses (grateful, professional, apologetic)
- ✅ Personalization (business name, reviewer name)
- ✅ Issue identification and addressing (negative reviews)
- ✅ Batch response generation
- ✅ JSON structured output
- ✅ Token tracking

## Installation

```bash
pip install ai-platform-core ai-platform-openai pyyaml
```

## Quick Start

```python
from ai_features.review_response import ReviewResponsePlugin
from ai_core import AIEngine
from ai_providers.openai import OpenAIProvider

# Setup
provider = OpenAIProvider(api_key="sk-...")
engine = AIEngine(provider=provider)
plugin = ReviewResponsePlugin(ai_engine=engine)

# Generate response
result = await plugin.generate_response(
    review_data={
        "rating": 5,
        "reviewer_name": "Sarah Johnson",
        "review_text": "Amazing service! The staff was incredibly helpful and professional."
    },
    business_name="Green Valley Salon",
    owner_name="Maria"  # Optional signature
)

print(result["response_text"])
```

## Output Format

### Positive Review Response

```json
{
  "response_text": "Thank you so much, Sarah! We're thrilled to hear you had such a wonderful experience...",
  "sentiment": "positive",
  "sentiment_score": 0.8,
  "tone": "grateful",
  "keywords": ["amazing", "helpful", "professional"],
  "tokens_used": 180,
  "model": "gpt-4"
}
```

### Negative Review Response

```json
{
  "response_text": "We sincerely apologize for your experience, John. This is not the standard we hold ourselves to...",
  "sentiment": "negative",
  "sentiment_score": 0.2,
  "tone": "apologetic",
  "issues_addressed": ["slow service", "cold food"],
  "keywords": ["slow", "cold", "disappointed"],
  "tokens_used": 220,
  "model": "gpt-4"
}
```

## Sentiment Detection

Automatic sentiment analysis based on rating and text:

- **Positive**: 4-5 stars → Grateful, warm response
- **Neutral**: 3 stars → Balanced, professional response
- **Negative**: 1-2 stars → Apologetic, solution-focused response

```python
# Sentiment is automatically detected
result = await plugin.generate_response(
    review_data={
        "rating": 2,  # Negative
        "review_text": "Service was slow and food was cold"
    },
    business_name="My Restaurant"
)

print(result["sentiment"])  # "negative"
print(result["tone"])  # "apologetic"
print(result["issues_addressed"])  # ["slow service", "cold food"]
```

## Personalization

Add business and owner details:

```python
result = await plugin.generate_response(
    review_data={...},
    business_name="Green Valley Salon",
    owner_name="Maria Garcia",  # Adds signature
    custom_instructions="Mention our new loyalty program"
)

# Response includes:
# "... We'd love to welcome you back!
#
# Maria Garcia
# Green Valley Salon"
```

## Batch Generation

Generate responses for multiple reviews:

```python
reviews = [
    {"rating": 5, "review_text": "Great service!", "review_id": "1"},
    {"rating": 2, "review_text": "Disappointed...", "review_id": "2"},
    {"rating": 4, "review_text": "Good experience", "review_id": "3"}
]

results = await plugin.generate_batch(
    reviews=reviews,
    business_name="My Business",
    owner_name="John"
)

for result in results:
    if result["success"]:
        print(f"Review {result['review_id']}: {result['sentiment']}")
        print(result["response_text"])
```

## Filter Pending Reviews

Get reviews needing responses:

```python
all_reviews = [...]  # From database

# Get only negative reviews needing responses
pending = await plugin.get_pending_reviews(
    reviews=all_reviews,
    filter_sentiment=["negative"],  # Only negative
    limit=20
)

# Generate responses for critical reviews
results = await plugin.generate_batch(
    reviews=pending,
    business_name="My Business"
)
```

## Custom Instructions

Add specific instructions per response:

```python
result = await plugin.generate_response(
    review_data={...},
    business_name="Restaurant",
    custom_instructions="Offer a 20% discount on their next visit"
)

# Response will naturally include the discount offer
```

## Integration Examples

### With Review Service

```python
# domain-services/review-service/app/ai.py
from ai_features.review_response import ReviewResponsePlugin
from ai_core import container

review_plugin = ReviewResponsePlugin(ai_engine=container.get_engine())

@router.post("/reviews/{review_id}/generate-response")
async def generate_response(review_id: str):
    review = await get_review(review_id)

    result = await review_plugin.generate_response(
        review_data={
            "rating": review.rating,
            "reviewer_name": review.reviewer_name,
            "review_text": review.review_text
        },
        business_name=review.business_name,
        site_id=review.site_id
    )

    # Save to database
    await save_ai_response(review_id, result)

    return result
```

### Auto-Response Workflow

```python
# Auto-generate responses for positive reviews
async def auto_respond_to_positive_reviews():
    # Get recent positive reviews
    reviews = await db.get_reviews(
        rating__gte=4,
        has_response=False,
        limit=50
    )

    # Generate responses
    results = await review_plugin.generate_batch(
        reviews=reviews,
        business_name="My Business"
    )

    # Save for approval
    for result in results:
        if result["success"]:
            await db.save_draft_response(
                review_id=result["review_id"],
                response_text=result["response_text"],
                status="pending_approval"
            )
```

### Platform Integration (Google, Yelp)

```python
# Fetch from Google My Business
google_reviews = await google_api.get_reviews()

# Generate responses
for review in google_reviews:
    result = await review_plugin.generate_response(
        review_data={
            "rating": review.starRating,
            "reviewer_name": review.reviewer.displayName,
            "review_text": review.comment
        },
        business_name="My Business"
    )

    # Post back to Google
    if auto_post_enabled:
        await google_api.post_response(
            review_id=review.reviewId,
            response_text=result["response_text"]
        )
```

## Performance

- **Time**: 1-2 seconds per response
- **Cost**: ~$0.01-0.02 per response (GPT-4)
- **Cost**: ~$0.0005-0.001 per response (GPT-3.5)

Monthly costs:
- 100 reviews: $1-2 (GPT-4) or $0.05-0.10 (GPT-3.5)
- 1000 reviews: $10-20 (GPT-4) or $0.50-1.00 (GPT-3.5)

## Best Practices

1. **Review before posting** - Always have human oversight
2. **Prioritize negative reviews** - Respond to 1-2 star reviews first
3. **Personalize** - Add business owner name for authenticity
4. **Be specific** - Reference details from the review
5. **Track performance** - Monitor response rates and follow-up reviews

## Response Guidelines

### DO:
- ✅ Thank reviewers genuinely
- ✅ Address specific points mentioned
- ✅ Offer solutions for negative reviews
- ✅ Invite them back
- ✅ Keep it professional but warm

### DON'T:
- ❌ Use template-sounding language
- ❌ Over-apologize (sounds insincere)
- ❌ Make excuses
- ❌ Get defensive
- ❌ Be too brief or generic

## Analytics

Track response effectiveness:

```python
# Monitor which responses get best engagement
SELECT
    sentiment,
    AVG(follow_up_rating) as avg_follow_up,
    COUNT(*) as response_count
FROM review_responses
WHERE posted_at > NOW() - INTERVAL '30 days'
GROUP BY sentiment;
```

## Pricing Tiers

**Starter ($29/month)**:
- 200 AI responses
- All sentiment types
- Basic personalization

**Professional ($99/month)**:
- 1000 AI responses
- Custom instructions
- Platform auto-posting
- Analytics

## Multi-Language Support (Future)

```python
result = await plugin.generate_response(
    review_data={
        "review_text": "Excelente servicio!",
        "rating": 5
    },
    business_name="Mi Negocio",
    language="es"  # Spanish
)
```
