# Storefront Service - API Overview

## Quick Stats
- **Total Endpoints**: 32
- **Database Tables**: 9
- **Pydantic Schemas**: 25+
- **Service Classes**: 4
- **Lines of Code**: ~5,700

## API Endpoints Summary

### Product Catalog (15 endpoints)
**Categories (5)**
- POST   /api/v1/catalog/{site_id}/categories
- GET    /api/v1/catalog/{site_id}/categories
- GET    /api/v1/catalog/{site_id}/categories/{category_id}
- PUT    /api/v1/catalog/{site_id}/categories/{category_id}
- DELETE /api/v1/catalog/{site_id}/categories/{category_id}

**Products (7)**
- POST   /api/v1/catalog/{site_id}/products
- GET    /api/v1/catalog/{site_id}/products (search with filters)
- GET    /api/v1/catalog/{site_id}/products/{product_id}
- GET    /api/v1/catalog/{site_id}/products/by-slug/{slug}
- PUT    /api/v1/catalog/{site_id}/products/{product_id}
- DELETE /api/v1/catalog/{site_id}/products/{product_id}

**Variants (3)**
- POST   /api/v1/catalog/{site_id}/products/{product_id}/variants
- GET    /api/v1/catalog/{site_id}/products/{product_id}/variants
- PUT    /api/v1/catalog/{site_id}/products/{product_id}/variants/{variant_id}

### Shopping Cart (9 endpoints)
- GET    /api/v1/{site_id}/cart
- GET    /api/v1/{site_id}/cart/{cart_id}
- POST   /api/v1/{site_id}/cart/{cart_id}/items
- GET    /api/v1/{site_id}/cart/{cart_id}/items
- PUT    /api/v1/{site_id}/cart/{cart_id}/items/{item_id}
- DELETE /api/v1/{site_id}/cart/{cart_id}/items/{item_id}
- DELETE /api/v1/{site_id}/cart/{cart_id}/items
- POST   /api/v1/{site_id}/cart/merge

### Orders (8 endpoints)
- POST   /api/v1/{site_id}/orders
- GET    /api/v1/{site_id}/orders
- GET    /api/v1/{site_id}/orders/{order_id}
- GET    /api/v1/{site_id}/orders/by-number/{order_number}
- GET    /api/v1/{site_id}/orders/{order_id}/items
- PUT    /api/v1/{site_id}/orders/{order_id}/status
- POST   /api/v1/{site_id}/orders/{order_id}/cancel
- GET    /api/v1/{site_id}/orders/{order_id}/history

## Business Logic Highlights

### Order Processing Flow
1. Validate cart exists and has items
2. Check inventory for ALL products
3. Generate unique order number (ORD-YYYYMMDD-XXXXX)
4. Create order with product snapshots
5. Deduct inventory
6. Create stock history entries
7. Mark cart as converted
8. Create order history entry
9. Publish order.placed event

### Cart Merging (Guest → User)
1. Find guest cart by session_id
2. Get or create user cart
3. For each guest cart item:
   - Check if item exists in user cart
   - Merge quantities OR move item
4. Mark guest cart as converted
5. Recalculate user cart totals

### Inventory Management
- Track stock at product OR variant level
- Automatic deduction on order placement
- Automatic restoration on order cancellation
- Complete audit trail via stock_history table
- Low stock alerts via events

## Database Design Highlights

### Multi-Tenancy
- Every table has `site_id` for isolation
- All queries filtered by `site_id`
- Indexes optimized for multi-tenant queries

### Audit Trails
- `order_history`: Complete status change log
- `stock_history`: All inventory movements
- `product_snapshot` in order_items: Historical data

### Flexible Schema
- JSONB for `attributes`, `options`, `delivery_address`
- Array support for `images`, `tags`
- GIN indexes for JSONB queries

## Event-Driven Architecture

### Order Events
- order.placed
- order.status_changed
- order.delivered
- order.cancelled

### Inventory Events
- inventory.low_stock
- inventory.out_of_stock

### Cart Events
- cart.abandoned

All events follow CloudEvents specification and can trigger:
- Email/SMS notifications
- Orchestration workflows
- Analytics tracking
- Admin dashboard updates
