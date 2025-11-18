# Quick Start Guide

Get the entire multi-website platform running in 5 minutes!

## Prerequisites

- Docker & Docker Compose installed
- 8GB+ RAM recommended
- Ports 5432, 6379, 8010-8015, 15672 available

## 🚀 Option 1: Quick Start (Automated)

```bash
# 1. Clone the repository
cd beautifulwebsites

# 2. Start all services
docker-compose up -d

# 3. Wait for services to initialize (30 seconds)
# Then run the initialization script
./infrastructure/scripts/init-platform.sh

# 4. (Optional) Seed sample data
./infrastructure/scripts/seed-all-data.sh
```

That's it! All services are now running.

## 🔍 Verify Everything Works

```bash
# Check all services
./infrastructure/scripts/check-services.sh

# Or manually:
curl http://localhost:8010/health  # Site Service
curl http://localhost:8011/health  # Storefront Service
curl http://localhost:8012/health  # Booking Service
curl http://localhost:8013/health  # Lead Service
curl http://localhost:8014/health  # Content Service
curl http://localhost:8015/health  # Widget Service
```

## 📚 Access API Documentation

Each service has interactive API docs (Swagger UI):

- **Site Service**: http://localhost:8010/docs
- **Storefront Service**: http://localhost:8011/docs  
- **Booking Service**: http://localhost:8012/docs
- **Lead Service**: http://localhost:8013/docs
- **Content Service**: http://localhost:8014/docs
- **Widget Service**: http://localhost:8015/docs

## 🛠️ Infrastructure Access

- **PostgreSQL**: `localhost:5432` (user: `platform_user`, pass: `platform_pass`)
- **Redis**: `localhost:6379`
- **RabbitMQ Admin**: http://localhost:15672 (user: `platform`, pass: `platform123`)

## 📖 Common Tasks

### Create Your First Site

```bash
# Using curl
curl -X POST http://localhost:8010/api/v1/sites \
  -H "Content-Type: application/json" \
  -d '{
    "org_id": "your-org-uuid",
    "slug": "my-awesome-store",
    "site_type": "ecommerce",
    "template_id": "template-uuid",
    "branding": {
      "business_name": "My Store",
      "primary_color": "#007bff"
    }
  }'
```

Or use the Swagger UI at http://localhost:8010/docs

### Add Products to Your Store

```bash
# First, create a category
curl -X POST http://localhost:8011/api/v1/catalog/{site_id}/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Electronics",
    "slug": "electronics"
  }'

# Then add a product
curl -X POST http://localhost:8011/api/v1/catalog/{site_id}/products \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": "category-uuid",
    "name": "Wireless Headphones",
    "slug": "wireless-headphones",
    "price": 99.99,
    "stock_quantity": 100
  }'
```

### Check Available Booking Slots

```bash
curl -X POST http://localhost:8012/api/v1/{site_id}/availability \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": "service-uuid",
    "date": "2025-01-20"
  }'
```

### Create a Booking

```bash
curl -X POST http://localhost:8012/api/v1/{site_id}/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": "service-uuid",
    "provider_id": "provider-uuid",
    "booking_date": "2025-01-20",
    "start_time": "10:00",
    "customer_name": "John Doe",
    "customer_phone": "+1234567890",
    "customer_email": "john@example.com"
  }'
```

## 🐛 Troubleshooting

### Services not starting?

```bash
# Check logs
docker-compose logs -f [service-name]

# Restart a specific service
docker-compose restart storefront-service

# Rebuild if you made code changes
docker-compose up -d --build
```

### Database connection issues?

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Manually test connection
docker-compose exec postgres psql -U platform_user -d storefront_service_db
```

### Port already in use?

```bash
# Check what's using the port
lsof -i :8010  # Replace with your port

# Or change the port in docker-compose.yml
ports:
  - "9010:8010"  # Maps host port 9010 to container port 8010
```

## 🛑 Stopping the Platform

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes all data)
docker-compose down -v
```

## 🔄 Development Workflow

### Making code changes

```bash
# 1. Edit code in domain-services/[service-name]/

# 2. Rebuild and restart that service
docker-compose up -d --build [service-name]

# 3. Check logs
docker-compose logs -f [service-name]
```

### Running services locally (without Docker)

```bash
# Example for Storefront Service
cd domain-services/storefront-service

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL=postgresql+asyncpg://platform_user:platform_pass@localhost:5432/storefront_service_db

# Run the service
python -m app.main
```

## 📊 Database Management

### Access database directly

```bash
docker-compose exec postgres psql -U platform_user -d storefront_service_db
```

### Backup a database

```bash
docker-compose exec postgres pg_dump -U platform_user storefront_service_db > backup.sql
```

### Restore a database

```bash
cat backup.sql | docker-compose exec -T postgres psql -U platform_user -d storefront_service_db
```

## 🎯 Next Steps

1. **Explore the APIs**: Visit each service's `/docs` endpoint
2. **Read the Architecture**: Check `ARCHITECTURE.md` for design details
3. **Build a Frontend**: Use the APIs to build your frontend with Next.js, React, etc.
4. **Customize**: Modify the services to fit your specific needs
5. **Deploy**: See `DEPLOYMENT.md` for production deployment guide

## 💡 Pro Tips

- Use the RabbitMQ management UI to monitor event flows
- Check Redis for cached data and event streams
- Use the seed scripts to quickly populate test data
- Each service has comprehensive logging - check the logs when debugging
- Use the health check endpoints to verify service status

## 🆘 Need Help?

- Check the comprehensive `ARCHITECTURE.md` for design details
- Review individual service READMEs in `domain-services/*/README.md`
- Check `IMPLEMENTATION_COMPLETE.md` for implementation details
- Look at API documentation at `http://localhost:PORT/docs`

---

**Happy Building! 🚀**
