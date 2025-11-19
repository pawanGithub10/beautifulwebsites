"""
FastAPI router for Product Description generation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from ai_features.product_description.plugin import ProductDescriptionPlugin
from ..models import (
    ProductDescriptionRequest,
    ProductDescriptionResponse,
    ErrorResponse
)
from ..dependencies import get_product_plugin
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/product",
    tags=["Product Description"],
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        403: {"model": ErrorResponse, "description": "Quota exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "AI provider unavailable"}
    }
)


@router.post(
    "/description",
    response_model=ProductDescriptionResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate product description",
    description="""
    Generate AI-powered product descriptions with SEO optimization.

    **Features:**
    - Category-specific descriptions (grocery, electronics, fashion, etc.)
    - Multiple tone options (professional, casual, luxury, technical, friendly)
    - Configurable length (short, medium, long)
    - SEO-optimized meta tags and keywords
    - Automatic tag generation

    **Returns:**
    - Full product description
    - Short description for previews
    - SEO meta title and description
    - Relevant tags/keywords
    - Token usage and cost information
    """
)
async def generate_description(
    request: ProductDescriptionRequest,
    plugin: ProductDescriptionPlugin = Depends(get_product_plugin)
) -> ProductDescriptionResponse:
    """
    Generate a product description using AI.

    Example request:
    ```json
    {
        "product_name": "Organic Quinoa",
        "category": "grocery",
        "features": ["Organic certified", "High protein", "Gluten-free"],
        "price": "$8.99",
        "target_audience": "Health-conscious shoppers",
        "tone": "professional",
        "length": "medium"
    }
    ```
    """
    try:
        logger.info(f"Generating description for product: {request.product_name}")

        # Build product data dict
        product_data = {
            "name": request.product_name,
            "features": ", ".join(request.features)
        }

        if request.price:
            product_data["price"] = request.price
        if request.target_audience:
            product_data["target_audience"] = request.target_audience

        # Generate description
        result = await plugin.generate_description(
            product_data=product_data,
            category=request.category,
            tone=request.tone.value,
            length=request.length.value,
            site_id=request.site_id,
            model=request.model
        )

        # Build response
        response = ProductDescriptionResponse(
            product_name=request.product_name,
            description=result["description"],
            short_description=result["short_description"],
            meta_title=result["meta_title"],
            meta_description=result["meta_description"],
            tags=result["tags"],
            category=request.category,
            tone=request.tone.value,
            length=request.length.value,
            tokens_used=result["tokens_used"],
            model=result["model"],
            generated_at=datetime.fromisoformat(result["generated_at"].replace('Z', '+00:00'))
        )

        logger.info(
            f"Description generated successfully: {response.tokens_used} tokens, "
            f"{len(response.tags)} tags"
        )

        return response

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except PermissionError as e:
        logger.error(f"Quota exceeded: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"Error generating description: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate product description. Please try again."
        )


@router.get(
    "/categories",
    response_model=dict,
    summary="Get available product categories",
    description="Get list of supported product categories with optimized prompts"
)
async def get_categories() -> dict:
    """
    Get available product categories.

    Returns a list of categories that have specialized prompt templates.
    """
    return {
        "categories": [
            {
                "id": "grocery",
                "name": "Grocery & Food",
                "description": "Food items, beverages, organic products"
            },
            {
                "id": "electronics",
                "name": "Electronics",
                "description": "Tech products, gadgets, appliances"
            },
            {
                "id": "fashion",
                "name": "Fashion & Apparel",
                "description": "Clothing, accessories, footwear"
            },
            {
                "id": "general",
                "name": "General Products",
                "description": "Default category for other products"
            }
        ],
        "tones": ["professional", "casual", "luxury", "technical", "friendly"],
        "lengths": ["short", "medium", "long"]
    }


@router.get(
    "/examples",
    response_model=dict,
    summary="Get example descriptions",
    description="Get example product descriptions for different categories"
)
async def get_examples() -> dict:
    """
    Get example product descriptions for reference.

    Useful for understanding the output format and quality.
    """
    return {
        "examples": [
            {
                "category": "grocery",
                "product_name": "Organic Quinoa",
                "description": "Discover the ancient superfood that's revolutionizing modern nutrition. Our premium organic quinoa is carefully sourced from sustainable farms...",
                "short_description": "Premium organic quinoa, pre-washed and ready to cook.",
                "meta_title": "Organic Quinoa - High Protein Superfood | Shop Now"
            },
            {
                "category": "electronics",
                "product_name": "Wireless Noise-Canceling Headphones",
                "description": "Immerse yourself in pure sound with our cutting-edge wireless headphones. Advanced active noise cancellation technology blocks out distractions...",
                "short_description": "Premium wireless headphones with active noise cancellation.",
                "meta_title": "Wireless Noise-Canceling Headphones | Premium Audio"
            },
            {
                "category": "fashion",
                "product_name": "Sustainable Cotton T-Shirt",
                "description": "Embrace sustainable style with our eco-friendly cotton t-shirt. Made from 100% organic cotton, this versatile wardrobe essential...",
                "short_description": "Eco-friendly organic cotton t-shirt in classic fit.",
                "meta_title": "Sustainable Cotton T-Shirt | Organic Fashion"
            }
        ]
    }
