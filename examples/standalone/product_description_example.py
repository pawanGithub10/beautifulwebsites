"""
Standalone Example: Product Description Generator

Demonstrates using the Product Description plugin without a web framework.
"""

import asyncio
import sys
import os
import json

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../packages'))

from ai_core.application.AIEngine import AIEngine, AIEngineBuilder
from ai_providers.openai.OpenAIProvider import OpenAIProvider
from ai_features.product_description.plugin import ProductDescriptionPlugin


async def main():
    """Main example function"""
    print("=" * 60)
    print("Product Description Generator - Standalone Example")
    print("=" * 60)
    print()

    # Initialize AI Engine
    print("🔧 Initializing AI Engine...")
    api_key = os.getenv("OPENAI_API_KEY", "sk-mock-key")
    provider = OpenAIProvider(api_key=api_key)

    builder = AIEngineBuilder()
    builder.with_provider(provider)
    builder.with_cache_enabled(False)  # Disable cache for demo
    engine = builder.build()

    print("✅ AI Engine ready!")
    print()

    # Initialize plugin
    print("🔧 Initializing Product Description Plugin...")
    plugin = ProductDescriptionPlugin(ai_engine=engine)
    print("✅ Plugin ready!")
    print()

    # Example 1: Grocery Product
    print("📝 Example 1: Grocery Product (Organic Quinoa)")
    print("-" * 60)

    result = await plugin.generate_description(
        product_data={
            "name": "Organic Quinoa",
            "features": "Organic certified, High protein, Gluten-free, Pre-washed, Sourced from Peru",
            "price": "$8.99",
            "target_audience": "Health-conscious shoppers and fitness enthusiasts"
        },
        category="grocery",
        tone="professional",
        length="medium",
        model="gpt-4"
    )

    print(f"\n📖 Full Description:")
    print(result["description"])
    print(f"\n✂️  Short Description:")
    print(result["short_description"])
    print(f"\n🏷️  Meta Title:")
    print(result["meta_title"])
    print(f"\n📝 Meta Description:")
    print(result["meta_description"])
    print(f"\n🔖 Tags:")
    print(", ".join(result["tags"]))
    print(f"\n💰 Tokens Used: {result['tokens_used']}")
    print()

    # Example 2: Electronics Product
    print("📝 Example 2: Electronics Product (Wireless Headphones)")
    print("-" * 60)

    result = await plugin.generate_description(
        product_data={
            "name": "Wireless Noise-Canceling Headphones",
            "features": "Active noise cancellation, 30-hour battery, Bluetooth 5.0, Premium comfort, Built-in microphone",
            "price": "$149.99",
            "target_audience": "Music lovers and professionals"
        },
        category="electronics",
        tone="technical",
        length="long",
        model="gpt-4"
    )

    print(f"\n📖 Full Description:")
    print(result["description"][:300] + "...")  # Show first 300 chars
    print(f"\n🔖 Tags:")
    print(", ".join(result["tags"]))
    print(f"\n💰 Tokens Used: {result['tokens_used']}")
    print()

    # Example 3: Fashion Product
    print("📝 Example 3: Fashion Product (Organic T-Shirt)")
    print("-" * 60)

    result = await plugin.generate_description(
        product_data={
            "name": "Sustainable Cotton T-Shirt",
            "features": "100% organic cotton, Fair trade certified, Eco-friendly dyes, Classic fit, Pre-shrunk",
            "price": "$29.99"
        },
        category="fashion",
        tone="friendly",
        length="short",
        model="gpt-4"
    )

    print(f"\n📖 Description:")
    print(result["description"])
    print(f"\n💰 Tokens Used: {result['tokens_used']}")
    print()

    # Export to JSON
    print("💾 Exporting last result to JSON...")
    with open("product_description_output.json", "w") as f:
        json.dump(result, f, indent=2)
    print("✅ Saved to: product_description_output.json")
    print()

    print("=" * 60)
    print("✨ All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Warning: OPENAI_API_KEY not set.")
        print("   Examples will use mock data.")
        print("   Set OPENAI_API_KEY for real AI functionality.\n")

    # Run examples
    asyncio.run(main())
