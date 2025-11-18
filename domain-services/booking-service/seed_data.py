"""
Seed Data Script - Sample data for Booking Service

Creates sample data for testing:
- Service categories
- Services (haircuts, facials, massages, etc.)
- Providers with skills
- Recurring weekly schedules

Usage:
    python seed_data.py --site-id <uuid> --business-type <salon|coaching|consulting>
"""

import asyncio
import sys
from uuid import UUID
from decimal import Decimal
from datetime import time
import argparse
import logging

from app.database import get_db_direct
from app.models import ServiceCategory, Service, Provider, RecurringSchedule
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ======================
# SALON/SPA DATA
# ======================

SALON_CATEGORIES = [
    {
        "name": "Hair Services",
        "slug": "hair-services",
        "description": "Hair care and styling services",
        "icon": "✂️"
    },
    {
        "name": "Skin Services",
        "slug": "skin-services",
        "description": "Facial and skin care treatments",
        "icon": "✨"
    },
    {
        "name": "Spa Services",
        "slug": "spa-services",
        "description": "Relaxation and wellness treatments",
        "icon": "💆"
    }
]

SALON_SERVICES = [
    {
        "category": "hair-services",
        "name": "Women's Haircut",
        "slug": "womens-haircut",
        "sku": "HAIR-WC-001",
        "short_description": "Professional haircut for women",
        "description": "Expert haircut tailored to your face shape and style. Includes wash and basic styling.",
        "price": Decimal("599.00"),
        "compare_at_price": Decimal("799.00"),
        "duration_minutes": 45,
        "buffer_minutes": 15,
        "images": ["/images/womens-haircut.jpg"],
        "tags": ["haircut", "women", "popular"],
        "is_featured": True
    },
    {
        "category": "hair-services",
        "name": "Men's Haircut",
        "slug": "mens-haircut",
        "sku": "HAIR-MC-001",
        "short_description": "Professional haircut for men",
        "description": "Classic or modern haircut. Includes hair wash and styling.",
        "price": Decimal("399.00"),
        "duration_minutes": 30,
        "buffer_minutes": 15,
        "images": ["/images/mens-haircut.jpg"],
        "tags": ["haircut", "men", "popular"],
        "is_featured": True
    },
    {
        "category": "hair-services",
        "name": "Hair Coloring",
        "slug": "hair-coloring",
        "sku": "HAIR-COL-001",
        "short_description": "Complete hair color transformation",
        "description": "Full hair coloring using premium brands. Includes toner and conditioning treatment.",
        "price": Decimal("2999.00"),
        "duration_minutes": 120,
        "buffer_minutes": 30,
        "images": ["/images/hair-color.jpg"],
        "tags": ["color", "premium"],
        "is_featured": True
    },
    {
        "category": "skin-services",
        "name": "Gold Facial",
        "slug": "gold-facial",
        "sku": "SKIN-GF-001",
        "short_description": "Luxury gold facial treatment",
        "description": "Premium facial with 24k gold. Deep cleansing, exfoliation, and hydration.",
        "price": Decimal("1999.00"),
        "duration_minutes": 60,
        "buffer_minutes": 15,
        "images": ["/images/gold-facial.jpg"],
        "tags": ["facial", "premium", "popular"],
        "is_featured": True
    },
    {
        "category": "skin-services",
        "name": "Basic Cleanup",
        "slug": "basic-cleanup",
        "sku": "SKIN-BC-001",
        "short_description": "Basic skin cleanup and care",
        "description": "Cleansing, exfoliation, and moisturizing. Perfect for regular maintenance.",
        "price": Decimal("799.00"),
        "duration_minutes": 30,
        "buffer_minutes": 10,
        "images": ["/images/cleanup.jpg"],
        "tags": ["facial", "basic"],
        "is_featured": False
    },
    {
        "category": "spa-services",
        "name": "Full Body Massage",
        "slug": "full-body-massage",
        "sku": "SPA-FBM-001",
        "short_description": "Relaxing full body massage",
        "description": "Complete body massage with aromatic oils. Choose from Swedish, Thai, or Deep Tissue.",
        "price": Decimal("2499.00"),
        "duration_minutes": 90,
        "buffer_minutes": 15,
        "images": ["/images/massage.jpg"],
        "tags": ["massage", "spa", "relaxation"],
        "is_featured": True
    }
]

SALON_PROVIDERS = [
    {
        "name": "Priya Sharma",
        "email": "priya@salon.com",
        "phone": "+919876543210",
        "bio": "Senior hair stylist with 10+ years of experience. Specialized in modern cuts and coloring.",
        "services": ["womens-haircut", "mens-haircut", "hair-coloring"],
        "schedule": [
            # Monday to Friday: 10 AM - 7 PM
            {"day": 0, "start": "10:00", "end": "19:00"},
            {"day": 1, "start": "10:00", "end": "19:00"},
            {"day": 2, "start": "10:00", "end": "19:00"},
            {"day": 3, "start": "10:00", "end": "19:00"},
            {"day": 4, "start": "10:00", "end": "19:00"},
        ]
    },
    {
        "name": "Rahul Verma",
        "email": "rahul@salon.com",
        "phone": "+919876543211",
        "bio": "Expert in men's grooming and beard styling. 8 years experience.",
        "services": ["mens-haircut"],
        "schedule": [
            # Tuesday to Saturday: 11 AM - 8 PM
            {"day": 1, "start": "11:00", "end": "20:00"},
            {"day": 2, "start": "11:00", "end": "20:00"},
            {"day": 3, "start": "11:00", "end": "20:00"},
            {"day": 4, "start": "11:00", "end": "20:00"},
            {"day": 5, "start": "11:00", "end": "20:00"},
        ]
    },
    {
        "name": "Anjali Patel",
        "email": "anjali@salon.com",
        "phone": "+919876543212",
        "bio": "Certified beautician and skin care specialist. Expert in facials and skin treatments.",
        "services": ["gold-facial", "basic-cleanup"],
        "schedule": [
            # Monday to Saturday: 9 AM - 6 PM
            {"day": 0, "start": "09:00", "end": "18:00"},
            {"day": 1, "start": "09:00", "end": "18:00"},
            {"day": 2, "start": "09:00", "end": "18:00"},
            {"day": 3, "start": "09:00", "end": "18:00"},
            {"day": 4, "start": "09:00", "end": "18:00"},
            {"day": 5, "start": "09:00", "end": "18:00"},
        ]
    },
    {
        "name": "Deepak Kumar",
        "email": "deepak@salon.com",
        "phone": "+919876543213",
        "bio": "Licensed massage therapist. Specialized in therapeutic and relaxation massage.",
        "services": ["full-body-massage"],
        "schedule": [
            # Monday to Friday: 12 PM - 9 PM
            {"day": 0, "start": "12:00", "end": "21:00"},
            {"day": 1, "start": "12:00", "end": "21:00"},
            {"day": 2, "start": "12:00", "end": "21:00"},
            {"day": 3, "start": "12:00", "end": "21:00"},
            {"day": 4, "start": "12:00", "end": "21:00"},
        ]
    }
]


async def create_categories(db, site_id, categories_data):
    """Create service categories"""
    category_map = {}

    for cat_data in categories_data:
        category = ServiceCategory(
            site_id=site_id,
            name=cat_data["name"],
            slug=cat_data["slug"],
            description=cat_data.get("description"),
            icon=cat_data.get("icon"),
            is_active=True
        )

        db.add(category)
        await db.flush()
        await db.refresh(category)

        category_map[cat_data["slug"]] = category
        logger.info(f"Created category: {category.name}")

    return category_map


async def create_services(db, site_id, services_data, category_map):
    """Create services"""
    service_map = {}

    for svc_data in services_data:
        category = category_map.get(svc_data["category"])
        if not category:
            logger.warning(f"Category not found: {svc_data['category']}")
            continue

        service = Service(
            site_id=site_id,
            category_id=category.category_id,
            name=svc_data["name"],
            slug=svc_data["slug"],
            sku=svc_data["sku"],
            short_description=svc_data.get("short_description"),
            description=svc_data.get("description"),
            price=svc_data["price"],
            compare_at_price=svc_data.get("compare_at_price"),
            duration_minutes=svc_data["duration_minutes"],
            buffer_minutes=svc_data.get("buffer_minutes", 0),
            images=svc_data.get("images", []),
            tags=svc_data.get("tags", []),
            is_featured=svc_data.get("is_featured", False),
            is_active=True
        )

        db.add(service)
        await db.flush()
        await db.refresh(service)

        service_map[svc_data["slug"]] = service
        logger.info(f"Created service: {service.name}")

    return service_map


async def create_providers(db, site_id, providers_data, service_map):
    """Create providers with schedules"""
    for prov_data in providers_data:
        # Get service IDs
        service_ids = []
        for service_slug in prov_data["services"]:
            service = service_map.get(service_slug)
            if service:
                service_ids.append(service.service_id)

        provider = Provider(
            site_id=site_id,
            name=prov_data["name"],
            email=prov_data.get("email"),
            phone=prov_data.get("phone"),
            bio=prov_data.get("bio"),
            is_active=True,
            accepts_bookings=True,
            service_ids=service_ids
        )

        db.add(provider)
        await db.flush()
        await db.refresh(provider)

        logger.info(f"Created provider: {provider.name}")

        # Create recurring schedules
        for sched_data in prov_data.get("schedule", []):
            start_parts = sched_data["start"].split(":")
            end_parts = sched_data["end"].split(":")

            schedule = RecurringSchedule(
                provider_id=provider.provider_id,
                day_of_week=sched_data["day"],
                start_time=time(hour=int(start_parts[0]), minute=int(start_parts[1])),
                end_time=time(hour=int(end_parts[0]), minute=int(end_parts[1])),
                is_active=True
            )

            db.add(schedule)
            logger.info(f"  - Created schedule: Day {sched_data['day']}, {sched_data['start']}-{sched_data['end']}")

    await db.flush()


async def seed_data(site_id: UUID, business_type: str):
    """Main seed function"""
    logger.info(f"Seeding data for site {site_id} (type: {business_type})")

    # Select data based on business type
    if business_type == "salon":
        categories_data = SALON_CATEGORIES
        services_data = SALON_SERVICES
        providers_data = SALON_PROVIDERS
    else:
        logger.error(f"Unknown business type: {business_type}")
        return

    # Get database session
    async for db in get_db_direct():
        try:
            # Create categories
            logger.info("Creating categories...")
            category_map = await create_categories(db, site_id, categories_data)

            # Create services
            logger.info("Creating services...")
            service_map = await create_services(db, site_id, services_data, category_map)

            # Create providers
            logger.info("Creating providers...")
            await create_providers(db, site_id, providers_data, service_map)

            # Commit
            await db.commit()
            logger.info("Seed data created successfully!")

        except Exception as e:
            await db.rollback()
            logger.error(f"Error seeding data: {e}")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed booking data")
    parser.add_argument("--site-id", required=True, help="Site UUID")
    parser.add_argument("--business-type", required=True, choices=["salon", "coaching", "consulting"],
                        help="Business type (salon, coaching, consulting)")

    args = parser.parse_args()

    try:
        site_id = UUID(args.site_id)
    except ValueError:
        logger.error("Invalid site ID format")
        sys.exit(1)

    asyncio.run(seed_data(site_id, args.business_type))
