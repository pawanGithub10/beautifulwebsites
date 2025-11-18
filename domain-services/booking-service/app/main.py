"""
Booking Service - FastAPI Application

Provides appointment/booking management for:
- Salons & Spas
- Coaching centers
- Consultancies
- Any time-based service businesses
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db, engine
from sqlalchemy import text

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME} on port {settings.SERVICE_PORT}")
    await init_db()
    logger.info("Database initialized")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME}")
    await engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="Booking Service",
    description="Appointment and booking management for service-based businesses",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Import routers
from app.routers import services, providers, availability, bookings

# Register routers
app.include_router(
    services.router,
    prefix="/api/v1",
    tags=["Services & Categories"]
)

app.include_router(
    providers.router,
    prefix="/api/v1",
    tags=["Providers & Schedules"]
)

app.include_router(
    availability.router,
    prefix="/api/v1",
    tags=["Availability"]
)

app.include_router(
    bookings.router,
    prefix="/api/v1",
    tags=["Bookings"]
)


# Health check endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": "1.0.0"
    }


@app.get("/ready")
async def readiness_check():
    """Readiness check - verifies database connectivity"""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "service": settings.SERVICE_NAME,
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise


# Root endpoint
@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "Service catalog management",
            "Provider management",
            "Schedule management (recurring & specific dates)",
            "Availability checking",
            "Booking creation",
            "Booking lifecycle management",
            "Cancellation with policies",
            "Multi-provider support",
            "Multi-site support"
        ],
        "endpoints": {
            "services": "/api/v1/{site_id}/services",
            "providers": "/api/v1/{site_id}/providers",
            "availability": "/api/v1/{site_id}/availability",
            "bookings": "/api/v1/{site_id}/bookings",
            "docs": "/docs",
            "health": "/health",
            "ready": "/ready"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG
    )
