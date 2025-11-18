#!/bin/bash
# Initialize the entire platform
# This script sets up all databases, seeds initial data, and verifies services

set -e

echo "🚀 Initializing Multi-Website Platform..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Wait for services to be ready
echo -e "${BLUE}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Check PostgreSQL
echo -e "${BLUE}📊 Checking PostgreSQL...${NC}"
docker-compose exec -T postgres psql -U platform_user -c "SELECT 1" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PostgreSQL is ready${NC}"
else
    echo -e "${YELLOW}⚠ PostgreSQL not ready yet, waiting...${NC}"
    sleep 5
fi

# Check Redis
echo -e "${BLUE}📮 Checking Redis...${NC}"
docker-compose exec -T redis redis-cli ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Redis is ready${NC}"
else
    echo -e "${YELLOW}⚠ Redis not ready yet${NC}"
fi

# Wait for all services to be healthy
echo -e "${BLUE}⏳ Waiting for all services to be healthy (30s)...${NC}"
sleep 30

# Check each service health
echo ""
echo -e "${BLUE}🏥 Health Check Summary:${NC}"
echo ""

services=("site-service:8010" "storefront-service:8011" "booking-service:8012" "lead-service:8013" "content-service:8014" "widget-service:8015")

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$port/health 2>/dev/null || echo "000")
    
    if [ "$status" = "200" ]; then
        echo -e "${GREEN}✓${NC} $name (port $port): healthy"
    else
        echo -e "${YELLOW}⚠${NC} $name (port $port): not responding (status: $status)"
    fi
done

echo ""
echo -e "${GREEN}✓ Platform initialization complete!${NC}"
echo ""
echo -e "${BLUE}📚 Service URLs:${NC}"
echo "  Site Service:       http://localhost:8010/docs"
echo "  Storefront Service: http://localhost:8011/docs"
echo "  Booking Service:    http://localhost:8012/docs"
echo "  Lead Service:       http://localhost:8013/docs"
echo "  Content Service:    http://localhost:8014/docs"
echo "  Widget Service:     http://localhost:8015/docs"
echo ""
echo -e "${BLUE}🔧 Infrastructure:${NC}"
echo "  PostgreSQL:         localhost:5432"
echo "  Redis:              localhost:6379"
echo "  RabbitMQ Admin:     http://localhost:15672 (platform/platform123)"
echo ""
echo -e "${YELLOW}💡 Next steps:${NC}"
echo "  1. Seed sample data: ./infrastructure/scripts/seed-all-data.sh"
echo "  2. Create your first site via Site Service API"
echo "  3. Check the API documentation at each service's /docs endpoint"
echo ""
