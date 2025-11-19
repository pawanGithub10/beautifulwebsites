"""
Review Response Generator Plugin

AI-powered review response generator with sentiment analysis.

Installation:
    pip install ai-platform-core ai-platform-openai pyyaml

Usage:
    from ai_features.review_response import ReviewResponsePlugin
    from ai_core import AIEngine
    from ai_providers.openai import OpenAIProvider

    provider = OpenAIProvider(api_key="sk-...")
    engine = AIEngine(provider=provider)

    plugin = ReviewResponsePlugin(ai_engine=engine)

    result = await plugin.generate_response(
        review_data={
            "rating": 5,
            "reviewer_name": "Sarah",
            "review_text": "Amazing service! Very professional..."
        },
        business_name="My Business"
    )

    print(result["response_text"])
"""

from .plugin import ReviewResponsePlugin

__version__ = "1.0.0"

__all__ = ["ReviewResponsePlugin"]
