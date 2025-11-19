"""
Standalone Example: Social Media Calendar Generator

Demonstrates using the Social Calendar plugin without a web framework.
"""

import asyncio
import sys
import os
import json
import csv

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../packages'))

from ai_core.application.AIEngine import AIEngineBuilder
from ai_providers.openai.OpenAIProvider import OpenAIProvider
from ai_features.social_calendar.plugin import SocialCalendarPlugin


async def main():
    """Main example function"""
    print("=" * 60)
    print("Social Media Calendar Generator - Standalone Example")
    print("=" * 60)
    print()

    # Initialize AI Engine
    print("🔧 Initializing AI Engine...")
    api_key = os.getenv("OPENAI_API_KEY", "sk-mock-key")
    provider = OpenAIProvider(api_key=api_key)

    builder = AIEngineBuilder()
    builder.with_provider(provider)
    engine = builder.build()

    # Initialize plugin
    plugin = SocialCalendarPlugin(ai_engine=engine)
    print("✅ AI Engine and Plugin ready!")
    print()

    # Example 1: Coffee Shop Calendar
    print("📱 Example 1: Coffee Shop - Monthly Calendar")
    print("-" * 60)

    result = await plugin.generate_calendar(
        month="2025-02",
        business_context={
            "business_type": "coffee shop",
            "brand_voice": "cozy and welcoming",
            "target_audience": "coffee lovers and remote workers"
        },
        posts_per_week=5,
        themes=["Valentine's specials", "new roasts", "community events"],
        products_to_feature=[
            {"name": "Valentine's Latte", "price": "$5.50"},
            {"name": "Ethiopian Single-Origin", "price": "$16.99"}
        ],
        model="gpt-4"
    )

    print(f"\n📊 Calendar Summary:")
    print(f"   Month: {result['month']}")
    print(f"   Business: {result['business_type']}")
    print(f"   Total Posts: {result['total_posts']}")
    print(f"\n📈 Content Mix:")
    for category, count in result['content_mix'].items():
        percentage = (count / result['total_posts']) * 100
        print(f"   {category.capitalize()}: {count} posts ({percentage:.0f}%)")

    print(f"\n📅 First 5 Posts:")
    for i, post in enumerate(result['posts'][:5], 1):
        print(f"\n   Post {i}:")
        print(f"   📅 {post['date']} at {post['time']}")
        print(f"   📝 {post['post_text']}")
        print(f"   🏷️  {', '.join(post['hashtags'])}")
        print(f"   📷 Image: {post['image_prompt']}")
        print(f"   📂 Category: {post['category']}")

    print(f"\n💰 Tokens Used: {result['tokens_used']}")
    print()

    # Export to CSV
    print("💾 Exporting calendar to CSV...")
    with open("social_calendar.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'date', 'time', 'post_text', 'hashtags', 'image_prompt', 'category'
        ])
        writer.writeheader()
        for post in result['posts']:
            writer.writerow({
                'date': post['date'],
                'time': post['time'],
                'post_text': post['post_text'],
                'hashtags': ', '.join(post['hashtags']),
                'image_prompt': post['image_prompt'],
                'category': post['category']
            })
    print("✅ Saved to: social_calendar.csv")
    print()

    # Example 2: Single Post with Platform Variations
    print("📱 Example 2: Restaurant - Single Post with Platform Variations")
    print("-" * 60)

    result = await plugin.generate_single_post(
        topic="New Spring Menu Launch - Fresh Seasonal Dishes",
        business_context={
            "business_type": "Italian restaurant",
            "brand_voice": "warm and authentic"
        },
        post_type="promotional",
        platforms=["instagram", "facebook", "twitter", "linkedin"],
        model="gpt-4"
    )

    print(f"\n📝 Main Post:")
    print(f"   {result['main_text']}")

    print(f"\n🏷️  Hashtags:")
    print(f"   {', '.join(result['hashtags'])}")

    print(f"\n📷 Image Prompt:")
    print(f"   {result['image_prompt']}")

    print(f"\n📱 Platform Variations:")
    for platform, variation in result['platforms'].items():
        print(f"\n   {platform.upper()}:")
        print(f"   Text: {variation['text']}")
        print(f"   Hashtags: {', '.join(variation['hashtags'])}")

    print(f"\n💰 Tokens Used: {result['tokens_used']}")
    print()

    # Example 3: Beauty Salon - Daily Posting Schedule
    print("📱 Example 3: Beauty Salon - High Frequency Calendar")
    print("-" * 60)

    result = await plugin.generate_calendar(
        month="2025-03",
        business_context={
            "business_type": "beauty salon",
            "brand_voice": "luxurious and pampering",
            "target_audience": "women 25-50 seeking self-care"
        },
        posts_per_week=7,  # Daily posting
        themes=["spring beauty", "self-care tips", "new treatments"],
        model="gpt-4"
    )

    print(f"\n📊 Calendar Summary:")
    print(f"   Total Posts: {result['total_posts']} (daily posting)")
    print(f"   Posts per week: 7")

    print(f"\n📈 Content Mix:")
    for category, count in result['content_mix'].items():
        print(f"   {category.capitalize()}: {count} posts")

    print(f"\n💰 Tokens Used: {result['tokens_used']}")
    print()

    # Export to JSON
    print("💾 Exporting last result to JSON...")
    with open("social_calendar_output.json", "w") as f:
        json.dump(result, f, indent=2)
    print("✅ Saved to: social_calendar_output.json")
    print()

    # Tips and Best Practices
    print("💡 Content Strategy Tips:")
    print("-" * 60)
    print("\n   ✅ Recommended Content Mix:")
    print("      • 40% Promotional (products, offers, sales)")
    print("      • 30% Educational (tips, how-tos, insights)")
    print("      • 20% Engagement (questions, polls, BTS)")
    print("      • 10% Testimonial (reviews, success stories)")

    print("\n   ✅ Best Posting Times:")
    print("      • 9:00 AM - Morning scrollers")
    print("      • 12:00 PM - Lunch break")
    print("      • 3:00 PM - Afternoon break")
    print("      • 6:00 PM - After work")
    print("      • 8:00 PM - Evening wind-down")

    print("\n   ✅ Platform-Specific Tips:")
    print("      • Instagram: High-quality visuals, 5-10 hashtags")
    print("      • Facebook: Engaging questions, 2-3 hashtags")
    print("      • Twitter: Concise messages, 1-2 hashtags")
    print("      • LinkedIn: Professional tone, 3-5 hashtags")
    print()

    print("=" * 60)
    print("✨ All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Warning: OPENAI_API_KEY not set. Examples will use mock data.\n")

    asyncio.run(main())
