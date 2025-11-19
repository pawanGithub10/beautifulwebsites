"""
Mock AI Provider for Testing

Provides realistic mock responses without calling external APIs.
Perfect for unit tests, CI/CD, and development without API keys.
"""

from ai_core.domain.interfaces.IAIProvider import IAIProvider
from ai_core.domain.models.AIRequest import AIRequest
from ai_core.domain.models.AIResponse import AIResponse
from typing import Dict, Optional
import json
import random


class MockProvider(IAIProvider):
    """
    Mock AI provider that generates realistic test responses.

    Does not make any external API calls - perfect for testing and development.
    """

    def __init__(self, fail_mode: bool = False, latency_ms: int = 100):
        """
        Initialize mock provider.

        Args:
            fail_mode: If True, provider will simulate failures
            latency_ms: Simulated latency in milliseconds
        """
        self.fail_mode = fail_mode
        self.latency_ms = latency_ms
        self.call_count = 0

    async def generate_completion(self, request: AIRequest) -> AIResponse:
        """
        Generate a mock completion.

        Returns realistic mock data based on the request prompt.
        """
        self.call_count += 1

        # Simulate failure mode
        if self.fail_mode and random.random() < 0.3:
            raise ConnectionError("Mock provider failure simulation")

        # Simulate latency
        if self.latency_ms > 0:
            import asyncio
            await asyncio.sleep(self.latency_ms / 1000)

        # Detect request type from prompt
        prompt_lower = request.prompt.lower()

        # Product Description
        if "product" in prompt_lower and "description" in prompt_lower:
            content = self._generate_product_description(request)

        # Review Response
        elif "review" in prompt_lower and "response" in prompt_lower:
            content = self._generate_review_response(request)

        # Social Calendar
        elif "social" in prompt_lower and "calendar" in prompt_lower:
            content = self._generate_social_calendar(request)

        # Social Post
        elif "social" in prompt_lower and "post" in prompt_lower:
            content = self._generate_social_post(request)

        # Generic response
        else:
            content = self._generate_generic(request)

        # Estimate tokens
        tokens = await self.estimate_tokens(request.prompt + content)

        return AIResponse(
            content=content,
            tokens_used=tokens,
            model=request.model or "mock-gpt-4",
            finish_reason="stop",
            metadata={"mock": True, "call_count": self.call_count}
        )

    def _generate_product_description(self, request: AIRequest) -> str:
        """Generate mock product description"""
        if request.response_format == "json":
            return json.dumps({
                "description": "This premium product combines exceptional quality with outstanding value. "
                               "Carefully crafted to meet the highest standards, it delivers reliable performance "
                               "and long-lasting satisfaction. Perfect for discerning customers who appreciate excellence.",
                "short_description": "Premium quality product with exceptional value and performance.",
                "meta_title": "Premium Quality Product | Shop Now",
                "meta_description": "Discover our premium product - exceptional quality, outstanding value, and reliable performance. Perfect for your needs.",
                "tags": ["premium", "quality", "value", "reliable", "recommended"]
            })
        else:
            return "This is a mock product description generated for testing purposes."

    def _generate_review_response(self, request: AIRequest) -> str:
        """Generate mock review response"""
        if request.response_format == "json":
            # Detect sentiment from prompt
            sentiment = "positive"
            if "negative" in request.prompt.lower() or "disappointed" in request.prompt.lower():
                sentiment = "negative"
            elif "neutral" in request.prompt.lower() or "okay" in request.prompt.lower():
                sentiment = "neutral"

            responses = {
                "positive": "Thank you so much for your wonderful review! We're thrilled that you had such a great experience. Your feedback means the world to us, and we can't wait to serve you again soon!",
                "neutral": "Thank you for taking the time to share your feedback. We appreciate your visit and would love the opportunity to exceed your expectations next time. Please don't hesitate to reach out if there's anything we can improve.",
                "negative": "We sincerely apologize for not meeting your expectations. This is not the level of service we strive to provide. We would appreciate the opportunity to make this right. Please contact us directly so we can discuss how we can better serve you in the future."
            }

            return json.dumps({
                "response_text": responses[sentiment],
                "sentiment": sentiment,
                "tone": "professional",
                "personalized": True
            })
        else:
            return "Thank you for your review! We appreciate your feedback."

    def _generate_social_calendar(self, request: AIRequest) -> str:
        """Generate mock social calendar"""
        posts = []
        for i in range(20):
            day = i + 1
            posts.append({
                "date": f"2025-02-{day:02d}",
                "time": ["09:00", "12:00", "15:00", "18:00", "20:00"][i % 5],
                "post_text": f"Exciting social media post #{day}! Join us for amazing content and engage with our community. #MockPost #Example",
                "hashtags": ["#MockPost", "#SocialMedia", "#Example"],
                "image_prompt": f"Engaging visual for post #{day} showing vibrant community interaction",
                "category": ["promotional", "educational", "engagement", "testimonial"][i % 4]
            })

        return json.dumps(posts)

    def _generate_social_post(self, request: AIRequest) -> str:
        """Generate mock social post"""
        return json.dumps({
            "main_text": "Check out our latest update! 🎉 We're excited to share something special with you.",
            "hashtags": ["#NewPost", "#Update", "#Community"],
            "image_prompt": "Eye-catching image showing product or service highlight",
            "platforms": {
                "instagram": {
                    "text": "✨ Something amazing is here! Check out our latest update and let us know what you think! 🎉",
                    "hashtags": ["#NewPost", "#InstaUpdate", "#Community"]
                },
                "facebook": {
                    "text": "We're excited to announce our latest update! Learn more and join the conversation.",
                    "hashtags": ["#NewPost", "#Update"]
                },
                "twitter": {
                    "text": "Big news! 🎉 Check out our latest update →",
                    "hashtags": ["#NewPost"]
                }
            }
        })

    def _generate_generic(self, request: AIRequest) -> str:
        """Generate generic mock response"""
        if request.response_format == "json":
            return json.dumps({
                "content": "This is a mock response generated for testing purposes.",
                "mock": True
            })
        else:
            return "This is a mock response generated for testing purposes."

    async def estimate_tokens(self, text: str) -> int:
        """
        Estimate tokens for text.

        Uses simple word count approximation: 1 token ≈ 0.75 words
        """
        words = len(text.split())
        return int(words / 0.75)

    async def check_health(self) -> bool:
        """
        Check provider health.

        Always returns True unless in fail_mode.
        """
        if self.fail_mode:
            return random.random() > 0.2  # 20% failure rate
        return True

    def get_pricing(self) -> Dict[str, float]:
        """
        Get mock pricing information.
        """
        return {
            "mock-gpt-4": 0.00,  # Free for testing
            "mock-gpt-3.5-turbo": 0.00
        }

    def reset(self):
        """Reset provider state (useful for tests)"""
        self.call_count = 0
