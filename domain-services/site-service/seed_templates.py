"""
Seed script to create default templates

Run this after starting the service to populate templates.
"""

import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import Template

# Create async engine
engine = create_async_engine(settings.DATABASE_URL)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed_templates():
    """Create default templates"""

    templates = [
        # Departmental Store Template
        {
            "template_name": "Modern Store",
            "site_type": "departmental_store",
            "layout_config": {
                "sections": [
                    {
                        "type": "hero",
                        "props": {
                            "title": "Welcome to Our Store",
                            "subtitle": "Quality products at great prices",
                            "cta_text": "Shop Now",
                            "cta_link": "/products",
                            "background_image": "https://images.unsplash.com/photo-1604719312566-8912e9227c6a",
                        }
                    },
                    {
                        "type": "product_grid",
                        "props": {
                            "columns": 3,
                            "show_price": True,
                            "show_add_to_cart": True
                        }
                    },
                    {
                        "type": "testimonials",
                        "props": {
                            "layout": "grid",
                            "columns": 3
                        }
                    },
                    {
                        "type": "contact_form",
                        "props": {
                            "fields": ["name", "email", "phone", "message"]
                        }
                    }
                ]
            },
            "style_config": {
                "primary_color": "#3b82f6",
                "secondary_color": "#10b981",
                "font_family": "Inter, sans-serif"
            },
            "is_premium": False
        },

        # Salon Template
        {
            "template_name": "Elegant Salon",
            "site_type": "salon",
            "layout_config": {
                "sections": [
                    {
                        "type": "hero",
                        "props": {
                            "title": "Beauty & Wellness",
                            "subtitle": "Expert care for your perfect look",
                            "cta_text": "Book Appointment",
                            "cta_link": "/booking",
                            "background_image": "https://images.unsplash.com/photo-1560066984-138dadb4c035",
                        }
                    },
                    {
                        "type": "service_grid",
                        "props": {
                            "columns": 3,
                            "show_price": True,
                            "show_duration": True
                        }
                    },
                    {
                        "type": "staff_profiles",
                        "props": {
                            "layout": "carousel"
                        }
                    },
                    {
                        "type": "booking_calendar",
                        "props": {
                            "view": "week"
                        }
                    },
                    {
                        "type": "testimonials",
                        "props": {
                            "layout": "grid",
                            "columns": 2
                        }
                    }
                ]
            },
            "style_config": {
                "primary_color": "#ec4899",
                "secondary_color": "#8b5cf6",
                "font_family": "Playfair Display, serif"
            },
            "is_premium": False
        },

        # Tiffin Service Template
        {
            "template_name": "Fresh Tiffin",
            "site_type": "tiffin_service",
            "layout_config": {
                "sections": [
                    {
                        "type": "hero",
                        "props": {
                            "title": "Homemade Meals Delivered",
                            "subtitle": "Healthy, delicious tiffin service",
                            "cta_text": "View Menu",
                            "cta_link": "/menu",
                            "background_image": "https://images.unsplash.com/photo-1504674900247-0877df9cc836",
                        }
                    },
                    {
                        "type": "product_grid",
                        "props": {
                            "columns": 2,
                            "show_price": True
                        }
                    },
                    {
                        "type": "pricing",
                        "props": {
                            "plans": []
                        }
                    },
                    {
                        "type": "testimonials",
                        "props": {
                            "layout": "carousel"
                        }
                    },
                    {
                        "type": "whatsapp_button",
                        "props": {
                            "position": "bottom-right"
                        }
                    }
                ]
            },
            "style_config": {
                "primary_color": "#10b981",
                "secondary_color": "#f59e0b",
                "font_family": "Poppins, sans-serif"
            },
            "is_premium": False
        },

        # Coaching Center Template
        {
            "template_name": "Modern Coaching",
            "site_type": "coaching_center",
            "layout_config": {
                "sections": [
                    {
                        "type": "hero",
                        "props": {
                            "title": "Unlock Your Potential",
                            "subtitle": "Expert coaching for success",
                            "cta_text": "Explore Courses",
                            "cta_link": "/courses",
                            "background_image": "https://images.unsplash.com/photo-1503676260728-1c00da094a0b",
                        }
                    },
                    {
                        "type": "service_grid",
                        "props": {
                            "columns": 3,
                            "show_price": True
                        }
                    },
                    {
                        "type": "staff_profiles",
                        "props": {
                            "layout": "grid"
                        }
                    },
                    {
                        "type": "testimonials",
                        "props": {
                            "layout": "grid",
                            "columns": 3
                        }
                    },
                    {
                        "type": "lead_form",
                        "props": {
                            "fields": ["name", "phone", "course_interest"]
                        }
                    }
                ]
            },
            "style_config": {
                "primary_color": "#4f46e5",
                "secondary_color": "#06b6d4",
                "font_family": "Roboto, sans-serif"
            },
            "is_premium": False
        }
    ]

    async with AsyncSessionLocal() as session:
        for template_data in templates:
            # Check if template already exists
            existing = await session.execute(
                "SELECT template_id FROM templates WHERE template_name = :name",
                {"name": template_data["template_name"]}
            )

            if not existing.scalar():
                template = Template(
                    template_id=uuid.uuid4(),
                    **template_data
                )
                session.add(template)
                print(f"Created template: {template_data['template_name']}")
            else:
                print(f"Template already exists: {template_data['template_name']}")

        await session.commit()

    print("\nTemplates seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed_templates())
