"""
Standalone Example: Review Response Generator

Demonstrates using the Review Response plugin without a web framework.
"""

import asyncio
import sys
import os
import json

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../packages'))

from ai_core.application.AIEngine import AIEngineBuilder
from ai_providers.openai.OpenAIProvider import OpenAIProvider
from ai_features.review_response.plugin import ReviewResponsePlugin


async def main():
    """Main example function"""
    print("=" * 60)
    print("Review Response Generator - Standalone Example")
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
    plugin = ReviewResponsePlugin(ai_engine=engine)
    print("✅ AI Engine and Plugin ready!")
    print()

    # Example 1: Positive Review (5 stars)
    print("💬 Example 1: Positive Review Response (5 stars)")
    print("-" * 60)

    review_data = {
        "review_text": "Amazing service! The team was incredibly professional and my hair looks fantastic. The salon is beautiful and clean. I've already booked my next appointment!",
        "rating": 5,
        "reviewer_name": "Sarah M.",
        "platform": "google"
    }

    result = await plugin.generate_response(
        review_data=review_data,
        business_name="Bella Beauty Salon",
        business_type="beauty salon",
        model="gpt-4"
    )

    print(f"\n📝 Original Review:")
    print(f"   Rating: {'⭐' * review_data['rating']}")
    print(f"   \"{review_data['review_text']}\"")
    print(f"   - {review_data['reviewer_name']}")

    print(f"\n💬 Generated Response:")
    print(f"   {result['response_text']}")

    print(f"\n📊 Sentiment Analysis:")
    print(f"   Sentiment: {result['sentiment']['sentiment']}")
    print(f"   Score: {result['sentiment']['score']:.2f}")
    print(f"   Keywords: {', '.join(result['sentiment']['keywords'])}")
    print(f"\n💰 Tokens Used: {result['tokens_used']}")
    print()

    # Example 2: Neutral Review (3 stars)
    print("💬 Example 2: Neutral Review Response (3 stars)")
    print("-" * 60)

    review_data = {
        "review_text": "The service was okay. Got what I needed but nothing particularly stood out. Prices are average for the area.",
        "rating": 3,
        "reviewer_name": "Mike D."
    }

    result = await plugin.generate_response(
        review_data=review_data,
        business_name="Bella Beauty Salon",
        model="gpt-4"
    )

    print(f"\n📝 Original Review:")
    print(f"   Rating: {'⭐' * review_data['rating']}")
    print(f"   \"{review_data['review_text']}\"")

    print(f"\n💬 Generated Response:")
    print(f"   {result['response_text']}")

    print(f"\n📊 Sentiment: {result['sentiment']['sentiment']} ({result['sentiment']['score']:.2f})")
    print()

    # Example 3: Negative Review (2 stars)
    print("💬 Example 3: Negative Review Response (2 stars)")
    print("-" * 60)

    review_data = {
        "review_text": "Disappointed with the service. Had to wait 30 minutes past my appointment time. The stylist seemed rushed and didn't listen to what I wanted.",
        "rating": 2,
        "reviewer_name": "Jennifer K."
    }

    result = await plugin.generate_response(
        review_data=review_data,
        business_name="Bella Beauty Salon",
        model="gpt-4"
    )

    print(f"\n📝 Original Review:")
    print(f"   Rating: {'⭐' * review_data['rating']}")
    print(f"   \"{review_data['review_text']}\"")

    print(f"\n💬 Generated Response:")
    print(f"   {result['response_text']}")

    print(f"\n📊 Sentiment: {result['sentiment']['sentiment']} ({result['sentiment']['score']:.2f})")
    print()

    # Example 4: Sentiment Analysis Only
    print("📊 Example 4: Sentiment Analysis Only")
    print("-" * 60)

    sentiment = await plugin.analyze_sentiment(
        review_text="The product exceeded my expectations! Best purchase I've made this year.",
        rating=5
    )

    print(f"\n   Sentiment: {sentiment['sentiment']}")
    print(f"   Confidence: {sentiment['score']:.2f}")
    print(f"   Keywords: {', '.join(sentiment['keywords'])}")
    print()

    # Export results
    print("💾 Exporting last result to JSON...")
    with open("review_response_output.json", "w") as f:
        json.dump(result, f, indent=2)
    print("✅ Saved to: review_response_output.json")
    print()

    print("=" * 60)
    print("✨ All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Warning: OPENAI_API_KEY not set. Examples will use mock data.\n")

    asyncio.run(main())
