# Social Media Content Calendar Generator 📱

AI-powered 30-day social media content calendar with platform variations, optimal timing, and content mix strategies.

## Features

- **30-Day Content Calendars**: Complete monthly planning with strategic content distribution
- **Content Mix Strategy**: 40% promotional, 30% educational, 20% engagement, 10% testimonial
- **Platform Variations**: Optimized content for Instagram, Facebook, Twitter, LinkedIn
- **Hashtag Research**: AI-suggested hashtags for each post
- **Image Prompts**: Detailed image descriptions for visual content creation
- **Optimal Timing**: Smart scheduling based on engagement patterns
- **Theme-Based Planning**: Seasonal and trending topic integration
- **Single Post Generation**: On-demand post creation with platform variations

## Installation

```bash
pip install ai-platform-core ai-platform-openai pyyaml
```

## Quick Start

```python
from ai_features.social_calendar import SocialCalendarPlugin
from ai_core import AIEngine
from ai_providers.openai import OpenAIProvider

# Setup AI engine
provider = OpenAIProvider(api_key="sk-...")
engine = AIEngine(provider=provider)

# Initialize plugin
plugin = SocialCalendarPlugin(ai_engine=engine)

# Generate 30-day calendar
result = await plugin.generate_calendar(
    month="2025-02",
    business_context={
        "business_type": "beauty salon",
        "brand_voice": "friendly and professional",
        "target_audience": "women 25-45"
    },
    posts_per_week=5
)

print(f"Generated {result['total_posts']} posts")
for post in result['posts']:
    print(f"{post['date']} {post['time']}: {post['post_text']}")
```

## Content Mix Strategy

The plugin automatically distributes posts according to proven social media best practices:

- **40% Promotional** (12/30 posts): Products, offers, sales, announcements
- **30% Educational** (9/30 posts): Tips, how-tos, industry insights, tutorials
- **20% Engagement** (6/30 posts): Questions, polls, behind-the-scenes, user content
- **10% Testimonial** (3/30 posts): Reviews, success stories, customer spotlights

## Usage Examples

### Generate Full Calendar

```python
result = await plugin.generate_calendar(
    month="2025-03",
    business_context={
        "business_type": "restaurant",
        "brand_voice": "warm and inviting",
        "target_audience": "families and food lovers"
    },
    posts_per_week=5,
    themes=["spring menu", "local sourcing", "chef specials"],
    products_to_feature=[
        {"name": "Spring Tasting Menu", "price": "$65"},
        {"name": "Weekend Brunch", "price": "$28"}
    ],
    site_id="site_123"
)

# Result structure
{
    "calendar_id": "cal_2025-03_20250119123045",
    "month": "2025-03",
    "business_type": "restaurant",
    "total_posts": 20,
    "posts": [
        {
            "date": "2025-03-01",
            "time": "09:00",
            "post_text": "Spring has sprung at our kitchen! 🌸 Try our new seasonal tasting menu...",
            "hashtags": ["#SpringMenu", "#FarmToTable", "#SeasonalEating"],
            "image_prompt": "Beautiful spring tasting menu with fresh vegetables and flowers",
            "category": "promotional"
        },
        {
            "date": "2025-03-03",
            "time": "15:00",
            "post_text": "Chef's Tip: Always let meat rest for 5-10 minutes after cooking for juicier results! 👨‍🍳",
            "hashtags": ["#ChefTips", "#CookingTips", "#FoodKnowledge"],
            "image_prompt": "Chef demonstrating proper meat resting technique",
            "category": "educational"
        }
    ],
    "tokens_used": 2850,
    "model": "gpt-4",
    "generated_at": "2025-01-19T12:30:45Z"
}
```

### Generate Single Post with Platform Variations

```python
post = await plugin.generate_single_post(
    topic="New product launch - Organic Face Serum",
    business_context={
        "business_type": "beauty brand",
        "brand_voice": "clean and empowering"
    },
    post_type="promotional",
    platforms=["instagram", "facebook", "twitter"],
    site_id="site_456"
)

# Result with platform-specific variations
{
    "main_text": "Introducing our new Organic Face Serum ✨",
    "hashtags": ["#OrganicBeauty", "#CleanSkincare", "#NewLaunch"],
    "image_prompt": "Elegant product shot of face serum with botanical ingredients",
    "platforms": {
        "instagram": {
            "text": "Glow naturally ✨ Our new Organic Face Serum is here! Packed with...",
            "hashtags": ["#OrganicBeauty", "#CleanSkincare", "#InstaBeauty"]
        },
        "facebook": {
            "text": "We're excited to announce our new Organic Face Serum! Made with...",
            "hashtags": ["#OrganicBeauty", "#CleanSkincare"]
        },
        "twitter": {
            "text": "NEW: Organic Face Serum 🌿 Clean ingredients, glowing results. Shop now →",
            "hashtags": ["#OrganicBeauty", "#CleanSkincare"]
        }
    },
    "topic": "New product launch - Organic Face Serum",
    "post_type": "promotional",
    "tokens_used": 650
}
```

### Custom Calendar Configuration

```python
# High-frequency posting schedule
result = await plugin.generate_calendar(
    month="2025-04",
    business_context={
        "business_type": "fitness studio",
        "brand_voice": "energetic and motivating",
        "target_audience": "fitness enthusiasts 20-40"
    },
    posts_per_week=7,  # Daily posting
    themes=["summer body", "outdoor workouts", "nutrition tips"]
)

# Result: 28 posts (7 per week × 4 weeks)
```

## API Reference

### SocialCalendarPlugin

#### `__init__(ai_engine: AIEngine)`

Initialize the plugin with an AI engine.

**Parameters:**
- `ai_engine` (AIEngine): Configured AI engine instance

#### `async generate_calendar(...)`

Generate a complete monthly social media calendar.

**Parameters:**
- `month` (str): Target month in YYYY-MM format (e.g., "2025-02")
- `business_context` (Dict): Business information
  - `business_type` (str, required): Type of business (e.g., "salon", "restaurant")
  - `brand_voice` (str, required): Brand tone (e.g., "friendly", "professional", "luxury")
  - `target_audience` (str, optional): Target demographic description
- `posts_per_week` (int, default=5): Number of posts per week (1-7)
- `themes` (List[str], optional): Key themes to cover in content
- `products_to_feature` (List[Dict], optional): Products to highlight
- `site_id` (str, optional): Site ID for usage tracking
- `model` (str, default="gpt-4"): AI model to use

**Returns:**
- Dict with calendar_id, month, total_posts, posts array, tokens_used, model

**Raises:**
- `ValueError`: If required business context is missing

#### `async generate_single_post(...)`

Generate a single social media post with platform variations.

**Parameters:**
- `topic` (str): Post topic or theme
- `business_context` (Dict): Business information
- `post_type` (str, default="promotional"): Type of post (promotional, educational, engagement, testimonial)
- `platforms` (List[str], optional): Target platforms (default: ["instagram", "facebook"])
- `site_id` (str, optional): Site ID for tracking
- `model` (str, default="gpt-4"): AI model to use

**Returns:**
- Dict with main_text, hashtags, image_prompt, platform variations, tokens_used

## Content Categories

### Promotional (40%)
- Product launches and features
- Special offers and discounts
- Sales announcements
- Event promotions
- Limited-time deals

### Educational (30%)
- Industry tips and tricks
- How-to guides and tutorials
- Expert advice and insights
- Best practices
- Educational content

### Engagement (20%)
- Questions to audience
- Polls and surveys
- Behind-the-scenes content
- User-generated content features
- Interactive challenges

### Testimonial (10%)
- Customer reviews and ratings
- Success stories and case studies
- Client spotlights and features
- Before/after transformations
- Community highlights

## Optimal Posting Times

The plugin automatically varies posting times throughout the day:

- **Morning** (9:00 AM): Catch early scrollers, breakfast engagement
- **Lunch** (12:00 PM): Midday break, high mobile usage
- **Afternoon** (3:00 PM): Afternoon slump, snack time browsing
- **Evening** (6:00 PM): After-work relaxation, prime engagement
- **Night** (8:00 PM): Evening wind-down, longest session times

## Integration Patterns

### With FastAPI

```python
from fastapi import FastAPI, HTTPException
from ai_features.social_calendar import SocialCalendarPlugin
from ai_core import AIEngine
from ai_providers.openai import OpenAIProvider

app = FastAPI()

# Setup at startup
provider = OpenAIProvider(api_key="sk-...")
engine = AIEngine(provider=provider)
calendar_plugin = SocialCalendarPlugin(ai_engine=engine)

@app.post("/api/calendar/generate")
async def generate_calendar(request: CalendarRequest):
    try:
        result = await calendar_plugin.generate_calendar(
            month=request.month,
            business_context=request.business_context,
            posts_per_week=request.posts_per_week
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### With Flask

```python
from flask import Flask, request, jsonify
from ai_features.social_calendar import SocialCalendarPlugin
import asyncio

app = Flask(__name__)
calendar_plugin = SocialCalendarPlugin(ai_engine=engine)

@app.route('/api/calendar/generate', methods=['POST'])
def generate_calendar():
    data = request.json

    result = asyncio.run(calendar_plugin.generate_calendar(
        month=data['month'],
        business_context=data['business_context']
    ))

    return jsonify(result)
```

### Standalone Script

```python
import asyncio
from ai_features.social_calendar import SocialCalendarPlugin
from ai_core import AIEngine
from ai_providers.openai import OpenAIProvider

async def main():
    provider = OpenAIProvider(api_key="sk-...")
    engine = AIEngine(provider=provider)
    plugin = SocialCalendarPlugin(ai_engine=engine)

    # Generate calendar
    result = await plugin.generate_calendar(
        month="2025-02",
        business_context={
            "business_type": "coffee shop",
            "brand_voice": "cozy and welcoming"
        }
    )

    # Export to CSV
    import csv
    with open('calendar.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'time', 'post_text', 'category'])
        writer.writeheader()
        writer.writerows(result['posts'])

    print(f"Exported {len(result['posts'])} posts to calendar.csv")

if __name__ == "__main__":
    asyncio.run(main())
```

## Prompt Customization

Customize calendar generation by modifying `prompts/calendar.yaml`:

```yaml
name: calendar
description: Generate monthly social media content calendar

template: |
  Generate a {posts_count}-post social media content calendar for {month}.

  Business Context:
  - Type: {business_type}
  - Brand Voice: {brand_voice}
  - Target Audience: {target_audience}

  # Add your custom requirements here

  Output ONLY valid JSON array...
```

## Cost Optimization

**Estimated Costs** (based on GPT-4 pricing):

- **Full Calendar** (30 posts): ~$0.08-0.15 per calendar
- **Single Post**: ~$0.01-0.02 per post
- **With Caching**: 30-50% cost reduction on repeated requests

**Tips to Reduce Costs:**

1. Enable caching for frequently requested months/themes
2. Use GPT-3.5 Turbo for drafts, GPT-4 for finals
3. Batch multiple calendars in single request
4. Reuse calendar structures with minor variations

```python
# Use cheaper model for drafts
draft = await plugin.generate_calendar(
    month="2025-03",
    business_context=context,
    model="gpt-3.5-turbo"
)

# Use GPT-4 only for final polish
final = await plugin.generate_calendar(
    month="2025-03",
    business_context=context,
    model="gpt-4"
)
```

## Best Practices

1. **Provide Rich Context**: More business details = better content
2. **Use Themes**: Guide AI with seasonal/trending topics
3. **Review and Edit**: AI is a starting point, add your unique voice
4. **A/B Test**: Try different brand voices and content mixes
5. **Track Performance**: Monitor which categories perform best
6. **Schedule in Advance**: Generate calendars 2-4 weeks ahead
7. **Platform Optimization**: Use platform variations for better engagement

## Troubleshooting

**Issue: Posts don't match my brand voice**

- Solution: Be more specific in brand_voice ("professional and data-driven" vs "professional")
- Add examples of your best posts to themes

**Issue: Too many promotional posts**

- Solution: The 40/30/20/10 mix is a default. Fork and customize the prompt template

**Issue: Hashtags not relevant**

- Solution: Add industry-specific keywords to business_context or themes

**Issue: Image prompts too generic**

- Solution: Include visual style preferences in brand_voice ("minimalist photography", "vibrant illustrations")

## Examples by Industry

### Beauty Salon

```python
calendar = await plugin.generate_calendar(
    month="2025-02",
    business_context={
        "business_type": "beauty salon",
        "brand_voice": "luxurious and pampering",
        "target_audience": "women 25-50 seeking self-care"
    },
    themes=["Valentine's specials", "winter skin care", "new treatments"]
)
```

### Restaurant

```python
calendar = await plugin.generate_calendar(
    month="2025-03",
    business_context={
        "business_type": "Italian restaurant",
        "brand_voice": "authentic and family-oriented",
        "target_audience": "families and food enthusiasts"
    },
    themes=["spring menu", "wine pairings", "chef stories"],
    products_to_feature=[
        {"name": "Spring Risotto Special", "price": "$24"}
    ]
)
```

### Fitness Studio

```python
calendar = await plugin.generate_calendar(
    month="2025-04",
    business_context={
        "business_type": "yoga studio",
        "brand_voice": "calming and empowering",
        "target_audience": "wellness seekers 25-45"
    },
    themes=["outdoor sessions", "mindfulness", "nutrition tips"],
    posts_per_week=7  # Daily engagement
)
```

## Architecture

Built on the modular AI platform architecture:

- **Domain Layer**: Pure business logic, framework-agnostic
- **Application Layer**: Uses AIEngine interface
- **Infrastructure Layer**: Pluggable AI providers (OpenAI, Claude, etc.)
- **Presentation Layer**: Works with any web framework

This plugin can be used standalone or integrated into any Python application.

## License

Part of the Beautiful Websites AI Platform.

## Support

For issues or questions, see the main platform documentation or create an issue in the repository.
