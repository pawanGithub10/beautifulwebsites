"""
Unit tests for Social Calendar Plugin
"""

import pytest
import sys
import os

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../packages'))

from ai_core.application.AIEngine import AIEngineBuilder
from ai_providers.mock.MockProvider import MockProvider
from ai_features.social_calendar.plugin import SocialCalendarPlugin


@pytest.fixture
async def plugin():
    """Create plugin with mock provider"""
    provider = MockProvider()
    builder = AIEngineBuilder()
    builder.with_provider(provider)
    engine = builder.build()
    return SocialCalendarPlugin(ai_engine=engine)


@pytest.mark.asyncio
async def test_generate_calendar_basic(plugin):
    """Test basic calendar generation"""
    result = await plugin.generate_calendar(
        month="2025-02",
        business_context={
            "business_type": "coffee shop",
            "brand_voice": "cozy"
        },
        model="mock-gpt-4"
    )

    assert "calendar_id" in result
    assert "month" in result
    assert "total_posts" in result
    assert "posts" in result
    assert "content_mix" in result
    assert result["month"] == "2025-02"
    assert isinstance(result["posts"], list)
    assert len(result["posts"]) > 0


@pytest.mark.asyncio
async def test_calendar_posts_per_week(plugin):
    """Test calendar with different posts per week"""
    for posts_per_week in [3, 5, 7]:
        result = await plugin.generate_calendar(
            month="2025-02",
            business_context={
                "business_type": "restaurant",
                "brand_voice": "warm"
            },
            posts_per_week=posts_per_week,
            model="mock-gpt-4"
        )

        # 4 weeks * posts_per_week
        expected_posts = posts_per_week * 4
        assert result["total_posts"] == expected_posts
        assert len(result["posts"]) == expected_posts


@pytest.mark.asyncio
async def test_calendar_content_mix(plugin):
    """Test that content mix is correctly distributed"""
    result = await plugin.generate_calendar(
        month="2025-02",
        business_context={
            "business_type": "salon",
            "brand_voice": "professional"
        },
        posts_per_week=5,
        model="mock-gpt-4"
    )

    content_mix = result["content_mix"]
    total = result["total_posts"]

    # Check that all categories are present
    assert "promotional" in content_mix
    assert "educational" in content_mix
    assert "engagement" in content_mix
    assert "testimonial" in content_mix

    # Check that counts sum to total
    assert sum(content_mix.values()) == total


@pytest.mark.asyncio
async def test_calendar_with_themes(plugin):
    """Test calendar generation with themes"""
    result = await plugin.generate_calendar(
        month="2025-03",
        business_context={
            "business_type": "gym",
            "brand_voice": "energetic"
        },
        themes=["spring fitness", "nutrition tips"],
        model="mock-gpt-4"
    )

    assert result is not None
    assert "posts" in result


@pytest.mark.asyncio
async def test_calendar_with_products(plugin):
    """Test calendar generation with product features"""
    result = await plugin.generate_calendar(
        month="2025-04",
        business_context={
            "business_type": "retail",
            "brand_voice": "friendly"
        },
        products_to_feature=[
            {"name": "Product 1", "price": "$29.99"},
            {"name": "Product 2", "price": "$49.99"}
        ],
        model="mock-gpt-4"
    )

    assert result is not None


@pytest.mark.asyncio
async def test_post_structure(plugin):
    """Test that each post has required fields"""
    result = await plugin.generate_calendar(
        month="2025-02",
        business_context={
            "business_type": "cafe",
            "brand_voice": "cozy"
        },
        model="mock-gpt-4"
    )

    for post in result["posts"]:
        assert "date" in post
        assert "time" in post
        assert "post_text" in post
        assert "hashtags" in post
        assert "image_prompt" in post
        assert "category" in post
        assert isinstance(post["hashtags"], list)


@pytest.mark.asyncio
async def test_generate_single_post_basic(plugin):
    """Test single post generation"""
    result = await plugin.generate_single_post(
        topic="New menu launch",
        business_context={
            "business_type": "restaurant",
            "brand_voice": "warm"
        },
        model="mock-gpt-4"
    )

    assert "main_text" in result
    assert "hashtags" in result
    assert "image_prompt" in result
    assert "platforms" in result
    assert "topic" in result
    assert "post_type" in result


@pytest.mark.asyncio
async def test_single_post_platforms(plugin):
    """Test single post with specific platforms"""
    platforms = ["instagram", "facebook"]

    result = await plugin.generate_single_post(
        topic="Special offer",
        business_context={
            "business_type": "shop",
            "brand_voice": "friendly"
        },
        platforms=platforms,
        model="mock-gpt-4"
    )

    assert "platforms" in result
    # Mock provider should include these platforms
    assert len(result["platforms"]) > 0


@pytest.mark.asyncio
async def test_single_post_types(plugin):
    """Test all post types"""
    post_types = ["promotional", "educational", "engagement", "testimonial"]

    for post_type in post_types:
        result = await plugin.generate_single_post(
            topic="Test topic",
            business_context={
                "business_type": "business",
                "brand_voice": "professional"
            },
            post_type=post_type,
            model="mock-gpt-4"
        )

        assert result is not None
        assert result["post_type"] == post_type


@pytest.mark.asyncio
async def test_calendar_validation(plugin):
    """Test validation of required fields"""
    with pytest.raises(ValueError):
        await plugin.generate_calendar(
            month="2025-02",
            business_context={},  # Missing required fields
            model="mock-gpt-4"
        )


@pytest.mark.asyncio
async def test_month_format_validation(plugin):
    """Test month format validation"""
    with pytest.raises(ValueError):
        await plugin.generate_calendar(
            month="02-2025",  # Wrong format
            business_context={
                "business_type": "shop",
                "brand_voice": "friendly"
            }
        )


@pytest.mark.asyncio
async def test_posts_per_week_validation(plugin):
    """Test posts_per_week validation"""
    with pytest.raises(ValueError):
        await plugin.generate_calendar(
            month="2025-02",
            business_context={
                "business_type": "shop",
                "brand_voice": "friendly"
            },
            posts_per_week=8  # Too many
        )


@pytest.mark.asyncio
async def test_calendar_includes_metadata(plugin):
    """Test that calendar includes all metadata"""
    result = await plugin.generate_calendar(
        month="2025-02",
        business_context={
            "business_type": "business",
            "brand_voice": "professional"
        },
        model="mock-gpt-4"
    )

    assert "calendar_id" in result
    assert "tokens_used" in result
    assert "model" in result
    assert "generated_at" in result
