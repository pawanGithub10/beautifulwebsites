"""
Seed Data Script - Sample Products for Testing

Creates sample data for different site types:
1. E-commerce Store (clothing)
2. Food Delivery (restaurant menu)
3. Services (salon/spa)

Usage:
    python seed_products.py --site-id <uuid> --site-type <store|food|salon>
"""

import asyncio
import sys
from uuid import UUID
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
import argparse
import logging

from app.database import get_db_direct
from app.models import Category, Product, ProductVariant
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ======================
# E-COMMERCE STORE DATA
# ======================

STORE_CATEGORIES = [
    {
        "name": "Men's Clothing",
        "slug": "mens-clothing",
        "description": "Fashion for men",
        "children": [
            {"name": "T-Shirts", "slug": "mens-tshirts", "description": "Casual t-shirts"},
            {"name": "Shirts", "slug": "mens-shirts", "description": "Formal and casual shirts"},
            {"name": "Jeans", "slug": "mens-jeans", "description": "Denim jeans"}
        ]
    },
    {
        "name": "Women's Clothing",
        "slug": "womens-clothing",
        "description": "Fashion for women",
        "children": [
            {"name": "Dresses", "slug": "womens-dresses", "description": "Casual and formal dresses"},
            {"name": "Tops", "slug": "womens-tops", "description": "Trendy tops"},
            {"name": "Jeans", "slug": "womens-jeans", "description": "Denim jeans"}
        ]
    },
    {
        "name": "Accessories",
        "slug": "accessories",
        "description": "Fashion accessories",
        "children": [
            {"name": "Bags", "slug": "bags", "description": "Handbags and backpacks"},
            {"name": "Watches", "slug": "watches", "description": "Watches and timepieces"}
        ]
    }
]

STORE_PRODUCTS = [
    {
        "category": "mens-tshirts",
        "name": "Classic Cotton T-Shirt",
        "slug": "classic-cotton-tshirt",
        "sku": "TSH-001",
        "short_description": "Comfortable cotton t-shirt for everyday wear",
        "description": "High-quality 100% cotton t-shirt. Breathable, soft, and durable. Perfect for casual outings.",
        "price": Decimal("499.00"),
        "compare_at_price": Decimal("699.00"),
        "images": ["/images/tshirt-white.jpg", "/images/tshirt-black.jpg"],
        "tags": ["cotton", "casual", "bestseller"],
        "is_featured": True,
        "track_inventory": True,
        "stock_quantity": 100,
        "variants": [
            {"name": "White - Small", "sku": "TSH-001-WH-S", "options": {"color": "White", "size": "S"}, "stock": 20},
            {"name": "White - Medium", "sku": "TSH-001-WH-M", "options": {"color": "White", "size": "M"}, "stock": 30},
            {"name": "White - Large", "sku": "TSH-001-WH-L", "options": {"color": "White", "size": "L"}, "stock": 25},
            {"name": "Black - Small", "sku": "TSH-001-BK-S", "options": {"color": "Black", "size": "S"}, "stock": 15},
            {"name": "Black - Medium", "sku": "TSH-001-BK-M", "options": {"color": "Black", "size": "M"}, "stock": 25},
            {"name": "Black - Large", "sku": "TSH-001-BK-L", "options": {"color": "Black", "size": "L"}, "stock": 20}
        ]
    },
    {
        "category": "mens-shirts",
        "name": "Formal Check Shirt",
        "slug": "formal-check-shirt",
        "sku": "SHT-001",
        "short_description": "Premium cotton check shirt for formal occasions",
        "description": "Elegant check pattern shirt made from premium cotton. Perfect for office and formal events.",
        "price": Decimal("1299.00"),
        "compare_at_price": Decimal("1799.00"),
        "images": ["/images/shirt-blue.jpg", "/images/shirt-white.jpg"],
        "tags": ["formal", "cotton", "check"],
        "is_featured": True,
        "track_inventory": True,
        "stock_quantity": 50,
        "variants": [
            {"name": "Blue - Small", "sku": "SHT-001-BL-S", "options": {"color": "Blue", "size": "S"}, "stock": 10},
            {"name": "Blue - Medium", "sku": "SHT-001-BL-M", "options": {"color": "Blue", "size": "M"}, "stock": 15},
            {"name": "Blue - Large", "sku": "SHT-001-BL-L", "options": {"color": "Blue", "size": "L"}, "stock": 10}
        ]
    },
    {
        "category": "womens-dresses",
        "name": "Floral Summer Dress",
        "slug": "floral-summer-dress",
        "sku": "DRS-001",
        "short_description": "Light and breezy floral dress for summer",
        "description": "Beautiful floral print dress. Lightweight fabric perfect for summer. Available in multiple patterns.",
        "price": Decimal("1599.00"),
        "images": ["/images/dress-floral.jpg"],
        "tags": ["summer", "floral", "casual"],
        "is_featured": True,
        "track_inventory": True,
        "stock_quantity": 30
    },
    {
        "category": "bags",
        "name": "Leather Crossbody Bag",
        "slug": "leather-crossbody-bag",
        "sku": "BAG-001",
        "short_description": "Genuine leather crossbody bag",
        "description": "Handcrafted genuine leather crossbody bag. Multiple compartments. Available in black and brown.",
        "price": Decimal("2499.00"),
        "compare_at_price": Decimal("3499.00"),
        "images": ["/images/bag-black.jpg", "/images/bag-brown.jpg"],
        "tags": ["leather", "accessories", "bestseller"],
        "is_featured": True,
        "track_inventory": True,
        "stock_quantity": 20
    }
]


# ======================
# FOOD DELIVERY DATA
# ======================

FOOD_CATEGORIES = [
    {
        "name": "Starters",
        "slug": "starters",
        "description": "Appetizers and starters",
        "children": [
            {"name": "Veg Starters", "slug": "veg-starters", "description": "Vegetarian appetizers"},
            {"name": "Non-Veg Starters", "slug": "nonveg-starters", "description": "Non-vegetarian appetizers"}
        ]
    },
    {
        "name": "Main Course",
        "slug": "main-course",
        "description": "Main dishes",
        "children": [
            {"name": "Veg Curries", "slug": "veg-curries", "description": "Vegetarian curries"},
            {"name": "Non-Veg Curries", "slug": "nonveg-curries", "description": "Non-vegetarian curries"},
            {"name": "Rice & Biryani", "slug": "rice-biryani", "description": "Rice dishes and biryani"}
        ]
    },
    {
        "name": "Breads",
        "slug": "breads",
        "description": "Indian breads"
    },
    {
        "name": "Desserts",
        "slug": "desserts",
        "description": "Sweet dishes"
    },
    {
        "name": "Beverages",
        "slug": "beverages",
        "description": "Drinks and beverages"
    }
]

FOOD_PRODUCTS = [
    {
        "category": "veg-starters",
        "name": "Paneer Tikka",
        "slug": "paneer-tikka",
        "sku": "FOOD-001",
        "short_description": "Grilled cottage cheese with spices",
        "description": "Marinated cottage cheese cubes grilled to perfection. Served with mint chutney.",
        "price": Decimal("299.00"),
        "images": ["/images/paneer-tikka.jpg"],
        "tags": ["vegetarian", "starter", "popular"],
        "is_featured": True,
        "track_inventory": False,
        "allow_backorder": True,
        "attributes": {"serves": "2", "spice_level": "medium", "dietary": "vegetarian"}
    },
    {
        "category": "nonveg-starters",
        "name": "Chicken Tikka",
        "slug": "chicken-tikka",
        "sku": "FOOD-002",
        "short_description": "Grilled chicken with Indian spices",
        "description": "Tender chicken pieces marinated in yogurt and spices, grilled in tandoor.",
        "price": Decimal("349.00"),
        "images": ["/images/chicken-tikka.jpg"],
        "tags": ["non-vegetarian", "starter", "popular"],
        "is_featured": True,
        "track_inventory": False,
        "allow_backorder": True,
        "attributes": {"serves": "2", "spice_level": "high", "dietary": "non-vegetarian"}
    },
    {
        "category": "veg-curries",
        "name": "Palak Paneer",
        "slug": "palak-paneer",
        "sku": "FOOD-003",
        "short_description": "Cottage cheese in spinach gravy",
        "description": "Fresh cottage cheese cubes cooked in creamy spinach gravy with mild spices.",
        "price": Decimal("279.00"),
        "images": ["/images/palak-paneer.jpg"],
        "tags": ["vegetarian", "curry", "healthy"],
        "is_featured": True,
        "track_inventory": False,
        "allow_backorder": True,
        "attributes": {"serves": "2", "spice_level": "low", "dietary": "vegetarian"}
    },
    {
        "category": "rice-biryani",
        "name": "Hyderabadi Chicken Biryani",
        "slug": "chicken-biryani",
        "sku": "FOOD-004",
        "short_description": "Aromatic basmati rice with chicken",
        "description": "Authentic Hyderabadi biryani with tender chicken pieces, fragrant basmati rice, and exotic spices.",
        "price": Decimal("399.00"),
        "images": ["/images/chicken-biryani.jpg"],
        "tags": ["non-vegetarian", "biryani", "bestseller"],
        "is_featured": True,
        "track_inventory": False,
        "allow_backorder": True,
        "attributes": {"serves": "1", "spice_level": "medium", "dietary": "non-vegetarian"},
        "variants": [
            {"name": "Regular", "sku": "FOOD-004-REG", "options": {"portion": "Regular"}, "price": Decimal("399.00")},
            {"name": "Family Pack", "sku": "FOOD-004-FAM", "options": {"portion": "Family"}, "price": Decimal("799.00")}
        ]
    },
    {
        "category": "breads",
        "name": "Butter Naan",
        "slug": "butter-naan",
        "sku": "FOOD-005",
        "short_description": "Soft Indian bread with butter",
        "description": "Freshly baked naan bread brushed with butter. Perfect with curries.",
        "price": Decimal("49.00"),
        "images": ["/images/naan.jpg"],
        "tags": ["vegetarian", "bread"],
        "is_featured": False,
        "track_inventory": False,
        "allow_backorder": True,
        "attributes": {"serves": "1", "dietary": "vegetarian"}
    },
    {
        "category": "desserts",
        "name": "Gulab Jamun (2 pcs)",
        "slug": "gulab-jamun",
        "sku": "FOOD-006",
        "short_description": "Traditional Indian sweet",
        "description": "Soft milk solids dumplings soaked in sugar syrup. Served warm.",
        "price": Decimal("79.00"),
        "images": ["/images/gulab-jamun.jpg"],
        "tags": ["vegetarian", "dessert", "sweet"],
        "is_featured": False,
        "track_inventory": False,
        "allow_backorder": True,
        "attributes": {"serves": "1", "dietary": "vegetarian"}
    }
]


# ======================
# SALON/SPA SERVICES DATA
# ======================

SALON_CATEGORIES = [
    {
        "name": "Hair Services",
        "slug": "hair-services",
        "description": "Hair care and styling",
        "children": [
            {"name": "Haircuts", "slug": "haircuts", "description": "Hair cutting services"},
            {"name": "Hair Color", "slug": "hair-color", "description": "Hair coloring services"},
            {"name": "Hair Treatments", "slug": "hair-treatments", "description": "Hair care treatments"}
        ]
    },
    {
        "name": "Skin Services",
        "slug": "skin-services",
        "description": "Skin care treatments",
        "children": [
            {"name": "Facials", "slug": "facials", "description": "Facial treatments"},
            {"name": "Cleanup", "slug": "cleanup", "description": "Skin cleanup"}
        ]
    },
    {
        "name": "Spa Services",
        "slug": "spa-services",
        "description": "Relaxation and wellness",
        "children": [
            {"name": "Massage", "slug": "massage", "description": "Body massage"},
            {"name": "Body Treatments", "slug": "body-treatments", "description": "Body care"}
        ]
    }
]

SALON_PRODUCTS = [
    {
        "category": "haircuts",
        "name": "Women's Haircut",
        "slug": "womens-haircut",
        "sku": "SAL-001",
        "short_description": "Professional haircut for women",
        "description": "Expert haircut tailored to your face shape and style preferences. Includes wash and basic styling.",
        "price": Decimal("599.00"),
        "images": ["/images/haircut-women.jpg"],
        "tags": ["haircut", "women", "popular"],
        "is_featured": True,
        "track_inventory": False,
        "allow_backorder": True,
        "attributes": {"duration": "45 mins", "gender": "female"}
    },
    {
        "category": "haircuts",
        "name": "Men's Haircut",
        "slug": "mens-haircut",
        "sku": "SAL-002",
        "short_description": "Professional haircut for men",
        "description": "Classic or modern haircut for men. Includes hair wash and styling.",
        "price": Decimal("399.00"),
        "images": ["/images/haircut-men.jpg"],
        "tags": ["haircut", "men", "popular"],
        "is_featured": True,
        "track_inventory": False,
        "allow_backorder": True,
        "attributes": {"duration": "30 mins", "gender": "male"}
    },
    {
        "category": "hair-color",
        "name": "Global Hair Color",
        "slug": "global-hair-color",
        "sku": "SAL-003",
        "short_description": "Full hair coloring",
        "description": "Complete hair color transformation using premium international brands. Includes toner and conditioning treatment.",
        "price": Decimal("2999.00"),
        "images": ["/images/hair-color.jpg"],
        "tags": ["color", "premium"],
        "is_featured": True,
        "track_inventory": False,
        "allow_backorder": True,
        "attributes": {"duration": "120 mins"}
    },
    {
        "category": "facials",
        "name": "Gold Facial",
        "slug": "gold-facial",
        "sku": "SAL-004",
        "short_description": "Luxury gold facial treatment",
        "description": "Premium facial treatment with 24k gold. Deep cleansing, exfoliation, and hydration. Leaves skin glowing.",
        "price": Decimal("1999.00"),
        "images": ["/images/gold-facial.jpg"],
        "tags": ["facial", "premium", "popular"],
        "is_featured": True,
        "track_inventory": False,
        "allow_backorder": True,
        "attributes": {"duration": "60 mins"}
    },
    {
        "category": "massage",
        "name": "Full Body Massage",
        "slug": "full-body-massage",
        "sku": "SAL-005",
        "short_description": "Relaxing full body massage",
        "description": "Complete body massage with aromatic oils. Relieves stress and muscle tension. Choose from Swedish, Thai, or Deep Tissue.",
        "price": Decimal("2499.00"),
        "images": ["/images/massage.jpg"],
        "tags": ["massage", "spa", "relaxation"],
        "is_featured": True,
        "track_inventory": False,
        "allow_backorder": True,
        "attributes": {"duration": "90 mins"},
        "variants": [
            {"name": "Swedish Massage", "sku": "SAL-005-SWE", "options": {"type": "Swedish"}, "price": Decimal("2499.00")},
            {"name": "Thai Massage", "sku": "SAL-005-THI", "options": {"type": "Thai"}, "price": Decimal("2999.00")},
            {"name": "Deep Tissue", "sku": "SAL-005-DT", "options": {"type": "Deep Tissue"}, "price": Decimal("3499.00")}
        ]
    }
]


async def create_categories(db: AsyncSession, site_id: UUID, categories_data: list, parent_id=None):
    """Recursively create categories and subcategories"""
    category_map = {}

    for cat_data in categories_data:
        category = Category(
            site_id=site_id,
            parent_id=parent_id,
            name=cat_data["name"],
            slug=cat_data["slug"],
            description=cat_data.get("description"),
            is_active=True
        )

        db.add(category)
        await db.flush()
        await db.refresh(category)

        category_map[cat_data["slug"]] = category

        logger.info(f"Created category: {category.name}")

        # Create children
        if "children" in cat_data:
            child_map = await create_categories(db, site_id, cat_data["children"], category.category_id)
            category_map.update(child_map)

    return category_map


async def create_products(db: AsyncSession, site_id: UUID, products_data: list, category_map: dict):
    """Create products with variants"""
    for prod_data in products_data:
        category = category_map.get(prod_data["category"])
        if not category:
            logger.warning(f"Category not found: {prod_data['category']}")
            continue

        product = Product(
            site_id=site_id,
            category_id=category.category_id,
            name=prod_data["name"],
            slug=prod_data["slug"],
            sku=prod_data["sku"],
            short_description=prod_data.get("short_description"),
            description=prod_data.get("description"),
            price=prod_data["price"],
            compare_at_price=prod_data.get("compare_at_price"),
            images=prod_data.get("images", []),
            tags=prod_data.get("tags", []),
            is_featured=prod_data.get("is_featured", False),
            is_active=True,
            track_inventory=prod_data.get("track_inventory", False),
            allow_backorder=prod_data.get("allow_backorder", False),
            stock_quantity=prod_data.get("stock_quantity", 0),
            attributes=prod_data.get("attributes", {})
        )

        db.add(product)
        await db.flush()
        await db.refresh(product)

        logger.info(f"Created product: {product.name}")

        # Create variants
        if "variants" in prod_data:
            for var_data in prod_data["variants"]:
                variant = ProductVariant(
                    product_id=product.product_id,
                    name=var_data["name"],
                    sku=var_data["sku"],
                    options=var_data.get("options", {}),
                    price=var_data.get("price"),
                    stock_quantity=var_data.get("stock", 0),
                    is_active=True
                )

                db.add(variant)
                logger.info(f"  - Created variant: {variant.name}")

    await db.flush()


async def seed_data(site_id: UUID, site_type: str):
    """Main seed function"""
    logger.info(f"Seeding data for site {site_id} (type: {site_type})")

    # Select data based on site type
    if site_type == "store":
        categories_data = STORE_CATEGORIES
        products_data = STORE_PRODUCTS
    elif site_type == "food":
        categories_data = FOOD_CATEGORIES
        products_data = FOOD_PRODUCTS
    elif site_type == "salon":
        categories_data = SALON_CATEGORIES
        products_data = SALON_PRODUCTS
    else:
        logger.error(f"Unknown site type: {site_type}")
        return

    # Get database session
    async for db in get_db_direct():
        try:
            # Create categories
            logger.info("Creating categories...")
            category_map = await create_categories(db, site_id, categories_data)

            # Create products
            logger.info("Creating products...")
            await create_products(db, site_id, products_data, category_map)

            # Commit
            await db.commit()
            logger.info("Seed data created successfully!")

        except Exception as e:
            await db.rollback()
            logger.error(f"Error seeding data: {e}")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed product data")
    parser.add_argument("--site-id", required=True, help="Site UUID")
    parser.add_argument("--site-type", required=True, choices=["store", "food", "salon"],
                        help="Site type (store, food, salon)")

    args = parser.parse_args()

    try:
        site_id = UUID(args.site_id)
    except ValueError:
        logger.error("Invalid site ID format")
        sys.exit(1)

    asyncio.run(seed_data(site_id, args.site_type))
