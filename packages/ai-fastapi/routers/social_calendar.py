"""
FastAPI router for Social Media Calendar generation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from ai_features.social_calendar.plugin import SocialCalendarPlugin
from ..models import (
    SocialCalendarRequest,
    SocialCalendarResponse,
    SinglePostRequest,
    SinglePostResponse,
    SocialPost,
    ErrorResponse
)
from ..dependencies import get_calendar_plugin
from datetime import datetime
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/social",
    tags=["Social Media Calendar"],
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        403: {"model": ErrorResponse, "description": "Quota exceeded"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "AI provider unavailable"}
    }
)


@router.post(
    "/calendar",
    response_model=SocialCalendarResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate social media calendar",
    description="""
    Generate a complete 30-day social media content calendar with AI.

    **Features:**
    - Strategic content mix (40% promotional, 30% educational, 20% engagement, 10% testimonial)
    - Multi-platform support (Instagram, Facebook, Twitter, LinkedIn)
    - Optimal posting times throughout the day
    - AI-generated hashtags (3-5 per post)
    - Image generation prompts for each post
    - Theme-based content planning
    - Seasonal and trending topic integration
    - Customizable posts per week (1-7 posts)

    **Returns:**
    - Complete month calendar with all posts
    - Content mix breakdown
    - Post details (text, hashtags, images, timing)
    - Token usage information
    """
)
async def generate_calendar(
    request: SocialCalendarRequest,
    plugin: SocialCalendarPlugin = Depends(get_calendar_plugin)
) -> SocialCalendarResponse:
    """
    Generate a complete monthly social media calendar.

    Example request:
    ```json
    {
        "month": "2025-02",
        "business_type": "coffee shop",
        "brand_voice": "cozy and welcoming",
        "target_audience": "coffee lovers and remote workers",
        "posts_per_week": 5,
        "themes": ["Valentine's specials", "new roasts"],
        "products_to_feature": [
            {"name": "Valentine's Latte", "price": "$5.50"}
        ]
    }
    ```
    """
    try:
        logger.info(f"Generating calendar for {request.month}: {request.business_type}")

        # Build business context
        business_context = {
            "business_type": request.business_type,
            "brand_voice": request.brand_voice
        }

        if request.target_audience:
            business_context["target_audience"] = request.target_audience

        # Generate calendar
        result = await plugin.generate_calendar(
            month=request.month,
            business_context=business_context,
            posts_per_week=request.posts_per_week,
            themes=request.themes,
            products_to_feature=request.products_to_feature,
            site_id=request.site_id,
            model=request.model
        )

        # Convert posts to SocialPost models
        posts = [
            SocialPost(
                date=post["date"],
                time=post["time"],
                post_text=post["post_text"],
                hashtags=post["hashtags"],
                image_prompt=post["image_prompt"],
                category=post["category"],
                platforms=post.get("platforms")
            )
            for post in result["posts"]
        ]

        # Build response
        response = SocialCalendarResponse(
            calendar_id=result["calendar_id"],
            month=result["month"],
            business_type=result["business_type"],
            total_posts=result["total_posts"],
            posts=posts,
            content_mix=result["content_mix"],
            tokens_used=result["tokens_used"],
            model=result["model"],
            generated_at=datetime.fromisoformat(result["generated_at"].replace('Z', '+00:00'))
        )

        logger.info(
            f"Calendar generated successfully: {response.total_posts} posts, "
            f"{response.tokens_used} tokens"
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
        logger.error(f"Error generating calendar: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate social calendar. Please try again."
        )


@router.post(
    "/post",
    response_model=SinglePostResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate single social media post",
    description="""
    Generate a single social media post with platform variations.

    **Features:**
    - Platform-specific content (Instagram, Facebook, Twitter, LinkedIn)
    - Post type selection (promotional, educational, engagement, testimonial)
    - AI-generated hashtags
    - Image generation prompt
    - Character limits per platform
    - Brand voice integration

    **Returns:**
    - Main post text
    - Platform-specific variations
    - Hashtag suggestions
    - Image generation prompt
    - Token usage information
    """
)
async def generate_post(
    request: SinglePostRequest,
    plugin: SocialCalendarPlugin = Depends(get_calendar_plugin)
) -> SinglePostResponse:
    """
    Generate a single social media post with platform variations.

    Example request:
    ```json
    {
        "topic": "New organic coffee bean launch",
        "business_type": "coffee shop",
        "brand_voice": "artisanal and passionate",
        "post_type": "promotional",
        "platforms": ["instagram", "facebook"]
    }
    ```
    """
    try:
        logger.info(f"Generating single post: {request.topic}")

        # Build business context
        business_context = {
            "business_type": request.business_type,
            "brand_voice": request.brand_voice
        }

        # Convert platform enums to strings
        platforms = [p.value for p in request.platforms]

        # Generate post
        result = await plugin.generate_single_post(
            topic=request.topic,
            business_context=business_context,
            post_type=request.post_type.value,
            platforms=platforms,
            site_id=request.site_id,
            model=request.model
        )

        # Build response
        response = SinglePostResponse(
            main_text=result["main_text"],
            hashtags=result["hashtags"],
            image_prompt=result["image_prompt"],
            platforms=result["platforms"],
            topic=result["topic"],
            post_type=result["post_type"],
            tokens_used=result["tokens_used"],
            model=result["model"],
            generated_at=datetime.fromisoformat(result["generated_at"].replace('Z', '+00:00'))
        )

        logger.info(
            f"Post generated successfully: {len(result['platforms'])} platform variations, "
            f"{response.tokens_used} tokens"
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
        logger.error(f"Error generating post: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate social post. Please try again."
        )


@router.get(
    "/content-mix",
    response_model=dict,
    summary="Get recommended content mix",
    description="Get the recommended content distribution strategy"
)
async def get_content_mix() -> dict:
    """
    Get recommended social media content mix.

    Returns the strategic distribution of content types for optimal engagement.
    """
    return {
        "recommended_mix": {
            "promotional": {
                "percentage": 40,
                "description": "Products, offers, sales, announcements",
                "examples": ["New product launch", "Special offer", "Sale announcement"]
            },
            "educational": {
                "percentage": 30,
                "description": "Tips, how-tos, industry insights, tutorials",
                "examples": ["How-to guide", "Expert tips", "Industry trends"]
            },
            "engagement": {
                "percentage": 20,
                "description": "Questions, polls, behind-the-scenes, user content",
                "examples": ["Poll question", "BTS content", "Customer spotlight"]
            },
            "testimonial": {
                "percentage": 10,
                "description": "Reviews, success stories, customer spotlights",
                "examples": ["Customer review", "Success story", "Before/after"]
            }
        },
        "posting_frequency": {
            "minimal": {"posts_per_week": 3, "description": "Maintain presence"},
            "moderate": {"posts_per_week": 5, "description": "Good engagement"},
            "aggressive": {"posts_per_week": 7, "description": "Maximum visibility"}
        },
        "optimal_times": [
            {"time": "09:00", "reason": "Morning scrollers, breakfast engagement"},
            {"time": "12:00", "reason": "Lunch break, high mobile usage"},
            {"time": "15:00", "reason": "Afternoon slump browsing"},
            {"time": "18:00", "reason": "After-work relaxation"},
            {"time": "20:00", "reason": "Evening wind-down, longest sessions"}
        ]
    }


@router.get(
    "/platform-specs",
    response_model=dict,
    summary="Get platform specifications",
    description="Get character limits and best practices for each platform"
)
async def get_platform_specs() -> dict:
    """
    Get platform-specific specifications and best practices.

    Returns character limits, hashtag limits, and posting guidelines.
    """
    return {
        "platforms": {
            "instagram": {
                "caption_limit": 2200,
                "hashtag_limit": 30,
                "optimal_hashtags": "5-10",
                "best_practices": [
                    "Use high-quality visuals",
                    "Mix popular and niche hashtags",
                    "Include call-to-action in bio link",
                    "Post Stories daily for engagement"
                ]
            },
            "facebook": {
                "post_limit": 63206,
                "optimal_length": "40-80 characters",
                "hashtag_limit": "No strict limit",
                "optimal_hashtags": "2-3",
                "best_practices": [
                    "Keep posts concise",
                    "Use native video when possible",
                    "Encourage comments and shares",
                    "Post when your audience is most active"
                ]
            },
            "twitter": {
                "character_limit": 280,
                "hashtag_limit": "No strict limit",
                "optimal_hashtags": "1-2",
                "best_practices": [
                    "Be concise and punchy",
                    "Use threads for longer content",
                    "Engage with replies quickly",
                    "Include relevant mentions"
                ]
            },
            "linkedin": {
                "post_limit": 3000,
                "optimal_length": "150-300 characters",
                "hashtag_limit": "No strict limit",
                "optimal_hashtags": "3-5",
                "best_practices": [
                    "Professional tone",
                    "Share industry insights",
                    "Include relevant documents",
                    "Tag companies and people when appropriate"
                ]
            }
        }
    }


@router.get(
    "/examples",
    response_model=dict,
    summary="Get example calendars",
    description="Get example social media calendars for different business types"
)
async def get_examples() -> dict:
    """
    Get example social media calendars for reference.

    Shows calendar structure and post examples for different industries.
    """
    return {
        "examples": [
            {
                "business_type": "restaurant",
                "sample_posts": [
                    {
                        "category": "promotional",
                        "text": "🍝 New Spring Menu Alert! Try our fresh seasonal dishes this week. Book your table now!",
                        "hashtags": ["#SpringMenu", "#FarmToTable", "#Foodie"]
                    },
                    {
                        "category": "educational",
                        "text": "Chef's Tip: Always let meat rest 5-10 minutes after cooking for juicier results! 👨‍🍳",
                        "hashtags": ["#ChefTips", "#CookingTips", "#FoodKnowledge"]
                    },
                    {
                        "category": "engagement",
                        "text": "What's your go-to comfort food? Tell us in the comments! 🍲",
                        "hashtags": ["#ComfortFood", "#FoodLovers", "#Community"]
                    }
                ]
            },
            {
                "business_type": "beauty salon",
                "sample_posts": [
                    {
                        "category": "promotional",
                        "text": "✨ Valentine's Special: 20% off all spa packages this week! Treat yourself or someone special.",
                        "hashtags": ["#ValentinesDay", "#SpaDay", "#SelfCare"]
                    },
                    {
                        "category": "educational",
                        "text": "Winter Hair Care 101: Use a deep conditioning treatment weekly to combat dryness! 💆‍♀️",
                        "hashtags": ["#HairCare", "#BeautyTips", "#WinterHair"]
                    },
                    {
                        "category": "testimonial",
                        "text": "\"Best haircut I've ever had!\" - Sarah M. Thank you for trusting us with your transformation! ⭐⭐⭐⭐⭐",
                        "hashtags": ["#CustomerLove", "#HairTransformation", "#5StarService"]
                    }
                ]
            }
        ]
    }
