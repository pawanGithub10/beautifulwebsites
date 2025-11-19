"""
Social Media Content Calendar Generator Plugin

AI-powered 30-day content calendar with platform variations.

Installation:
    pip install ai-platform-core ai-platform-openai pyyaml

Usage:
    from ai_features.social_calendar import SocialCalendarPlugin
    from ai_core import AIEngine
    from ai_providers.openai import OpenAIProvider

    provider = OpenAIProvider(api_key="sk-...")
    engine = AIEngine(provider=provider)

    plugin = SocialCalendarPlugin(ai_engine=engine)

    result = await plugin.generate_calendar(
        month="2025-02",
        business_context={
            "business_type": "salon",
            "brand_voice": "friendly and professional",
            "target_audience": "women 25-45"
        }
    )

    print(f"Generated {result['total_posts']} posts")
"""

from .plugin import SocialCalendarPlugin

__version__ = "1.0.0"

__all__ = ["SocialCalendarPlugin"]
