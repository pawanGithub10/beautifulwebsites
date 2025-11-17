"""
Site Service - Domain Service for managing website configurations

This service demonstrates the plug-and-play modular architecture:
- Clean separation from core services
- Event-driven communication
- Multi-tenant by design
- Horizontally scalable
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
import logging

from app.config import settings
from app.database import engine, init_db
from app.routers import sites, templates, sections

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan - handles startup and shutdown
    """
    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME} on port {settings.SERVICE_PORT}")

    # Create database tables
    await init_db()

    logger.info(f"{settings.SERVICE_NAME} started successfully")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.SERVICE_NAME}")
    logger.info(f"{settings.SERVICE_NAME} stopped")


# Create FastAPI app
app = FastAPI(
    title="Site Service",
    description="Domain service for managing multi-tenant website configurations",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint (no auth required)
@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers and monitoring"""
    return {
        "service": settings.SERVICE_NAME,
        "status": "healthy",
        "version": "1.0.0"
    }

# Readiness check
@app.get("/ready")
async def readiness_check():
    """Readiness check - verifies dependencies are available"""
    try:
        # Check database connection
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        return {
            "service": settings.SERVICE_NAME,
            "status": "ready",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service not ready: {str(e)}"
        )

# Include routers
# Note: Authentication can be added per-route or here as a dependency
app.include_router(
    sites.router,
    prefix="/v1/sites",
    tags=["Sites"]
)

app.include_router(
    templates.router,
    prefix="/v1/templates",
    tags=["Templates"]
)

app.include_router(
    sections.router,
    prefix="/v1/sites",
    tags=["Sections"]
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
