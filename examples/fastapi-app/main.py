"""
Complete FastAPI Example Application

Demonstrates full integration of all AI features with production-ready patterns.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import sys
import os

# Add packages to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../packages'))

from ai_fastapi import (
    product_description_router,
    review_response_router,
    social_calendar_router,
    add_ai_middleware
)
from ai_fastapi.dependencies import configure_ai_platform, get_ai_engine
from ai_fastapi.models import HealthResponse
from ai_core.application.AIEngine import AIEngine
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Beautiful Websites AI API",
    description="""
    AI-powered features for website generation platform.

    **Features:**
    - Product Description Generator
    - Customer Review Responder
    - Social Media Calendar Generator

    All features are powered by advanced AI models with caching and usage tracking.
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Product Description",
            "description": "Generate SEO-optimized product descriptions"
        },
        {
            "name": "Review Response",
            "description": "Generate sentiment-aware review responses"
        },
        {
            "name": "Social Media Calendar",
            "description": "Generate 30-day social media calendars"
        },
        {
            "name": "System",
            "description": "Health checks and system information"
        }
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Configure AI platform on startup
@app.on_event("startup")
async def startup():
    """Initialize AI platform with all components"""
    logger.info("🚀 Starting Beautiful Websites AI Platform...")

    try:
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("⚠️  OPENAI_API_KEY not set. Using mock provider.")

        # Configure platform
        configure_ai_platform(
            provider_type="openai",
            api_key=api_key,
            enable_cache=os.getenv("ENABLE_CACHE", "true").lower() == "true",
            enable_tracking=os.getenv("ENABLE_TRACKING", "true").lower() == "true",
            redis_url=os.getenv("REDIS_URL"),
            postgres_url=os.getenv("DATABASE_URL")
        )

        logger.info("✅ AI Platform initialized successfully!")
        logger.info(f"   Cache: {os.getenv('ENABLE_CACHE', 'true')}")
        logger.info(f"   Tracking: {os.getenv('ENABLE_TRACKING', 'true')}")

    except Exception as e:
        logger.error(f"❌ Failed to initialize AI Platform: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down AI Platform...")


# Add AI middleware
app = add_ai_middleware(
    app,
    enable_error_handler=True,
    enable_logging=True,
    enable_rate_limit=os.getenv("ENABLE_RATE_LIMIT", "false").lower() == "true",
    rate_limit_requests=int(os.getenv("RATE_LIMIT_REQUESTS", "100")),
    rate_limit_window=int(os.getenv("RATE_LIMIT_WINDOW", "3600"))
)

# Include AI feature routers
app.include_router(product_description_router)
app.include_router(review_response_router)
app.include_router(social_calendar_router)

# ============================================================================
# ROOT AND SYSTEM ENDPOINTS
# ============================================================================

@app.get("/", response_class=HTMLResponse, tags=["System"])
async def root():
    """
    Root endpoint with welcome page
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Beautiful Websites AI API</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                padding: 40px;
                border-radius: 10px;
                backdrop-filter: blur(10px);
            }
            h1 { margin-top: 0; }
            a {
                color: #fff;
                text-decoration: none;
                border-bottom: 2px solid #fff;
                padding-bottom: 2px;
            }
            a:hover { opacity: 0.8; }
            .feature {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
            }
            .links {
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid rgba(255, 255, 255, 0.3);
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Beautiful Websites AI API</h1>
            <p>Welcome to the AI-powered features platform!</p>

            <h2>Available Features:</h2>

            <div class="feature">
                <h3>📝 Product Description Generator</h3>
                <p>Generate SEO-optimized product descriptions with category-specific prompts.</p>
            </div>

            <div class="feature">
                <h3>💬 Review Response Generator</h3>
                <p>Create sentiment-aware responses to customer reviews automatically.</p>
            </div>

            <div class="feature">
                <h3>📱 Social Media Calendar</h3>
                <p>Generate 30-day content calendars with strategic content mix.</p>
            </div>

            <div class="links">
                <h3>Get Started:</h3>
                <p>📚 <a href="/docs">Interactive API Documentation (Swagger UI)</a></p>
                <p>📖 <a href="/redoc">Alternative Documentation (ReDoc)</a></p>
                <p>💚 <a href="/health">Health Check</a></p>
            </div>
        </div>
    </body>
    </html>
    """


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health(engine: AIEngine = Depends(get_ai_engine)):
    """
    Health check endpoint

    Returns system health status including AI provider availability.
    """
    try:
        # Check provider health
        provider_healthy = await engine.provider.check_health()
        provider_name = engine.provider.__class__.__name__.replace("Provider", "")

        return HealthResponse(
            status="healthy" if provider_healthy else "degraded",
            ai_provider=provider_name,
            provider_healthy=provider_healthy,
            cache_enabled=engine.enable_cache,
            tracking_enabled=engine.token_tracker is not None,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


@app.get("/stats", tags=["System"])
async def stats(engine: AIEngine = Depends(get_ai_engine)):
    """
    Get system statistics

    Returns usage statistics and system metrics.
    """
    return {
        "system": {
            "status": "operational",
            "version": "1.0.0"
        },
        "provider": {
            "name": engine.provider.__class__.__name__.replace("Provider", ""),
            "pricing": engine.provider.get_pricing()
        },
        "features": {
            "cache_enabled": engine.enable_cache,
            "tracking_enabled": engine.token_tracker is not None
        },
        "endpoints": {
            "product_description": "/api/product/description",
            "review_response": "/api/review/respond",
            "social_calendar": "/api/social/calendar",
            "social_post": "/api/social/post"
        }
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. API calls will use mock data.")
        print("   Set OPENAI_API_KEY environment variable for real AI functionality.")

    # Run server
    print("\n🚀 Starting Beautiful Websites AI API Server")
    print("=" * 60)
    print(f"📍 Server: http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")
    print(f"💚 Health: http://localhost:8000/health")
    print("=" * 60)
    print("\nPress Ctrl+C to stop\n")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
