# Storefront Service

**Port:** 8011
**Purpose:** Comprehensive e-commerce backend for multi-website platform

The Storefront Service provides complete e-commerce functionality including product catalog, shopping cart, order processing, and inventory management. It supports multiple site types (stores, food delivery, service bookings) with a flexible, multi-tenant architecture.

---

## 🎯 Features

### Product Catalog Management
- **Hierarchical Categories**: Unlimited nesting with parent-child relationships
- **Products**: Full product management with variants (size, color, options)
- **Search & Filtering**: Advanced product search with multiple filters
- **Inventory Tracking**: Real-time stock management with history
- **Product Variants**: Support for size, color, and custom options
- **Flexible Attributes**: JSONB-based custom product attributes
- **SEO-Friendly**: URL slugs for products and categories

### Shopping Cart
- **Guest Carts**: Anonymous shopping via session ID
- **User Carts**: Persistent carts for authenticated users
- **Cart Merging**: Automatic merge on user login
- **Auto-Expiry**: Configurable cart expiration
- **Real-time Totals**: Automatic calculation of subtotal, tax, discounts

### Order Processing
- **Order Placement**: Create orders from cart with validation
- **Order Lifecycle**: Managed status workflow (placed → confirmed → preparing → dispatched → delivered)
- **Inventory Deduction**: Automatic stock reduction on order
- **Order History**: Complete audit trail of status changes
- **Cancellation**: Order cancellation with inventory restoration
- **Product Snapshots**: Historical data preservation

### Notifications & Events
- **CloudEvents**: Event publishing for notifications
- **Order Events**: Order placed, status changed, delivered, cancelled
- **Inventory Alerts**: Low stock and out-of-stock notifications
- **Cart Events**: Abandoned cart recovery

### Multi-Tenant Architecture
- **Site Isolation**: Complete data isolation via `site_id`
- **Multi-Site Support**: Single instance serves multiple websites
- **Flexible Configuration**: Per-site customization

---

## 📁 Project Structure

```
storefront-service/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── config.py                  # Configuration settings
│   ├── database.py                # Database connection
│   ├── models.py                  # SQLAlchemy models (9 tables)
│   ├── schemas.py                 # Pydantic schemas (25+ schemas)
│   │
│   ├── routers/                   # API endpoints
│   │   ├── products.py            # Catalog endpoints (15 endpoints)
│   │   ├── cart.py                # Cart endpoints (9 endpoints)
│   │   └── orders.py              # Order endpoints (8 endpoints)
│   │
│   ├── services/                  # Business logic
│   │   ├── product_service.py     # Product/category/variant logic
│   │   ├── cart_service.py        # Cart operations
│   │   ├── order_service.py       # Order processing
│   │   └── event_service.py       # Event publishing
│   │
│   └── middleware/                # Cross-cutting concerns
│       └── auth.py                # JWT authentication
│
├── seed_products.py               # Sample data generator
├── Dockerfile                     # Container image
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## 🗄️ Database Schema

### Core Tables

#### **categories**
Hierarchical product categories with parent-child relationships.

**Key Fields:**
- `category_id` (UUID, PK)
- `site_id` (UUID, FK to sites)
- `parent_id` (UUID, self-referencing FK)
- `name`, `slug`, `description`
- `is_active`

**Indexes:**
- `site_id`, `slug`
- `parent_id`

#### **products**
Product catalog with flexible attributes.

**Key Fields:**
- `product_id` (UUID, PK)
- `site_id` (UUID, FK to sites)
- `category_id` (UUID, FK to categories)
- `name`, `slug`, `sku`
- `price`, `compare_at_price`
- `images` (JSONB array)
- `tags` (JSONB array)
- `attributes` (JSONB) - flexible custom attributes
- `stock_quantity`
- `track_inventory`, `allow_backorder`
- `is_featured`, `is_active`

**Indexes:**
- `site_id`, `category_id`
- `slug`, `sku`
- `is_active`, `is_featured`
- GIN index on `tags` for array queries

#### **product_variants**
Product variations (size, color, etc.) with separate pricing and inventory.

**Key Fields:**
- `variant_id` (UUID, PK)
- `product_id` (UUID, FK to products)
- `name`, `sku`
- `options` (JSONB) - e.g., `{"color": "Red", "size": "Large"}`
- `price` (overrides product price if set)
- `stock_quantity`
- `is_active`

#### **carts**
Shopping carts for users and guests.

**Key Fields:**
- `cart_id` (UUID, PK)
- `site_id` (UUID, FK to sites)
- `user_id` (UUID, nullable) - for authenticated users
- `session_id` (String, nullable) - for guests
- `status` (active, converted, abandoned)
- `subtotal`, `tax`, `discount`, `total`
- `expires_at`

**Indexes:**
- `site_id`, `user_id`, `session_id`
- `status`

#### **cart_items**
Items in shopping carts.

**Key Fields:**
- `cart_item_id` (UUID, PK)
- `cart_id` (UUID, FK to carts)
- `product_id` (UUID, FK to products)
- `variant_id` (UUID, nullable, FK to variants)
- `quantity`
- `unit_price`, `total_price`

#### **orders**
Customer orders with full details.

**Key Fields:**
- `order_id` (UUID, PK)
- `site_id` (UUID, FK to sites)
- `user_id` (UUID, nullable)
- `order_number` (unique, e.g., "ORD-20251118-12345")
- `customer_name`, `customer_email`, `customer_phone`
- `delivery_address` (JSONB)
- `subtotal`, `tax`, `delivery_fee`, `discount`, `total`
- `payment_method`, `payment_status`
- `order_status` (placed, confirmed, preparing, dispatched, delivered, cancelled)
- Timestamps: `placed_at`, `confirmed_at`, `dispatched_at`, `delivered_at`, `cancelled_at`

**Indexes:**
- `site_id`, `user_id`
- `order_number` (unique)
- `order_status`, `payment_status`
- `customer_phone` (for order lookup)

#### **order_items**
Products in orders with historical snapshots.

**Key Fields:**
- `order_item_id` (UUID, PK)
- `order_id` (UUID, FK to orders)
- `product_id` (UUID, FK to products)
- `variant_id` (UUID, nullable)
- `product_name`, `product_sku` (snapshot)
- `variant_options` (JSONB, snapshot)
- `product_snapshot` (JSONB) - preserves product data
- `quantity`
- `unit_price`, `total_price`

#### **order_history**
Complete audit trail of order status changes.

**Key Fields:**
- `history_id` (UUID, PK)
- `order_id` (UUID, FK to orders)
- `old_status`, `new_status`
- `notes`
- `changed_by_user_id` (UUID, nullable)
- `created_at`

#### **stock_history**
Inventory movement tracking.

**Key Fields:**
- `history_id` (UUID, PK)
- `product_id` (UUID, FK to products)
- `variant_id` (UUID, nullable)
- `movement_type` (sale, return, adjustment, restock)
- `quantity_change` (negative for deductions)
- `quantity_after`
- `reference_type`, `reference_id` (links to order, etc.)
- `notes`

---

## 🚀 API Endpoints

### Product Catalog (Prefix: `/api/v1/catalog`)

#### Categories
```
POST   /{site_id}/categories                    Create category
GET    /{site_id}/categories                    List categories (with parent filter)
GET    /{site_id}/categories/{category_id}      Get category
PUT    /{site_id}/categories/{category_id}      Update category
DELETE /{site_id}/categories/{category_id}      Delete category (soft delete)
```

#### Products
```
POST   /{site_id}/products                      Create product
GET    /{site_id}/products                      Search products (with filters)
GET    /{site_id}/products/{product_id}         Get product
GET    /{site_id}/products/by-slug/{slug}       Get product by slug
PUT    /{site_id}/products/{product_id}         Update product
DELETE /{site_id}/products/{product_id}         Delete product (soft delete)
```

**Search Filters:**
- `category_id`: Filter by category
- `search`: Full-text search in name/description
- `tags`: Filter by tags (array)
- `min_price`, `max_price`: Price range
- `is_featured`: Featured products only
- `in_stock`: Available products only
- `page`, `page_size`: Pagination (default: 1, 20)
- `sort_by`, `sort_order`: Sorting (default: created_at, desc)

#### Product Variants
```
POST   /{site_id}/products/{product_id}/variants              Create variant
GET    /{site_id}/products/{product_id}/variants              List variants
PUT    /{site_id}/products/{product_id}/variants/{variant_id} Update variant
```

### Shopping Cart (Prefix: `/api/v1`)

```
GET    /{site_id}/cart                          Get or create cart
GET    /{site_id}/cart/{cart_id}                Get cart by ID
POST   /{site_id}/cart/{cart_id}/items          Add item to cart
GET    /{site_id}/cart/{cart_id}/items          List cart items
PUT    /{site_id}/cart/{cart_id}/items/{item_id}  Update cart item quantity
DELETE /{site_id}/cart/{cart_id}/items/{item_id}  Remove cart item
DELETE /{site_id}/cart/{cart_id}/items          Clear cart
POST   /{site_id}/cart/merge                    Merge guest cart into user cart
```

**Headers:**
- `X-Session-ID`: Guest session identifier (for anonymous carts)
- `Authorization`: Bearer token (for authenticated users)

### Orders (Prefix: `/api/v1`)

```
POST   /{site_id}/orders                        Place order
GET    /{site_id}/orders                        List orders (with filters)
GET    /{site_id}/orders/{order_id}             Get order
GET    /{site_id}/orders/by-number/{order_number}  Get order by number
GET    /{site_id}/orders/{order_id}/items       Get order items
PUT    /{site_id}/orders/{order_id}/status      Update order status
POST   /{site_id}/orders/{order_id}/cancel      Cancel order
GET    /{site_id}/orders/{order_id}/history     Get order history
```

**Order Filters:**
- `order_status`: placed, confirmed, preparing, dispatched, delivered, cancelled
- `payment_status`: pending, paid, failed, refunded
- `customer_phone`: Lookup by phone
- `date_from`, `date_to`: Date range
- `page`, `page_size`: Pagination

**Valid Status Transitions:**
```
placed → confirmed, cancelled
confirmed → preparing, cancelled
preparing → dispatched, cancelled
dispatched → delivered, cancelled
delivered → (terminal)
cancelled → (terminal)
```

### Health & Metadata

```
GET    /                   Service information
GET    /health             Health check
GET    /ready              Readiness check (includes DB connectivity)
GET    /docs               OpenAPI documentation (Swagger UI)
```

---

## 🔧 Setup & Installation

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- Redis (for events, optional)
- RabbitMQ (for events, optional)

### 1. Environment Variables

Create `.env` file:

```bash
# Service
SERVICE_NAME=storefront-service
SERVICE_PORT=8011
DEBUG=true
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/storefront_db

# Redis & Events (optional)
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
EVENTS_ENABLED=false

# Cart Settings
DEFAULT_CART_EXPIRY_HOURS=24
MAX_CART_ITEMS=50

# CORS
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]

# Auth Service (for JWT verification)
AUTH_SERVICE_URL=http://auth-service:8001
```

### 2. Install Dependencies

```bash
cd domain-services/storefront-service
pip install -r requirements.txt
```

### 3. Initialize Database

```bash
# Create database
createdb storefront_db

# Run service (auto-creates tables)
python -m app.main
```

### 4. Seed Sample Data

```bash
# For e-commerce store
python seed_products.py --site-id <UUID> --site-type store

# For food delivery
python seed_products.py --site-id <UUID> --site-type food

# For salon/spa
python seed_products.py --site-id <UUID> --site-type salon
```

### 5. Run Service

```bash
# Development
python -m app.main

# Production (with uvicorn)
uvicorn app.main:app --host 0.0.0.0 --port 8011
```

### 6. Docker Deployment

```bash
# Build image
docker build -t storefront-service:latest .

# Run container
docker run -p 8011:8011 \
  -e DATABASE_URL=postgresql+asyncpg://... \
  storefront-service:latest
```

---

## 📝 Usage Examples

### Create Product with Variants

```bash
# 1. Create category
curl -X POST http://localhost:8011/api/v1/catalog/{site_id}/categories \
  -H "Content-Type: application/json" \
  -d '{
    "name": "T-Shirts",
    "slug": "tshirts",
    "description": "Cotton t-shirts"
  }'

# 2. Create product
curl -X POST http://localhost:8011/api/v1/catalog/{site_id}/products \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": "{category_id}",
    "name": "Classic Cotton T-Shirt",
    "slug": "classic-tshirt",
    "sku": "TSH-001",
    "price": 499.00,
    "stock_quantity": 100,
    "track_inventory": true,
    "tags": ["cotton", "casual"]
  }'

# 3. Add variants
curl -X POST http://localhost:8011/api/v1/catalog/{site_id}/products/{product_id}/variants \
  -H "Content-Type: application/json" \
  -d '{
    "name": "White - Medium",
    "sku": "TSH-001-WH-M",
    "options": {"color": "White", "size": "M"},
    "stock_quantity": 30
  }'
```

### Shopping Flow

```bash
# 1. Get or create cart (guest)
curl -X GET http://localhost:8011/api/v1/{site_id}/cart \
  -H "X-Session-ID: guest-12345"

# 2. Add item to cart
curl -X POST http://localhost:8011/api/v1/{site_id}/cart/{cart_id}/items \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "{product_id}",
    "variant_id": "{variant_id}",
    "quantity": 2
  }'

# 3. Place order
curl -X POST http://localhost:8011/api/v1/{site_id}/orders \
  -H "Content-Type: application/json" \
  -d '{
    "cart_id": "{cart_id}",
    "customer_name": "John Doe",
    "customer_email": "john@example.com",
    "customer_phone": "+919876543210",
    "delivery_address": {
      "line1": "123 Main St",
      "city": "Mumbai",
      "state": "Maharashtra",
      "postal_code": "400001",
      "country": "India"
    },
    "payment_method": "cod"
  }'
```

### Order Management

```bash
# 1. List orders
curl -X GET "http://localhost:8011/api/v1/{site_id}/orders?order_status=placed&page=1"

# 2. Update order status
curl -X PUT http://localhost:8011/api/v1/{site_id}/orders/{order_id}/status \
  -H "Content-Type: application/json" \
  -d '{
    "order_status": "confirmed",
    "internal_notes": "Payment verified"
  }'

# 3. Cancel order
curl -X POST "http://localhost:8011/api/v1/{site_id}/orders/{order_id}/cancel?reason=Customer%20requested"

# 4. Get order history
curl -X GET http://localhost:8011/api/v1/{site_id}/orders/{order_id}/history
```

---

## 🔐 Authentication

The service supports JWT-based authentication via the Auth Service:

- **Optional Auth**: Cart endpoints work for both guests and authenticated users
- **Required Auth**: Admin operations (order status updates) require authentication
- **Token Verification**: Tokens validated against Auth Service

**Usage:**
```bash
curl -X GET http://localhost:8011/api/v1/{site_id}/orders \
  -H "Authorization: Bearer {jwt_token}"
```

**Mock Auth (Development):**
```python
# In middleware/auth.py, uncomment:
# auth_middleware = MockAuthMiddleware()

# Use test token:
curl -H "Authorization: Bearer test-token" ...
```

---

## 🎨 Customization

### Custom Product Attributes

Use the `attributes` JSONB field for flexible product data:

```json
{
  "attributes": {
    "material": "100% Cotton",
    "care_instructions": "Machine wash cold",
    "country_of_origin": "India",
    "brand": "MyBrand"
  }
}
```

### Custom Variant Options

```json
{
  "options": {
    "color": "Red",
    "size": "Large",
    "pattern": "Striped"
  }
}
```

### Event-Driven Notifications

Configure event publishing in `.env`:

```bash
EVENTS_ENABLED=true
REDIS_URL=redis://localhost:6379/0
```

Events published:
- `order.placed` → Email + SMS to customer
- `order.status_changed` → Status update notification
- `order.delivered` → Delivery confirmation + review request
- `cart.abandoned` → Cart recovery email
- `inventory.low_stock` → Admin alert

---

## 📊 Performance Considerations

### Database Optimization
- **Indexes**: Optimized for common queries (site_id, status, dates)
- **JSONB**: GIN indexes on tags and searchable attributes
- **Connection Pooling**: 20 connections, no overflow
- **Async Operations**: Non-blocking database I/O

### Caching (Future)
- Product catalog caching
- Cart session storage in Redis
- Search results caching

### Scalability
- **Horizontal Scaling**: Stateless service design
- **Multi-Tenancy**: Single instance serves multiple sites
- **Event-Driven**: Async processing via events

---

## 🧪 Testing

### Manual Testing

Access Swagger UI for interactive testing:
```
http://localhost:8011/docs
```

### Integration Testing

```bash
# 1. Start service
python -m app.main

# 2. Run seed data
python seed_products.py --site-id <uuid> --site-type store

# 3. Test complete flow
# - Create cart
# - Add products
# - Place order
# - Update status
# - Cancel order
```

---

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql -h localhost -U user -d storefront_db
```

### Import Errors
```bash
# Ensure all dependencies installed
pip install -r requirements.txt

# Check Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/storefront-service"
```

### Seed Data Failures
```bash
# Check site_id exists in site-service
# Verify database tables created
# Check foreign key constraints
```

---

## 🚧 Future Enhancements

- [ ] Payment gateway integration (Stripe, Razorpay)
- [ ] Advanced discount engine (coupons, promotions)
- [ ] Product reviews and ratings
- [ ] Wishlist functionality
- [ ] Advanced search with Elasticsearch
- [ ] Product recommendations
- [ ] Multi-currency support
- [ ] Shipping rate calculation
- [ ] Tax calculation by location
- [ ] Return/refund management

---

## 📞 Support

For issues and questions:
- Check service logs: `tail -f app.log`
- API documentation: `http://localhost:8011/docs`
- Architecture docs: `/home/user/beautifulwebsites/ARCHITECTURE.md`

---

## 📄 License

Part of the Beautiful Websites multi-website platform.

---

**Service Version:** 1.0.0
**Last Updated:** 2025-11-18
