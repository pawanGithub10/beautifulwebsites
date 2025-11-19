"""
FastAPI router for Review Response generation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from ai_features.review_response.plugin import ReviewResponsePlugin
from ..models import (
    ReviewResponseRequest,
    ReviewResponseResponse,
    ErrorResponse
)
from ..dependencies import get_review_plugin
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/review",
    tags=["Review Response"],
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        403: {"model": ErrorResponse, "description": "Quota exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "AI provider unavailable"}
    }
)


@router.post(
    "/respond",
    response_model=ReviewResponseResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate review response",
    description="""
    Generate AI-powered responses to customer reviews with sentiment analysis.

    **Features:**
    - Automatic sentiment analysis (positive, neutral, negative)
    - Tone-matched responses (empathetic for negative, enthusiastic for positive)
    - Personalization with reviewer name
    - Platform-specific variations (Google, Yelp, Facebook)
    - Professional and brand-appropriate responses
    - Keyword extraction from reviews

    **Returns:**
    - Personalized response text
    - Sentiment analysis results
    - Keyword extraction
    - Platform variations (optional)
    - Token usage information
    """
)
async def generate_response(
    request: ReviewResponseRequest,
    plugin: ReviewResponsePlugin = Depends(get_review_plugin)
) -> ReviewResponseResponse:
    """
    Generate a response to a customer review using AI.

    Example request:
    ```json
    {
        "review_text": "Amazing service! The team was professional and my hair looks fantastic.",
        "rating": 5,
        "reviewer_name": "Sarah",
        "business_name": "Bella Beauty Salon",
        "business_type": "beauty salon",
        "platform": "google"
    }
    ```
    """
    try:
        logger.info(f"Generating response for {request.rating}-star review")

        # Build review data dict
        review_data = {
            "review_text": request.review_text,
            "rating": request.rating
        }

        if request.reviewer_name:
            review_data["reviewer_name"] = request.reviewer_name
        if request.platform:
            review_data["platform"] = request.platform

        # Generate response
        result = await plugin.generate_response(
            review_data=review_data,
            business_name=request.business_name,
            business_type=request.business_type,
            site_id=request.site_id,
            model=request.model
        )

        # Build response
        response = ReviewResponseResponse(
            response_text=result["response_text"],
            sentiment=result["sentiment"]["sentiment"],
            sentiment_score=result["sentiment"]["score"],
            keywords=result["sentiment"]["keywords"],
            platform_variations=result.get("platform_variations"),
            review_rating=request.rating,
            tokens_used=result["tokens_used"],
            model=result["model"],
            generated_at=datetime.fromisoformat(result["generated_at"].replace('Z', '+00:00'))
        )

        logger.info(
            f"Response generated successfully: {response.sentiment} sentiment "
            f"({response.sentiment_score:.2f}), {response.tokens_used} tokens"
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
        logger.error(f"Error generating review response: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate review response. Please try again."
        )


@router.post(
    "/analyze",
    response_model=dict,
    summary="Analyze review sentiment",
    description="Analyze sentiment of a review without generating a response"
)
async def analyze_sentiment(
    review_text: str,
    rating: int,
    plugin: ReviewResponsePlugin = Depends(get_review_plugin)
) -> dict:
    """
    Analyze sentiment of a review.

    Returns sentiment classification, score, and keywords without generating a response.

    Example:
    ```json
    {
        "review_text": "The food was okay, nothing special.",
        "rating": 3
    }
    ```
    """
    try:
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")

        logger.info(f"Analyzing sentiment for {rating}-star review")

        # Analyze sentiment
        result = await plugin.analyze_sentiment(
            review_text=review_text,
            rating=rating
        )

        logger.info(f"Sentiment analysis complete: {result['sentiment']} ({result['score']:.2f})")

        return result

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze sentiment. Please try again."
        )


@router.get(
    "/examples",
    response_model=dict,
    summary="Get example review responses",
    description="Get example responses for different sentiment levels"
)
async def get_examples() -> dict:
    """
    Get example review responses for reference.

    Shows how responses vary based on sentiment and rating.
    """
    return {
        "examples": [
            {
                "sentiment": "positive",
                "rating": 5,
                "review": "Amazing service! The team was professional and my hair looks fantastic. Will definitely come back!",
                "response": "Thank you so much for your wonderful review! We're thrilled that you loved your experience at Bella Beauty Salon. Our team works hard to provide exceptional service, and it means the world to us to know we exceeded your expectations. We can't wait to see you again soon!"
            },
            {
                "sentiment": "neutral",
                "rating": 3,
                "review": "The service was okay. Got what I needed but nothing special.",
                "response": "Thank you for taking the time to share your feedback. We appreciate your visit and would love the opportunity to exceed your expectations next time. If there's anything specific we can improve, please don't hesitate to reach out to us directly."
            },
            {
                "sentiment": "negative",
                "rating": 2,
                "review": "Disappointed with the service. Had to wait 30 minutes past my appointment time.",
                "response": "We sincerely apologize for the wait time and disappointment with your recent visit. This is not the level of service we strive to provide. We would appreciate the opportunity to make this right. Please contact us directly so we can discuss how we can better serve you in the future."
            }
        ],
        "sentiment_levels": [
            {"level": "very positive", "rating_range": "5 stars"},
            {"level": "positive", "rating_range": "4 stars"},
            {"level": "neutral", "rating_range": "3 stars"},
            {"level": "negative", "rating_range": "2 stars"},
            {"level": "very negative", "rating_range": "1 star"}
        ]
    }


@router.get(
    "/best-practices",
    response_model=dict,
    summary="Get review response best practices",
    description="Get tips for responding to customer reviews effectively"
)
async def get_best_practices() -> dict:
    """
    Get best practices for responding to reviews.

    Returns guidelines and tips for effective review management.
    """
    return {
        "best_practices": [
            {
                "category": "Response Time",
                "tip": "Respond within 24-48 hours",
                "reason": "Shows you value customer feedback and are actively engaged"
            },
            {
                "category": "Personalization",
                "tip": "Use the reviewer's name when available",
                "reason": "Makes the response feel genuine and personal"
            },
            {
                "category": "Positive Reviews",
                "tip": "Express gratitude and reinforce key points",
                "reason": "Encourages repeat business and shows appreciation"
            },
            {
                "category": "Negative Reviews",
                "tip": "Acknowledge the issue and offer to resolve offline",
                "reason": "Shows you care about solutions, not public arguments"
            },
            {
                "category": "Neutral Reviews",
                "tip": "Thank them and invite them to share more feedback",
                "reason": "Opens dialogue and shows commitment to improvement"
            },
            {
                "category": "Brand Voice",
                "tip": "Maintain consistent brand voice across all responses",
                "reason": "Reinforces brand identity and professionalism"
            }
        ],
        "dos": [
            "Always thank the reviewer",
            "Address specific points mentioned in the review",
            "Take responsibility when appropriate",
            "Offer solutions for negative experiences",
            "Keep responses professional and courteous"
        ],
        "donts": [
            "Don't argue or get defensive",
            "Don't use generic, copy-paste responses",
            "Don't ignore negative reviews",
            "Don't make promises you can't keep",
            "Don't violate customer privacy in responses"
        ]
    }
