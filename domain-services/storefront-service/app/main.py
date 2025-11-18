"""
Storefront Service - E-commerce backend

Comprehensive service for:
- Product catalog management
- Shopping cart operations
- Order processing and lifecycle
- Inventory tracking
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import text
import logging

from app.config import settings
from app.database import engine, init_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    logger.info(f"Starting {settings.SERVICE_NAME} on port {settings.SERVICE_PORT}")

    # Create database tables
    await init_db()

    logger.info(f"{settings.SERVICE_NAME} started successfully")
    yield

    logger.info(f"Shutting down {settings.SERVICE_NAME}")


# Create FastAPI app
app = FastAPI(
    title="Storefront Service",
    description="E-commerce backend for multi-website platform",
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

# Health check
@app.get("/health")
async def health_check():
    return {
        "service": settings.SERVICE_NAME,
        "status": "healthy",
        "version": "1.0.0"
    }

# Readiness check
@app.get("/ready")
async def readiness_check():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        return {
            "service": settings.SERVICE_NAME,
            "status": "ready",
            "database": "connected"
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise

# Import routers
from app.routers import products, cart, orders

# Register routers
app.include_router(
    products.router,
    prefix="/api/v1/catalog",
    tags=["Products & Categories"]
)

app.include_router(
    cart.router,
    prefix="/api/v1",
    tags=["Shopping Cart"]
)

app.include_router(
    orders.router,
    prefix="/api/v1",
    tags=["Orders"]
)

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "features": [
            "Product catalog management",
            "Category management (hierarchical)",
            "Product variants (size, color, etc.)",
            "Shopping cart (user & guest)",
            "Order processing",
            "Order lifecycle management",
            "Inventory tracking",
            "Stock history",
            "Multi-site support"
        ],
        "endpoints": {
            "catalog": "/api/v1/catalog/{site_id}/...",
            "cart": "/api/v1/{site_id}/cart",
            "orders": "/api/v1/{site_id}/orders",
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
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
