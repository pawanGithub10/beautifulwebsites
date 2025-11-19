"""
Pydantic models for FastAPI request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class ToneType(str, Enum):
    """Product description tone options"""
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    LUXURY = "luxury"
    TECHNICAL = "technical"
    FRIENDLY = "friendly"


class LengthType(str, Enum):
    """Product description length options"""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"


class PostType(str, Enum):
    """Social media post types"""
    PROMOTIONAL = "promotional"
    EDUCATIONAL = "educational"
    ENGAGEMENT = "engagement"
    TESTIMONIAL = "testimonial"


class SocialPlatform(str, Enum):
    """Social media platforms"""
    INSTAGRAM = "instagram"
    FACEBOOK = "facebook"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"


# ============================================================================
# PRODUCT DESCRIPTION MODELS
# ============================================================================

class ProductDescriptionRequest(BaseModel):
    """Request model for product description generation"""
    product_name: str = Field(..., description="Name of the product", min_length=1, max_length=200)
    category: Optional[str] = Field(None, description="Product category (grocery, electronics, fashion, etc.)")
    features: List[str] = Field(..., description="List of product features", min_items=1)
    price: Optional[str] = Field(None, description="Product price (e.g., '$29.99')")
    target_audience: Optional[str] = Field(None, description="Target customer demographic")
    tone: ToneType = Field(ToneType.PROFESSIONAL, description="Writing tone")
    length: LengthType = Field(LengthType.MEDIUM, description="Description length")
    site_id: Optional[str] = Field(None, description="Site ID for usage tracking")
    model: str = Field("gpt-4", description="AI model to use")

    class Config:
        schema_extra = {
            "example": {
                "product_name": "Organic Quinoa",
                "category": "grocery",
                "features": ["Organic certified", "High protein", "Gluten-free", "Pre-washed"],
                "price": "$8.99",
                "target_audience": "Health-conscious shoppers",
                "tone": "professional",
                "length": "medium",
                "site_id": "site_123"
            }
        }


class ProductDescriptionResponse(BaseModel):
    """Response model for product description"""
    product_name: str
    description: str
    short_description: str
    meta_title: str
    meta_description: str
    tags: List[str]
    category: Optional[str] = None
    tone: str
    length: str
    tokens_used: int
    model: str
    generated_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "product_name": "Organic Quinoa",
                "description": "Discover the ancient superfood that's revolutionizing modern nutrition...",
                "short_description": "Premium organic quinoa, pre-washed and ready to cook.",
                "meta_title": "Organic Quinoa - High Protein Superfood | Shop Now",
                "meta_description": "Premium organic quinoa packed with protein and nutrients. Gluten-free, pre-washed, and certified organic.",
                "tags": ["organic", "quinoa", "superfood", "gluten-free", "high-protein"],
                "category": "grocery",
                "tone": "professional",
                "length": "medium",
                "tokens_used": 450,
                "model": "gpt-4",
                "generated_at": "2025-01-19T12:00:00Z"
            }
        }


# ============================================================================
# REVIEW RESPONSE MODELS
# ============================================================================

class ReviewResponseRequest(BaseModel):
    """Request model for review response generation"""
    review_text: str = Field(..., description="The customer review text", min_length=1)
    rating: int = Field(..., description="Review rating (1-5 stars)", ge=1, le=5)
    reviewer_name: Optional[str] = Field(None, description="Name of the reviewer")
    business_name: str = Field(..., description="Your business name", min_length=1)
    business_type: Optional[str] = Field(None, description="Type of business (restaurant, salon, etc.)")
    platform: Optional[str] = Field(None, description="Review platform (google, yelp, facebook)")
    site_id: Optional[str] = Field(None, description="Site ID for usage tracking")
    model: str = Field("gpt-4", description="AI model to use")

    @validator('rating')
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v

    class Config:
        schema_extra = {
            "example": {
                "review_text": "Amazing service! The team was professional and my hair looks fantastic. Will definitely come back!",
                "rating": 5,
                "reviewer_name": "Sarah",
                "business_name": "Bella Beauty Salon",
                "business_type": "beauty salon",
                "platform": "google",
                "site_id": "site_456"
            }
        }


class ReviewResponseResponse(BaseModel):
    """Response model for review response"""
    response_text: str
    sentiment: str
    sentiment_score: float
    keywords: List[str]
    platform_variations: Optional[Dict[str, str]] = None
    review_rating: int
    tokens_used: int
    model: str
    generated_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "response_text": "Thank you so much for your wonderful review, Sarah! We're thrilled that you loved your experience...",
                "sentiment": "positive",
                "sentiment_score": 0.95,
                "keywords": ["amazing", "professional", "fantastic"],
                "platform_variations": {
                    "google": "Thank you so much for your wonderful review, Sarah!...",
                    "yelp": "We appreciate your kind words, Sarah!..."
                },
                "review_rating": 5,
                "tokens_used": 320,
                "model": "gpt-4",
                "generated_at": "2025-01-19T12:00:00Z"
            }
        }


# ============================================================================
# SOCIAL CALENDAR MODELS
# ============================================================================

class SocialPost(BaseModel):
    """Individual social media post"""
    date: str
    time: str
    post_text: str
    hashtags: List[str]
    image_prompt: str
    category: str
    platforms: Optional[Dict[str, Dict[str, Any]]] = None


class SocialCalendarRequest(BaseModel):
    """Request model for social calendar generation"""
    month: str = Field(..., description="Target month in YYYY-MM format", regex=r'^\d{4}-\d{2}$')
    business_type: str = Field(..., description="Type of business", min_length=1)
    brand_voice: str = Field(..., description="Brand voice/tone", min_length=1)
    target_audience: Optional[str] = Field(None, description="Target audience description")
    posts_per_week: int = Field(5, description="Number of posts per week", ge=1, le=7)
    themes: Optional[List[str]] = Field(None, description="Key themes to cover")
    products_to_feature: Optional[List[Dict[str, Any]]] = Field(None, description="Products to highlight")
    site_id: Optional[str] = Field(None, description="Site ID for usage tracking")
    model: str = Field("gpt-4", description="AI model to use")

    @validator('month')
    def validate_month(cls, v):
        try:
            datetime.strptime(v, '%Y-%m')
        except ValueError:
            raise ValueError('Month must be in YYYY-MM format')
        return v

    class Config:
        schema_extra = {
            "example": {
                "month": "2025-02",
                "business_type": "coffee shop",
                "brand_voice": "cozy and welcoming",
                "target_audience": "coffee lovers and remote workers",
                "posts_per_week": 5,
                "themes": ["Valentine's specials", "new roasts", "community events"],
                "products_to_feature": [
                    {"name": "Valentine's Latte", "price": "$5.50"}
                ],
                "site_id": "site_789"
            }
        }


class SocialCalendarResponse(BaseModel):
    """Response model for social calendar"""
    calendar_id: str
    month: str
    business_type: str
    total_posts: int
    posts: List[SocialPost]
    content_mix: Dict[str, int]
    tokens_used: int
    model: str
    generated_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "calendar_id": "cal_2025-02_20250119120000",
                "month": "2025-02",
                "business_type": "coffee shop",
                "total_posts": 20,
                "posts": [
                    {
                        "date": "2025-02-01",
                        "time": "09:00",
                        "post_text": "Start your weekend with our new Valentine's Latte ❤️☕",
                        "hashtags": ["#CoffeeLovers", "#ValentinesDay", "#CoffeShop"],
                        "image_prompt": "Beautiful heart-shaped latte art in red cup",
                        "category": "promotional"
                    }
                ],
                "content_mix": {
                    "promotional": 8,
                    "educational": 6,
                    "engagement": 4,
                    "testimonial": 2
                },
                "tokens_used": 2850,
                "model": "gpt-4",
                "generated_at": "2025-01-19T12:00:00Z"
            }
        }


class SinglePostRequest(BaseModel):
    """Request model for single post generation"""
    topic: str = Field(..., description="Post topic or theme", min_length=1)
    business_type: str = Field(..., description="Type of business", min_length=1)
    brand_voice: str = Field(..., description="Brand voice/tone", min_length=1)
    post_type: PostType = Field(PostType.PROMOTIONAL, description="Type of post")
    platforms: List[SocialPlatform] = Field(
        [SocialPlatform.INSTAGRAM, SocialPlatform.FACEBOOK],
        description="Target platforms"
    )
    site_id: Optional[str] = Field(None, description="Site ID for usage tracking")
    model: str = Field("gpt-4", description="AI model to use")

    class Config:
        schema_extra = {
            "example": {
                "topic": "New organic coffee bean launch",
                "business_type": "coffee shop",
                "brand_voice": "artisanal and passionate",
                "post_type": "promotional",
                "platforms": ["instagram", "facebook"],
                "site_id": "site_789"
            }
        }


class SinglePostResponse(BaseModel):
    """Response model for single post"""
    main_text: str
    hashtags: List[str]
    image_prompt: str
    platforms: Dict[str, Dict[str, Any]]
    topic: str
    post_type: str
    tokens_used: int
    model: str
    generated_at: datetime

    class Config:
        schema_extra = {
            "example": {
                "main_text": "Introducing our newest treasure: Single-origin Ethiopian beans ☕✨",
                "hashtags": ["#SpecialtyCoffee", "#EthiopianCoffee", "#NewArrival"],
                "image_prompt": "Artisanal coffee beans in burlap sack with Ethiopian origin label",
                "platforms": {
                    "instagram": {
                        "text": "Introducing our newest treasure ☕✨ Single-origin Ethiopian beans...",
                        "hashtags": ["#SpecialtyCoffee", "#EthiopianCoffee", "#CoffeeLover"]
                    },
                    "facebook": {
                        "text": "We're excited to announce our newest single-origin coffee from Ethiopia!...",
                        "hashtags": ["#SpecialtyCoffee", "#EthiopianCoffee"]
                    }
                },
                "topic": "New organic coffee bean launch",
                "post_type": "promotional",
                "tokens_used": 450,
                "model": "gpt-4",
                "generated_at": "2025-01-19T12:00:00Z"
            }
        }


# ============================================================================
# COMMON MODELS
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    status_code: int

    class Config:
        schema_extra = {
            "example": {
                "error": "Validation Error",
                "detail": "Product name is required",
                "status_code": 400
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    ai_provider: str
    provider_healthy: bool
    cache_enabled: bool
    tracking_enabled: bool
    timestamp: datetime

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "ai_provider": "OpenAI",
                "provider_healthy": True,
                "cache_enabled": True,
                "tracking_enabled": True,
                "timestamp": "2025-01-19T12:00:00Z"
            }
        }
