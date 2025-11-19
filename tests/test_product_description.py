"""
Unit tests for Product Description Plugin
"""

import pytest
import sys
import os

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../packages'))

from ai_core.application.AIEngine import AIEngineBuilder
from ai_providers.mock.MockProvider import MockProvider
from ai_features.product_description.plugin import ProductDescriptionPlugin


@pytest.fixture
async def plugin():
    """Create plugin with mock provider"""
    provider = MockProvider()
    builder = AIEngineBuilder()
    builder.with_provider(provider)
    engine = builder.build()
    return ProductDescriptionPlugin(ai_engine=engine)


@pytest.mark.asyncio
async def test_generate_description_basic(plugin):
    """Test basic product description generation"""
    result = await plugin.generate_description(
        product_data={
            "name": "Test Product",
            "features": "Feature 1, Feature 2"
        },
        model="mock-gpt-4"
    )

    assert "description" in result
    assert "short_description" in result
    assert "meta_title" in result
    assert "meta_description" in result
    assert "tags" in result
    assert isinstance(result["tags"], list)
    assert result["tokens_used"] > 0


@pytest.mark.asyncio
async def test_generate_description_with_category(plugin):
    """Test description generation with category"""
    result = await plugin.generate_description(
        product_data={
            "name": "Organic Quinoa",
            "features": "Organic, High protein"
        },
        category="grocery",
        model="mock-gpt-4"
    )

    assert result["description"] is not None
    assert len(result["description"]) > 0


@pytest.mark.asyncio
async def test_generate_description_with_tone(plugin):
    """Test description generation with different tones"""
    tones = ["professional", "casual", "luxury", "technical", "friendly"]

    for tone in tones:
        result = await plugin.generate_description(
            product_data={
                "name": "Test Product",
                "features": "Feature 1"
            },
            tone=tone,
            model="mock-gpt-4"
        )

        assert result is not None
        assert "description" in result


@pytest.mark.asyncio
async def test_generate_description_with_length(plugin):
    """Test description generation with different lengths"""
    lengths = ["short", "medium", "long"]

    for length in lengths:
        result = await plugin.generate_description(
            product_data={
                "name": "Test Product",
                "features": "Feature 1"
            },
            length=length,
            model="mock-gpt-4"
        )

        assert result is not None
        assert "description" in result


@pytest.mark.asyncio
async def test_generate_description_with_price(plugin):
    """Test description generation with price"""
    result = await plugin.generate_description(
        product_data={
            "name": "Test Product",
            "features": "Feature 1",
            "price": "$29.99"
        },
        model="mock-gpt-4"
    )

    assert result is not None


@pytest.mark.asyncio
async def test_generate_description_validation(plugin):
    """Test validation of required fields"""
    with pytest.raises(ValueError):
        await plugin.generate_description(
            product_data={},  # Missing required fields
            model="mock-gpt-4"
        )


@pytest.mark.asyncio
async def test_generate_description_includes_metadata(plugin):
    """Test that result includes metadata"""
    result = await plugin.generate_description(
        product_data={
            "name": "Test Product",
            "features": "Feature 1"
        },
        model="mock-gpt-4"
    )

    assert "tokens_used" in result
    assert "model" in result
    assert "generated_at" in result
    assert result["model"] == "mock-gpt-4"


@pytest.mark.asyncio
async def test_multiple_categories(plugin):
    """Test all available categories"""
    categories = ["grocery", "electronics", "fashion", None]

    for category in categories:
        result = await plugin.generate_description(
            product_data={
                "name": f"Test {category or 'general'} Product",
                "features": "Feature 1, Feature 2"
            },
            category=category,
            model="mock-gpt-4"
        )

        assert result is not None
        assert "description" in result
