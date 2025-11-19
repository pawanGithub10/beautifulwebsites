"""
Unit tests for Review Response Plugin
"""

import pytest
import sys
import os

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../packages'))

from ai_core.application.AIEngine import AIEngineBuilder
from ai_providers.mock.MockProvider import MockProvider
from ai_features.review_response.plugin import ReviewResponsePlugin


@pytest.fixture
async def plugin():
    """Create plugin with mock provider"""
    provider = MockProvider()
    builder = AIEngineBuilder()
    builder.with_provider(provider)
    engine = builder.build()
    return ReviewResponsePlugin(ai_engine=engine)


@pytest.mark.asyncio
async def test_analyze_sentiment_positive(plugin):
    """Test sentiment analysis for positive review"""
    result = await plugin.analyze_sentiment(
        review_text="Amazing service! Love it!",
        rating=5
    )

    assert "sentiment" in result
    assert "score" in result
    assert "keywords" in result
    assert result["sentiment"] in ["positive", "very positive"]
    assert 0 <= result["score"] <= 1


@pytest.mark.asyncio
async def test_analyze_sentiment_negative(plugin):
    """Test sentiment analysis for negative review"""
    result = await plugin.analyze_sentiment(
        review_text="Terrible experience. Very disappointed.",
        rating=1
    )

    assert result["sentiment"] in ["negative", "very negative"]


@pytest.mark.asyncio
async def test_analyze_sentiment_neutral(plugin):
    """Test sentiment analysis for neutral review"""
    result = await plugin.analyze_sentiment(
        review_text="It was okay, nothing special.",
        rating=3
    )

    assert result["sentiment"] == "neutral"


@pytest.mark.asyncio
async def test_generate_response_basic(plugin):
    """Test basic review response generation"""
    result = await plugin.generate_response(
        review_data={
            "review_text": "Great service!",
            "rating": 5
        },
        business_name="Test Business",
        model="mock-gpt-4"
    )

    assert "response_text" in result
    assert "sentiment" in result
    assert "tokens_used" in result
    assert "model" in result
    assert len(result["response_text"]) > 0


@pytest.mark.asyncio
async def test_generate_response_with_reviewer_name(plugin):
    """Test response generation with reviewer name"""
    result = await plugin.generate_response(
        review_data={
            "review_text": "Excellent!",
            "rating": 5,
            "reviewer_name": "John"
        },
        business_name="Test Business",
        model="mock-gpt-4"
    )

    assert result is not None
    assert "response_text" in result


@pytest.mark.asyncio
async def test_generate_response_with_platform(plugin):
    """Test response generation with platform specification"""
    platforms = ["google", "yelp", "facebook"]

    for platform in platforms:
        result = await plugin.generate_response(
            review_data={
                "review_text": "Good service",
                "rating": 4,
                "platform": platform
            },
            business_name="Test Business",
            model="mock-gpt-4"
        )

        assert result is not None


@pytest.mark.asyncio
async def test_generate_response_validation(plugin):
    """Test validation of required fields"""
    with pytest.raises(ValueError):
        await plugin.generate_response(
            review_data={},  # Missing required fields
            business_name="Test Business"
        )


@pytest.mark.asyncio
async def test_rating_validation(plugin):
    """Test that invalid ratings are rejected"""
    with pytest.raises(ValueError):
        await plugin.analyze_sentiment(
            review_text="Test",
            rating=6  # Invalid rating
        )

    with pytest.raises(ValueError):
        await plugin.analyze_sentiment(
            review_text="Test",
            rating=0  # Invalid rating
        )


@pytest.mark.asyncio
async def test_all_rating_levels(plugin):
    """Test response generation for all rating levels"""
    for rating in range(1, 6):
        result = await plugin.generate_response(
            review_data={
                "review_text": f"Rating {rating} review",
                "rating": rating
            },
            business_name="Test Business",
            model="mock-gpt-4"
        )

        assert result is not None
        assert "sentiment" in result


@pytest.mark.asyncio
async def test_business_type_optional(plugin):
    """Test that business_type is optional"""
    result = await plugin.generate_response(
        review_data={
            "review_text": "Great!",
            "rating": 5
        },
        business_name="Test Business",
        business_type="restaurant",  # Optional
        model="mock-gpt-4"
    )

    assert result is not None


@pytest.mark.asyncio
async def test_response_includes_metadata(plugin):
    """Test that response includes all required metadata"""
    result = await plugin.generate_response(
        review_data={
            "review_text": "Excellent service!",
            "rating": 5
        },
        business_name="Test Business",
        model="mock-gpt-4"
    )

    assert "response_text" in result
    assert "sentiment" in result
    assert "tokens_used" in result
    assert "model" in result
    assert "generated_at" in result
