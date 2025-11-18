#!/bin/bash
# Seed sample data for all services
# Creates a complete demo environment

set -e

echo "🌱 Seeding sample data for all services..."
echo ""

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

# Generate a demo site ID (you can change this)
DEMO_SITE_ID="00000000-0000-0000-0000-000000000001"

echo -e "${BLUE}📝 Seeding Site Service templates...${NC}"
docker-compose exec -T site-service python seed_templates.py 2>/dev/null || echo "Templates seed script not found or already seeded"
echo -e "${GREEN}✓ Site templates seeded${NC}"
echo ""

echo -e "${BLUE}🛍️  Seeding Storefront Service (store type)...${NC}"
docker-compose exec -T storefront-service python seed_products.py --site-id $DEMO_SITE_ID --site-type store 2>/dev/null || echo "Products seed script not found"
echo -e "${GREEN}✓ Store products seeded${NC}"
echo ""

echo -e "${BLUE}💇 Seeding Booking Service (salon type)...${NC}"
docker-compose exec -T booking-service python seed_data.py --site-id $DEMO_SITE_ID --business-type salon 2>/dev/null || echo "Booking seed script not found"
echo -e "${GREEN}✓ Salon services and providers seeded${NC}"
echo ""

echo -e "${GREEN}✓ All sample data seeded!${NC}"
echo ""
echo "Demo Site ID: $DEMO_SITE_ID"
echo ""
echo "You can now:"
echo "  - Browse products at http://localhost:8011/docs"
echo "  - Check available booking slots at http://localhost:8012/docs"
echo "  - Create test orders and bookings"
