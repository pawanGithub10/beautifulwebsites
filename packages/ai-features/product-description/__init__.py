"""
Product Description Generator Plugin

AI-powered product description generator with category-specific prompts.

Installation:
    pip install ai-platform-core ai-platform-openai pyyaml

Usage:
    from ai_features.product_description import ProductDescriptionPlugin
    from ai_core import AIEngine
    from ai_providers.openai import OpenAIProvider

    provider = OpenAIProvider(api_key="sk-...")
    engine = AIEngine(provider=provider)

    plugin = ProductDescriptionPlugin(ai_engine=engine)

    result = await plugin.generate_description(
        product_data={
            "name": "Organic Green Tea",
            "category": "Beverages",
            "price": 299,
            "features": ["organic", "antioxidant-rich", "imported"]
        },
        category="grocery",
        tone="professional",
        length="medium"
    )

    print(result["description"])
"""

from .plugin import ProductDescriptionPlugin

__version__ = "1.0.0"

__all__ = ["ProductDescriptionPlugin"]
