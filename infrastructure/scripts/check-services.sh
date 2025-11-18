#!/bin/bash
# Quick health check for all services

echo "🏥 Platform Health Check"
echo ""

services=(
    "Site Service:8010"
    "Storefront:8011"
    "Booking:8012"
    "Lead:8013"
    "Content:8014"
    "Widget:8015"
)

for service in "${services[@]}"; do
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    
    response=$(curl -s http://localhost:$port/health 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        status=$(echo $response | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        echo "✓ $name: $status"
    else
        echo "✗ $name: not responding"
    fi
done

echo ""
echo "Infrastructure:"
docker-compose ps postgres redis rabbitmq 2>/dev/null | grep -E "(postgres|redis|rabbitmq)" || echo "Run 'docker-compose ps' to check infrastructure"
