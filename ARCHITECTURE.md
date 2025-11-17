# Multi-Website Platform Architecture
## For Small Business Websites (Departmental Stores, Services, Local SMEs)

**Version:** 1.0
**Date:** 2025-11-17
**Status:** Design Specification

---

## 1. Executive Summary

### Key Architectural Principles

- **Separation of Concerns**: Core platform services remain generic; business logic lives in domain services
- **Orchestration-Ready**: Event-driven architecture allows future workflow layer without rewrites
- **Multi-Tenancy First**: All services designed for isolated tenant data with shared infrastructure
- **Configuration Over Code**: New website types created via templates, configs, and workflows—not new codebases
- **API-First**: Clean contracts between layers enable independent scaling and evolution

### Architecture Layers

1. **Core Services Layer** (Existing) — Platform capabilities: auth, users, billing, AI, notifications, logging
2. **Domain Services Layer** (New) — Business entities: sites, products, bookings, leads, content, widgets
3. **Frontend Layer** (New) — Multi-tenant Next.js app with theme engine and dynamic routing
4. **Event Bus Layer** (New) — Message broker for async communication and orchestration hooks
5. **Orchestration Layer** (Future) — Workflow engine for cross-service processes (Temporal/Camunda/n8n)

### Technology Stack Recommendation

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Frontend** | Next.js 14+ (App Router) | SSR for SEO, dynamic routing, edge runtime, built-in API routes |
| **Domain Services** | Python (FastAPI) or Node.js (NestJS) | Match core_services stack; FastAPI preferred for async + validation |
| **Event Bus** | Redis Streams or RabbitMQ | Redis for simplicity; RabbitMQ for advanced routing |
| **Database** | PostgreSQL per domain service | Proven, JSONB for flexible schemas, excellent multi-tenancy support |
| **Cache** | Redis | Shared with event bus; cache themes, site configs, session data |
| **Future Orchestration** | Temporal (recommended) | Durable workflows, versioning, visibility, Python/Go SDKs |

### Core Design Decisions

✅ **DO:**
- Keep core services completely business-agnostic
- Use event sourcing for domain events (order placed, booking confirmed)
- Store all business logic in domain services or orchestration layer
- Make frontend 100% data-driven from domain APIs
- Design APIs to be orchestration-friendly (idempotent, compensatable)

❌ **DO NOT:**
- Put business rules (discount logic, booking rules) into core services
- Hardcode website types in frontend—use configuration
- Tightly couple domain services—they communicate via events only
- Store workflow state in domain services—that's orchestration's job
- Mix tenant data—strict isolation at database level

---

## 2. High-Level Architecture

### 2.1 System Context Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         INTERNET / USERS                            │
│  (Store Owners, End Customers, Site Admins)                        │
└────────────┬────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     CDN / EDGE LAYER (Cloudflare/Vercel)           │
│  - Static assets, images, CSS, JS                                  │
│  - Edge caching for site configs and pages                         │
└────────────┬────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   FRONTEND LAYER (Next.js Multi-Tenant)            │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │  Public Site │  │ Admin Panel  │  │ Owner Portal │            │
│  │  Renderer    │  │ (Site CMS)   │  │ (Dashboard)  │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│                                                                     │
│  Components:                                                        │
│  - Theme Engine (CSS-in-JS + config)                               │
│  - Dynamic Route Resolver (slug → site)                            │
│  - Section Renderer (hero, grid, forms)                            │
│  - LLM-powered content suggestions                                 │
└────────────┬────────────────────────────────────────────────────────┘
             │
             │ HTTP/REST + GraphQL
             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    API GATEWAY / BFF LAYER (Optional)              │
│  - Request routing, rate limiting, JWT validation                  │
│  - GraphQL Federation (if using GraphQL)                           │
│  - Request/response transformation                                 │
└────────────┬────────────────────────────────────────────────────────┘
             │
             ├────────────────────────┬────────────────────────┐
             │                        │                        │
             ▼                        ▼                        ▼
┌─────────────────────────┐  ┌──────────────────────┐  ┌─────────────────┐
│   DOMAIN SERVICES       │  │  CORE SERVICES       │  │  EVENT BUS      │
│   (Business Logic)      │  │  (Platform)          │  │  (Redis/RMQ)    │
│                         │  │                      │  │                 │
│ • Site Service          │  │ • Auth Service       │  │ Topics:         │
│   (8010)                │  │   (8000)             │  │ - site.events   │
│                         │  │                      │  │ - order.events  │
│ • Storefront Service    │  │ • User Service       │  │ - booking.events│
│   (8011)                │  │   (8001)             │  │ - lead.events   │
│                         │  │                      │  │ - billing.events│
│ • Booking Service       │  │ • Billing Service    │  └─────────────────┘
│   (8012)                │  │   (8002)             │           │
│                         │  │                      │           │
│ • Lead Service          │  │ • LLM Gateway        │           │
│   (8013)                │  │   (8003)             │           │
│                         │  │                      │           │
│ • Content Service       │  │ • Notification       │           │
│   (8014)                │  │   (8004)             │           │
│                         │  │                      │           │
│ • Widget Service        │  │ • Logging & Audit    │           │
│   (8015)                │  │   (8005)             │           │
└────────┬────────────────┘  └──────────┬───────────┘           │
         │                              │                        │
         └──────────────────────────────┴────────────────────────┘
                                        │
                                        ▼
                    ┌───────────────────────────────────────┐
                    │  ORCHESTRATION LAYER (Future)         │
                    │  - Temporal / Camunda / n8n           │
                    │  - Workflows for complex processes    │
                    │  - Listens to events, calls services  │
                    └───────────────────────────────────────┘
```

### 2.2 Layer Responsibilities

#### **CORE SERVICES LAYER** (Existing - Ports 8000-8005)

**Responsibilities:**
- ✅ Platform-level identity and access control (Auth, User)
- ✅ Subscription management and payment processing (Billing)
- ✅ AI capabilities gateway with prompt management (LLM Gateway)
- ✅ Multi-channel notification dispatch (Notification)
- ✅ Centralized logging and audit trails (Logging)

**MUST NOT Do:**
- ❌ Store business entities (products, bookings, orders)
- ❌ Implement business rules (discount calculations, booking availability)
- ❌ Know about website types or domain concepts
- ❌ Orchestrate multi-step business workflows

**Communication:**
- **Inbound:** REST APIs with JWT authentication
- **Outbound:** Webhook callbacks, event publishing (for billing events, notification delivery status)
- **Dependencies:** None between core services (loosely coupled)

---

#### **DOMAIN SERVICES LAYER** (New - Ports 8010-8015)

**Responsibilities:**
- ✅ Manage business entities and their lifecycles (sites, products, bookings, leads)
- ✅ Enforce domain-specific validation rules (e.g., booking slot availability)
- ✅ Expose business capabilities via clean REST APIs
- ✅ Emit domain events for state changes (ORDER_PLACED, BOOKING_CONFIRMED)
- ✅ Handle multi-tenancy at data level (org_id filtering)

**MUST NOT Do:**
- ❌ Implement cross-service workflows (that's orchestration's job)
- ❌ Directly call other domain services (use events instead)
- ❌ Duplicate core service logic (always delegate to Auth, Billing, etc.)
- ❌ Handle notifications directly (emit events; Notification Service handles delivery)

**Communication:**
- **Inbound:** REST APIs (JSON), authenticated via Auth Service
- **Outbound:** Event publishing to message bus
- **Dependencies:**
  - Auth Service (token validation via shared JWT library or API calls)
  - User Service (org/tenant info lookup)
  - Billing Service (quota checks, feature flags)
  - Notification Service (trigger notifications via events)
  - LLM Gateway (AI-powered features like product description generation)
  - Logging Service (structured event logging)

---

#### **FRONTEND LAYER** (New - Next.js)

**Responsibilities:**
- ✅ Render public-facing websites for end customers
- ✅ Provide site admin panel for content management (WYSIWYG-like experience)
- ✅ Provide owner dashboard for analytics, orders, bookings
- ✅ Dynamically load site config, theme, and content from Domain Services
- ✅ Handle routing based on domain/subdomain/path slugs
- ✅ Integrate LLM Gateway for AI-powered content suggestions in admin panel

**MUST NOT Do:**
- ❌ Store business logic (all logic delegated to Domain Services)
- ❌ Make direct calls to Core Services (use Domain Services as aggregators)
- ❌ Hardcode website types (use configuration from Site Service)
- ❌ Store state beyond user session (all persistent state in Domain Services)

**Communication:**
- **Inbound:** HTTP requests from browsers
- **Outbound:** REST API calls to Domain Services (and occasionally Core Services for auth)
- **Real-time:** WebSocket or Server-Sent Events for live order updates (optional)

---

#### **EVENT BUS LAYER** (New - Redis Streams / RabbitMQ)

**Responsibilities:**
- ✅ Reliable pub/sub messaging between services
- ✅ Topic-based routing (site.*, order.*, booking.*, lead.*)
- ✅ Event persistence for replay (important for orchestration)
- ✅ Dead letter queues for failed message handling

**MUST NOT Do:**
- ❌ Transform or enrich events (services publish complete event payloads)
- ❌ Implement business logic (it's just transport)

**Communication:**
- **Inbound:** Events published by Domain Services and Core Services
- **Outbound:** Events consumed by subscribers (other Domain Services, Orchestration Layer)

---

#### **ORCHESTRATION LAYER** (Future - Temporal/Camunda/n8n)

**Responsibilities:**
- ✅ Define and execute multi-step, long-running workflows
- ✅ Handle saga patterns (compensating transactions for failures)
- ✅ Coordinate calls across multiple Domain Services
- ✅ Implement timers, retries, human-in-the-loop approvals
- ✅ Provide workflow visibility and debugging

**MUST NOT Do:**
- ❌ Directly modify databases of Domain Services
- ❌ Implement domain validation logic (delegate to Domain Services)
- ❌ Bypass Domain Service APIs

**Communication:**
- **Inbound:** Events from Event Bus trigger workflows
- **Outbound:** REST API calls to Domain Services and Core Services
- **Storage:** Own database for workflow state and history

---

## 3. Domain Service Design (Modular & Reusable)

### 3.1 Site Service (Port 8010)

**Purpose:** Manage site definitions, templates, and configurations. This is the "meta" service that defines what sites exist and how they're structured.

**Main Entities:**

```sql
-- Table: sites
CREATE TABLE sites (
  site_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL,  -- FK to User Service
  slug VARCHAR(100) UNIQUE NOT NULL,  -- e.g., 'rams-grocery'
  domain VARCHAR(255),  -- custom domain (optional)
  site_type VARCHAR(50) NOT NULL,  -- 'departmental_store', 'tiffin_service', 'salon', etc.
  template_id UUID,  -- FK to templates table
  status VARCHAR(20) DEFAULT 'draft',  -- draft, published, suspended
  meta_title VARCHAR(200),
  meta_description TEXT,
  favicon_url VARCHAR(500),
  logo_url VARCHAR(500),
  primary_color VARCHAR(7),  -- HEX color
  secondary_color VARCHAR(7),
  font_family VARCHAR(100),
  config JSONB,  -- Site-specific settings (e.g., {"enable_cart": true, "show_prices": false})
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (org_id) REFERENCES orgs(org_id)  -- Conceptual; actual FK via User Service
);

-- Table: templates
CREATE TABLE templates (
  template_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  template_name VARCHAR(100) NOT NULL,  -- 'modern_store', 'minimal_service', etc.
  site_type VARCHAR(50) NOT NULL,  -- Which site type this template supports
  layout_config JSONB NOT NULL,  -- Default sections, order, props
  style_config JSONB,  -- Default colors, fonts, spacing
  preview_url VARCHAR(500),
  is_premium BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Table: site_sections (dynamic page sections)
CREATE TABLE site_sections (
  section_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  page_path VARCHAR(200) DEFAULT '/',  -- '/', '/about', '/services'
  section_type VARCHAR(50) NOT NULL,  -- 'hero', 'product_grid', 'testimonials', 'contact_form'
  section_order INT NOT NULL,
  section_config JSONB NOT NULL,  -- Props for this section instance
  is_visible BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (site_id) REFERENCES sites(site_id) ON DELETE CASCADE
);
```

**Core APIs:**

```
POST   /v1/sites                          # Create new site
GET    /v1/sites/{site_id}                # Get site details
GET    /v1/sites?org_id={id}              # List all sites for an org
PUT    /v1/sites/{site_id}                # Update site config
DELETE /v1/sites/{site_id}                # Soft delete site
PATCH  /v1/sites/{site_id}/status         # Publish/suspend site

GET    /v1/sites/by-slug/{slug}           # Resolve site by slug (for frontend)
GET    /v1/sites/by-domain/{domain}       # Resolve site by custom domain

POST   /v1/sites/{site_id}/sections       # Add section to page
PUT    /v1/sites/{site_id}/sections/{id}  # Update section
DELETE /v1/sites/{site_id}/sections/{id}  # Remove section
GET    /v1/sites/{site_id}/pages/{path}   # Get all sections for a page

GET    /v1/templates                      # List available templates
GET    /v1/templates/{template_id}        # Get template details
```

**Multi-Tenancy:**
- All queries filtered by `org_id` (extracted from JWT token)
- Row-level security (RLS) in PostgreSQL to enforce isolation
- Each org can have multiple sites (one-to-many)

**Dependencies on Core Services:**
- **Auth Service:** Validate JWT tokens, check user permissions
- **User Service:** Fetch org details, check ownership
- **Billing Service:** Check plan limits (e.g., max 5 sites on basic plan)
- **LLM Gateway:** Generate site meta descriptions, suggest color schemes
- **Logging Service:** Log site creation, config changes

**Events Emitted:**
```json
{
  "event_type": "SITE_CREATED",
  "site_id": "uuid",
  "org_id": "uuid",
  "site_type": "departmental_store",
  "timestamp": "2025-11-17T10:00:00Z"
}
```

---

### 3.2 Storefront Service (Port 8011)

**Purpose:** Manage products/services catalog, categories, inventory, shopping cart, and orders. Reusable across e-commerce style sites.

**Main Entities:**

```sql
-- Table: categories
CREATE TABLE categories (
  category_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  parent_category_id UUID,  -- For nested categories
  name VARCHAR(200) NOT NULL,
  slug VARCHAR(200) NOT NULL,
  description TEXT,
  image_url VARCHAR(500),
  sort_order INT DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (site_id) REFERENCES sites(site_id),
  FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
);

-- Table: products
CREATE TABLE products (
  product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  category_id UUID,
  sku VARCHAR(100),
  name VARCHAR(300) NOT NULL,
  slug VARCHAR(300) NOT NULL,
  description TEXT,
  short_description VARCHAR(500),
  price DECIMAL(10,2) NOT NULL,
  compare_at_price DECIMAL(10,2),  -- For showing discounts
  cost DECIMAL(10,2),  -- For margin calculations
  images JSONB,  -- Array of image URLs
  tags TEXT[],  -- For search/filtering
  is_active BOOLEAN DEFAULT TRUE,
  stock_quantity INT,
  track_inventory BOOLEAN DEFAULT TRUE,
  meta JSONB,  -- Flexible attributes (e.g., {"size": "500g", "brand": "Tata"})
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (site_id) REFERENCES sites(site_id),
  FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

-- Table: carts
CREATE TABLE carts (
  cart_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  user_id UUID,  -- NULL for guest carts
  session_id VARCHAR(255),  -- For guest tracking
  expires_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Table: cart_items
CREATE TABLE cart_items (
  cart_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  cart_id UUID NOT NULL,
  product_id UUID NOT NULL,
  quantity INT NOT NULL DEFAULT 1,
  price_at_add DECIMAL(10,2) NOT NULL,  -- Snapshot price
  added_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (cart_id) REFERENCES carts(cart_id) ON DELETE CASCADE,
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- Table: orders
CREATE TABLE orders (
  order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  order_number VARCHAR(50) UNIQUE NOT NULL,  -- Human-readable ID
  user_id UUID,  -- FK to User Service (or NULL for guest)
  customer_name VARCHAR(200) NOT NULL,
  customer_email VARCHAR(255),
  customer_phone VARCHAR(20) NOT NULL,
  delivery_address JSONB,
  subtotal DECIMAL(10,2) NOT NULL,
  tax DECIMAL(10,2) DEFAULT 0,
  delivery_fee DECIMAL(10,2) DEFAULT 0,
  discount DECIMAL(10,2) DEFAULT 0,
  total DECIMAL(10,2) NOT NULL,
  payment_method VARCHAR(50),  -- 'cod', 'online', 'upi'
  payment_status VARCHAR(20) DEFAULT 'pending',  -- pending, paid, failed
  order_status VARCHAR(20) DEFAULT 'placed',  -- placed, confirmed, preparing, dispatched, delivered, cancelled
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (site_id) REFERENCES sites(site_id)
);

-- Table: order_items
CREATE TABLE order_items (
  order_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  order_id UUID NOT NULL,
  product_id UUID,
  product_name VARCHAR(300),  -- Snapshot in case product deleted
  quantity INT NOT NULL,
  unit_price DECIMAL(10,2) NOT NULL,
  total_price DECIMAL(10,2) NOT NULL,
  FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);
```

**Core APIs:**

```
# Catalog Management
POST   /v1/sites/{site_id}/categories
GET    /v1/sites/{site_id}/categories
PUT    /v1/sites/{site_id}/categories/{id}

POST   /v1/sites/{site_id}/products
GET    /v1/sites/{site_id}/products?category={id}&tags={tag}&search={query}
GET    /v1/sites/{site_id}/products/{product_id}
PUT    /v1/sites/{site_id}/products/{product_id}
DELETE /v1/sites/{site_id}/products/{product_id}
PATCH  /v1/sites/{site_id}/products/{product_id}/stock  # Update inventory

# Shopping Cart
POST   /v1/sites/{site_id}/carts                       # Create cart
GET    /v1/sites/{site_id}/carts/{cart_id}
POST   /v1/sites/{site_id}/carts/{cart_id}/items       # Add item
PUT    /v1/sites/{site_id}/carts/{cart_id}/items/{item_id}  # Update quantity
DELETE /v1/sites/{site_id}/carts/{cart_id}/items/{item_id}

# Orders
POST   /v1/sites/{site_id}/orders                      # Checkout / Create order
GET    /v1/sites/{site_id}/orders?status={status}
GET    /v1/sites/{site_id}/orders/{order_id}
PATCH  /v1/sites/{site_id}/orders/{order_id}/status    # Update order status
POST   /v1/sites/{site_id}/orders/{order_id}/cancel
```

**Multi-Tenancy:**
- All entities linked to `site_id`
- Each site is isolated (org A cannot see org B's products)
- Database-level RLS or application-level filtering

**Dependencies on Core Services:**
- **Auth Service:** Validate tokens for admin operations
- **User Service:** Link orders to users (optional)
- **Billing Service:** Check if storefront feature is enabled for this org's plan
- **LLM Gateway:** Generate product descriptions, SEO-optimized titles
- **Notification Service:** Send order confirmation emails/SMS
- **Logging Service:** Audit order status changes, inventory updates

**Events Emitted:**
```json
{
  "event_type": "ORDER_PLACED",
  "order_id": "uuid",
  "site_id": "uuid",
  "total": 1250.00,
  "customer_phone": "+911234567890",
  "timestamp": "2025-11-17T10:30:00Z"
}

{
  "event_type": "ORDER_STATUS_CHANGED",
  "order_id": "uuid",
  "old_status": "placed",
  "new_status": "confirmed",
  "timestamp": "2025-11-17T10:45:00Z"
}

{
  "event_type": "LOW_STOCK_ALERT",
  "product_id": "uuid",
  "site_id": "uuid",
  "current_stock": 5,
  "threshold": 10,
  "timestamp": "2025-11-17T11:00:00Z"
}
```

---

### 3.3 Booking Service (Port 8012)

**Purpose:** Manage appointment scheduling, service slots, bookings. Reusable for salons, clinics, coaching centers, consultations.

**Main Entities:**

```sql
-- Table: services (bookable services)
CREATE TABLE services (
  service_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  duration_minutes INT NOT NULL,  -- 30, 60, 90, etc.
  price DECIMAL(10,2),
  image_url VARCHAR(500),
  is_active BOOLEAN DEFAULT TRUE,
  buffer_minutes INT DEFAULT 0,  -- Time between appointments
  max_advance_booking_days INT DEFAULT 30,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (site_id) REFERENCES sites(site_id)
);

-- Table: staff (providers who deliver services)
CREATE TABLE staff (
  staff_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  user_id UUID,  -- FK to User Service (optional)
  name VARCHAR(200) NOT NULL,
  email VARCHAR(255),
  phone VARCHAR(20),
  avatar_url VARCHAR(500),
  bio TEXT,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (site_id) REFERENCES sites(site_id)
);

-- Table: staff_services (many-to-many)
CREATE TABLE staff_services (
  staff_id UUID NOT NULL,
  service_id UUID NOT NULL,
  PRIMARY KEY (staff_id, service_id),
  FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE CASCADE,
  FOREIGN KEY (service_id) REFERENCES services(service_id) ON DELETE CASCADE
);

-- Table: availability_slots (weekly schedule)
CREATE TABLE availability_slots (
  availability_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  staff_id UUID NOT NULL,
  day_of_week INT NOT NULL,  -- 0 = Sunday, 6 = Saturday
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  FOREIGN KEY (staff_id) REFERENCES staff(staff_id) ON DELETE CASCADE
);

-- Table: bookings
CREATE TABLE bookings (
  booking_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  service_id UUID NOT NULL,
  staff_id UUID,
  user_id UUID,  -- FK to User Service (or NULL for guest)
  customer_name VARCHAR(200) NOT NULL,
  customer_email VARCHAR(255),
  customer_phone VARCHAR(20) NOT NULL,
  booking_date DATE NOT NULL,
  start_time TIME NOT NULL,
  end_time TIME NOT NULL,
  status VARCHAR(20) DEFAULT 'pending',  -- pending, confirmed, completed, cancelled, no_show
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (site_id) REFERENCES sites(site_id),
  FOREIGN KEY (service_id) REFERENCES services(service_id),
  FOREIGN KEY (staff_id) REFERENCES staff(staff_id)
);
```

**Core APIs:**

```
# Services
POST   /v1/sites/{site_id}/services
GET    /v1/sites/{site_id}/services
PUT    /v1/sites/{site_id}/services/{service_id}

# Staff
POST   /v1/sites/{site_id}/staff
GET    /v1/sites/{site_id}/staff
PUT    /v1/sites/{site_id}/staff/{staff_id}
POST   /v1/sites/{site_id}/staff/{staff_id}/availability  # Set weekly hours

# Availability Check
GET    /v1/sites/{site_id}/availability?service_id={id}&date={YYYY-MM-DD}&staff_id={id}
       # Returns available time slots for booking

# Bookings
POST   /v1/sites/{site_id}/bookings                  # Create booking
GET    /v1/sites/{site_id}/bookings?date={date}&status={status}
GET    /v1/sites/{site_id}/bookings/{booking_id}
PATCH  /v1/sites/{site_id}/bookings/{booking_id}/status  # Confirm, cancel, complete
```

**Multi-Tenancy:**
- All entities scoped to `site_id`
- Staff can belong to one site only (or multiple via user_id if needed)

**Dependencies on Core Services:**
- **Auth Service:** Token validation
- **User Service:** Optional user linking for customers and staff
- **Billing Service:** Feature flag checks
- **LLM Gateway:** Smart slot suggestions, automated reminders text generation
- **Notification Service:** Send booking confirmation, reminder 24h before, follow-up after appointment
- **Logging Service:** Audit booking changes, cancellations

**Events Emitted:**
```json
{
  "event_type": "BOOKING_CREATED",
  "booking_id": "uuid",
  "site_id": "uuid",
  "service_id": "uuid",
  "booking_date": "2025-11-20",
  "start_time": "10:00:00",
  "customer_phone": "+911234567890",
  "timestamp": "2025-11-17T12:00:00Z"
}

{
  "event_type": "BOOKING_CONFIRMED",
  "booking_id": "uuid",
  "timestamp": "2025-11-17T12:05:00Z"
}

{
  "event_type": "BOOKING_REMINDER_DUE",
  "booking_id": "uuid",
  "reminder_type": "24h_before",
  "timestamp": "2025-11-19T10:00:00Z"
}
```

---

### 3.4 Lead Service (Port 8013)

**Purpose:** Capture and manage customer inquiries, quote requests, contact form submissions. Reusable across all site types.

**Main Entities:**

```sql
-- Table: leads
CREATE TABLE leads (
  lead_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  lead_source VARCHAR(50),  -- 'contact_form', 'chat', 'phone', 'whatsapp'
  customer_name VARCHAR(200) NOT NULL,
  customer_email VARCHAR(255),
  customer_phone VARCHAR(20),
  subject VARCHAR(300),
  message TEXT NOT NULL,
  status VARCHAR(20) DEFAULT 'new',  -- new, contacted, qualified, converted, closed
  assigned_to_user_id UUID,  -- FK to User Service (sales rep)
  metadata JSONB,  -- Extra form fields (e.g., preferred_time, budget_range)
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (site_id) REFERENCES sites(site_id)
);

-- Table: lead_activities (audit trail)
CREATE TABLE lead_activities (
  activity_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lead_id UUID NOT NULL,
  activity_type VARCHAR(50) NOT NULL,  -- 'status_change', 'note_added', 'email_sent', 'call_made'
  description TEXT,
  performed_by_user_id UUID,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (lead_id) REFERENCES leads(lead_id) ON DELETE CASCADE
);
```

**Core APIs:**

```
POST   /v1/sites/{site_id}/leads                    # Submit lead (public endpoint)
GET    /v1/sites/{site_id}/leads?status={status}    # List leads (authenticated)
GET    /v1/sites/{site_id}/leads/{lead_id}
PATCH  /v1/sites/{site_id}/leads/{lead_id}/status
POST   /v1/sites/{site_id}/leads/{lead_id}/activities  # Add note/activity
```

**Multi-Tenancy:**
- Scoped to `site_id`

**Dependencies on Core Services:**
- **Notification Service:** Auto-respond to lead submitter, notify site owner
- **LLM Gateway:** Classify lead intent, suggest follow-up actions
- **Logging Service:** Log lead submissions and status changes

**Events Emitted:**
```json
{
  "event_type": "LEAD_CREATED",
  "lead_id": "uuid",
  "site_id": "uuid",
  "lead_source": "contact_form",
  "customer_phone": "+911234567890",
  "timestamp": "2025-11-17T13:00:00Z"
}

{
  "event_type": "LEAD_STATUS_CHANGED",
  "lead_id": "uuid",
  "old_status": "new",
  "new_status": "contacted",
  "timestamp": "2025-11-17T14:00:00Z"
}
```

---

### 3.5 Content Service (Port 8014)

**Purpose:** Manage dynamic text content, blog posts, FAQs, testimonials, media library. Headless CMS capabilities.

**Main Entities:**

```sql
-- Table: pages (for additional pages beyond home)
CREATE TABLE pages (
  page_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  title VARCHAR(300) NOT NULL,
  slug VARCHAR(300) NOT NULL,
  content TEXT,  -- Rich text / HTML
  meta_title VARCHAR(200),
  meta_description VARCHAR(500),
  is_published BOOLEAN DEFAULT FALSE,
  published_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (site_id) REFERENCES sites(site_id),
  UNIQUE (site_id, slug)
);

-- Table: blog_posts
CREATE TABLE blog_posts (
  post_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  author_user_id UUID,
  title VARCHAR(300) NOT NULL,
  slug VARCHAR(300) NOT NULL,
  excerpt VARCHAR(500),
  content TEXT NOT NULL,
  featured_image_url VARCHAR(500),
  tags TEXT[],
  is_published BOOLEAN DEFAULT FALSE,
  published_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (site_id) REFERENCES sites(site_id),
  UNIQUE (site_id, slug)
);

-- Table: faqs
CREATE TABLE faqs (
  faq_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  question VARCHAR(500) NOT NULL,
  answer TEXT NOT NULL,
  category VARCHAR(100),
  sort_order INT DEFAULT 0,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (site_id) REFERENCES sites(site_id)
);

-- Table: testimonials
CREATE TABLE testimonials (
  testimonial_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  customer_name VARCHAR(200) NOT NULL,
  customer_title VARCHAR(200),  -- e.g., "CEO, Acme Corp"
  rating INT CHECK (rating >= 1 AND rating <= 5),
  content TEXT NOT NULL,
  avatar_url VARCHAR(500),
  is_featured BOOLEAN DEFAULT FALSE,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (site_id) REFERENCES sites(site_id)
);

-- Table: media_library
CREATE TABLE media_library (
  media_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  file_name VARCHAR(300) NOT NULL,
  file_url VARCHAR(500) NOT NULL,
  file_type VARCHAR(50),  -- image, video, document
  file_size_bytes BIGINT,
  alt_text VARCHAR(300),
  tags TEXT[],
  uploaded_by_user_id UUID,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (site_id) REFERENCES sites(site_id)
);
```

**Core APIs:**

```
# Pages
POST   /v1/sites/{site_id}/pages
GET    /v1/sites/{site_id}/pages
GET    /v1/sites/{site_id}/pages/{slug}
PUT    /v1/sites/{site_id}/pages/{page_id}

# Blog
POST   /v1/sites/{site_id}/blog/posts
GET    /v1/sites/{site_id}/blog/posts?tags={tag}
GET    /v1/sites/{site_id}/blog/posts/{slug}
PUT    /v1/sites/{site_id}/blog/posts/{post_id}

# FAQs
POST   /v1/sites/{site_id}/faqs
GET    /v1/sites/{site_id}/faqs?category={cat}
PUT    /v1/sites/{site_id}/faqs/{faq_id}

# Testimonials
POST   /v1/sites/{site_id}/testimonials
GET    /v1/sites/{site_id}/testimonials?is_featured=true

# Media
POST   /v1/sites/{site_id}/media                    # Upload file
GET    /v1/sites/{site_id}/media?file_type={type}
DELETE /v1/sites/{site_id}/media/{media_id}
```

**Multi-Tenancy:**
- All content scoped to `site_id`

**Dependencies on Core Services:**
- **LLM Gateway:** Generate blog post drafts, FAQ answers, product descriptions
- **Logging Service:** Audit content changes

**Events Emitted:**
```json
{
  "event_type": "BLOG_POST_PUBLISHED",
  "post_id": "uuid",
  "site_id": "uuid",
  "title": "10 Tips for Your Store",
  "timestamp": "2025-11-17T15:00:00Z"
}
```

---

### 3.6 Widget Service (Port 8015)

**Purpose:** Manage configurable widgets (calculators, forms, chatbots, WhatsApp buttons). Reusable across sites.

**Main Entities:**

```sql
-- Table: widgets
CREATE TABLE widgets (
  widget_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  site_id UUID NOT NULL,
  widget_type VARCHAR(50) NOT NULL,  -- 'calculator', 'contact_form', 'whatsapp_button', 'chatbot'
  widget_name VARCHAR(200) NOT NULL,
  config JSONB NOT NULL,  -- Widget-specific configuration
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (site_id) REFERENCES sites(site_id)
);

-- Table: widget_submissions (for forms, calculators)
CREATE TABLE widget_submissions (
  submission_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  widget_id UUID NOT NULL,
  user_inputs JSONB NOT NULL,  -- User-entered data
  calculated_result JSONB,  -- For calculators
  submitted_by_user_id UUID,
  ip_address INET,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (widget_id) REFERENCES widgets(widget_id)
);
```

**Core APIs:**

```
POST   /v1/sites/{site_id}/widgets
GET    /v1/sites/{site_id}/widgets?widget_type={type}
GET    /v1/sites/{site_id}/widgets/{widget_id}
PUT    /v1/sites/{site_id}/widgets/{widget_id}

POST   /v1/widgets/{widget_id}/submit       # Public endpoint for widget interaction
GET    /v1/sites/{site_id}/widgets/{widget_id}/submissions  # View submissions
```

**Example Widget Configs:**

```json
// WhatsApp Button
{
  "widget_type": "whatsapp_button",
  "config": {
    "phone_number": "+911234567890",
    "pre_filled_message": "Hi, I'm interested in your products!",
    "button_text": "Chat on WhatsApp",
    "position": "bottom-right"
  }
}

// EMI Calculator
{
  "widget_type": "calculator",
  "config": {
    "calculator_type": "emi",
    "fields": [
      {"name": "principal", "label": "Loan Amount", "type": "number"},
      {"name": "rate", "label": "Interest Rate (%)", "type": "number"},
      {"name": "tenure", "label": "Tenure (months)", "type": "number"}
    ],
    "formula": "EMI = [P x R x (1+R)^N] / [(1+R)^N-1]"
  }
}
```

**Dependencies on Core Services:**
- **LLM Gateway:** Power chatbot widgets with AI responses
- **Notification Service:** Send widget submission notifications

**Events Emitted:**
```json
{
  "event_type": "WIDGET_SUBMITTED",
  "widget_id": "uuid",
  "widget_type": "contact_form",
  "site_id": "uuid",
  "timestamp": "2025-11-17T16:00:00Z"
}
```

---

## 4. Frontend / Multi-Site Architecture

### 4.1 Technology Stack: Next.js 14+ (App Router)

**Justification:**

✅ **Server-Side Rendering (SSR):** Critical for SEO; small businesses need to rank in Google
✅ **Dynamic Routing:** `app/[slug]/page.tsx` for multi-site support
✅ **API Routes:** Built-in backend for BFF pattern (aggregating domain service calls)
✅ **Image Optimization:** Automatic optimization for product images, logos
✅ **Edge Runtime:** Deploy to Vercel Edge for fast global delivery
✅ **TypeScript Support:** Type safety across frontend and API routes
✅ **React Server Components:** Fetch data on server, reduce client bundle size
✅ **Incremental Static Regeneration (ISR):** Cache site configs, revalidate on changes

**Alternatives Considered:**
- ❌ **Separate SPAs per site:** Too much duplication, hard to maintain
- ❌ **WordPress Multi-site:** Not flexible enough for custom business logic
- ❌ **Gatsby:** Static generation doesn't fit dynamic storefronts well
- ❌ **Vue/Nuxt:** Team familiarity and ecosystem favor React/Next.js

---

### 4.2 Project Structure

```
beautifulwebsites/
├── apps/
│   ├── web/                          # Main Next.js app
│   │   ├── app/
│   │   │   ├── (public)/             # Public site routes
│   │   │   │   ├── [slug]/           # Dynamic site rendering
│   │   │   │   │   ├── page.tsx      # Home page
│   │   │   │   │   ├── [page]/page.tsx  # Additional pages
│   │   │   │   │   ├── products/     # Product listing/detail
│   │   │   │   │   ├── booking/      # Booking flow
│   │   │   │   │   ├── contact/      # Contact form
│   │   │   │   │   └── layout.tsx    # Site-specific layout
│   │   │   ├── (admin)/              # Admin panel routes
│   │   │   │   ├── dashboard/
│   │   │   │   ├── site-editor/      # Visual site editor
│   │   │   │   ├── products/
│   │   │   │   ├── orders/
│   │   │   │   ├── bookings/
│   │   │   │   └── layout.tsx        # Admin layout
│   │   │   ├── api/                  # Backend for frontend (BFF)
│   │   │   │   ├── sites/[slug]/route.ts
│   │   │   │   ├── products/route.ts
│   │   │   │   └── orders/route.ts
│   │   │   └── layout.tsx            # Root layout
│   │   ├── components/
│   │   │   ├── sections/             # Reusable site sections
│   │   │   │   ├── HeroSection.tsx
│   │   │   │   ├── ProductGridSection.tsx
│   │   │   │   ├── TestimonialsSection.tsx
│   │   │   │   ├── ContactFormSection.tsx
│   │   │   │   ├── WhatsAppButtonSection.tsx
│   │   │   │   └── index.ts
│   │   │   ├── ui/                   # Base UI components (shadcn/ui)
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   └── ...
│   │   │   ├── admin/                # Admin-specific components
│   │   │   │   ├── SiteEditor.tsx
│   │   │   │   ├── SectionPicker.tsx
│   │   │   │   └── AIContentSuggester.tsx
│   │   │   └── layout/
│   │   │       ├── Header.tsx
│   │   │       ├── Footer.tsx
│   │   │       └── MobileNav.tsx
│   │   ├── lib/
│   │   │   ├── api/                  # API client for domain services
│   │   │   │   ├── site-service.ts
│   │   │   │   ├── storefront-service.ts
│   │   │   │   ├── booking-service.ts
│   │   │   │   └── ...
│   │   │   ├── theme/
│   │   │   │   ├── theme-engine.ts   # Dynamic theming logic
│   │   │   │   └── default-themes.ts
│   │   │   ├── utils/
│   │   │   │   ├── cn.ts             # Class name helper (clsx + tailwind-merge)
│   │   │   │   └── format.ts
│   │   │   └── hooks/
│   │   │       ├── useSiteConfig.ts
│   │   │       ├── useCart.ts
│   │   │       └── useBooking.ts
│   │   ├── styles/
│   │   │   └── globals.css           # Tailwind + global styles
│   │   ├── public/
│   │   │   ├── default-assets/       # Default logos, images
│   │   │   └── ...
│   │   ├── middleware.ts             # Domain/subdomain routing
│   │   ├── next.config.js
│   │   └── package.json
│   │
│   └── owner-portal/                 # Separate Next.js app for site owners (optional)
│       └── ...                       # Dashboard, analytics, settings
│
├── packages/
│   ├── ui/                           # Shared UI components (if multiple apps)
│   ├── types/                        # Shared TypeScript types
│   │   ├── site.ts
│   │   ├── product.ts
│   │   ├── booking.ts
│   │   └── ...
│   └── config/                       # Shared configs (ESLint, TypeScript, Tailwind)
│
├── domain-services/                  # Domain microservices (FastAPI/NestJS)
│   ├── site-service/
│   ├── storefront-service/
│   ├── booking-service/
│   ├── lead-service/
│   ├── content-service/
│   ├── widget-service/
│   └── docker-compose.yml
│
├── infrastructure/
│   ├── docker/
│   ├── k8s/                          # Kubernetes manifests (if using)
│   └── terraform/                    # IaC for cloud resources
│
├── docs/
│   ├── ARCHITECTURE.md               # This document
│   ├── API.md                        # API documentation
│   └── DEPLOYMENT.md
│
├── .github/
│   └── workflows/                    # CI/CD pipelines
│
├── turbo.json                        # Turborepo config (if using monorepo)
├── package.json
└── README.md
```

---

### 4.3 Multi-Site Routing Strategy

**Option A: Slug-Based Routing (Recommended for MVP)**

- All sites served from single domain: `yourplatform.com/{slug}`
- Example: `yourplatform.com/rams-grocery`, `yourplatform.com/bella-salon`
- Middleware resolves slug → site_id → site config

```typescript
// middleware.ts
import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Extract slug from path (e.g., /rams-grocery/products → rams-grocery)
  const slug = pathname.split('/')[1]

  if (slug && slug !== 'admin' && slug !== 'api') {
    // Fetch site config from Site Service (with caching)
    const siteConfig = await fetchSiteConfig(slug)

    if (!siteConfig) {
      return NextResponse.redirect(new URL('/404', request.url))
    }

    // Store site config in request headers for downstream use
    const requestHeaders = new Headers(request.headers)
    requestHeaders.set('x-site-id', siteConfig.site_id)
    requestHeaders.set('x-site-config', JSON.stringify(siteConfig))

    return NextResponse.next({
      request: {
        headers: requestHeaders,
      },
    })
  }
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico).*)'],
}
```

**Option B: Subdomain Routing (For Growth)**

- Each site gets subdomain: `rams-grocery.yourplatform.com`, `bella-salon.yourplatform.com`
- Wildcard DNS: `*.yourplatform.com` → Next.js app
- Middleware extracts subdomain instead of slug

**Option C: Custom Domain Mapping (Premium Feature)**

- Site owners can use own domains: `www.ramsgrocery.com`
- DNS CNAME → yourplatform.com
- Middleware checks `request.headers.get('host')` → lookup site by domain

---

### 4.4 Theme Engine Architecture

**Approach: CSS-in-JS + Tailwind CSS + CSS Variables**

```typescript
// lib/theme/theme-engine.ts
import { SiteConfig } from '@/types/site'

export function generateThemeCSS(siteConfig: SiteConfig): string {
  const {
    primary_color = '#3b82f6',
    secondary_color = '#10b981',
    font_family = 'Inter, sans-serif',
  } = siteConfig

  return `
    :root {
      --color-primary: ${primary_color};
      --color-secondary: ${secondary_color};
      --font-family: ${font_family};
      --color-primary-hover: ${darken(primary_color, 10)};
      --color-bg: #ffffff;
      --color-text: #1f2937;
    }
  `
}

// Inject theme CSS in layout
export function ThemeProvider({ siteConfig, children }: { siteConfig: SiteConfig; children: React.ReactNode }) {
  const themeCSS = generateThemeCSS(siteConfig)

  return (
    <>
      <style dangerouslySetInnerHTML={{ __html: themeCSS }} />
      {children}
    </>
  )
}
```

**Tailwind Configuration:**

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: 'var(--color-primary)',
        secondary: 'var(--color-secondary)',
      },
      fontFamily: {
        sans: ['var(--font-family)', 'system-ui'],
      },
    },
  },
}
```

**Usage in Components:**

```tsx
<button className="bg-primary text-white hover:bg-primary-hover px-6 py-3 rounded-lg">
  Add to Cart
</button>
```

---

### 4.5 Section-Based Page Rendering

**Key Concept:** Pages are composed of reusable sections. Each section has a type and config.

```tsx
// app/[slug]/page.tsx
import { SectionRenderer } from '@/components/SectionRenderer'
import { fetchSiteSections } from '@/lib/api/site-service'

export default async function SitePage({ params }: { params: { slug: string } }) {
  const sections = await fetchSiteSections(params.slug, '/')  // Home page

  return (
    <div className="site-page">
      {sections.map((section) => (
        <SectionRenderer
          key={section.section_id}
          type={section.section_type}
          config={section.section_config}
        />
      ))}
    </div>
  )
}
```

```tsx
// components/SectionRenderer.tsx
import { HeroSection } from './sections/HeroSection'
import { ProductGridSection } from './sections/ProductGridSection'
import { TestimonialsSection } from './sections/TestimonialsSection'
import { ContactFormSection } from './sections/ContactFormSection'

const SECTION_COMPONENTS = {
  hero: HeroSection,
  product_grid: ProductGridSection,
  testimonials: TestimonialsSection,
  contact_form: ContactFormSection,
  // ... more section types
}

export function SectionRenderer({ type, config }: { type: string; config: any }) {
  const Component = SECTION_COMPONENTS[type]

  if (!Component) {
    console.error(`Unknown section type: ${type}`)
    return null
  }

  return <Component {...config} />
}
```

**Example Section Component:**

```tsx
// components/sections/HeroSection.tsx
export function HeroSection({
  title,
  subtitle,
  cta_text,
  cta_link,
  background_image,
  text_alignment = 'center',
}: {
  title: string
  subtitle?: string
  cta_text?: string
  cta_link?: string
  background_image?: string
  text_alignment?: 'left' | 'center' | 'right'
}) {
  return (
    <section
      className="relative h-[500px] flex items-center justify-center"
      style={{
        backgroundImage: background_image ? `url(${background_image})` : 'none',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className={`container mx-auto px-4 text-${text_alignment}`}>
        <h1 className="text-5xl font-bold text-white mb-4">{title}</h1>
        {subtitle && <p className="text-xl text-white mb-8">{subtitle}</p>}
        {cta_text && cta_link && (
          <a href={cta_link} className="bg-primary text-white px-8 py-4 rounded-lg inline-block">
            {cta_text}
          </a>
        )}
      </div>
    </section>
  )
}
```

---

### 4.6 Site Admin Panel (Visual Editor)

**Features:**

1. **Section Management:**
   - Drag-and-drop to reorder sections
   - Add new sections from library
   - Configure section props via forms
   - Live preview

2. **Content Editing:**
   - Inline text editing
   - Image upload to Media Library
   - Rich text editor for long content

3. **AI-Powered Suggestions:**
   - Generate product descriptions (LLM Gateway)
   - Suggest SEO meta tags
   - Create FAQ answers
   - Draft blog posts

**Architecture:**

```tsx
// app/(admin)/site-editor/page.tsx
'use client'

import { useState } from 'react'
import { DndContext, closestCenter } from '@dnd-kit/core'
import { SectionPicker } from '@/components/admin/SectionPicker'
import { SectionConfigPanel } from '@/components/admin/SectionConfigPanel'
import { SectionRenderer } from '@/components/SectionRenderer'

export default function SiteEditorPage() {
  const [sections, setSections] = useState([])
  const [selectedSection, setSelectedSection] = useState(null)

  const handleAddSection = (sectionType: string) => {
    const newSection = {
      section_id: crypto.randomUUID(),
      section_type: sectionType,
      section_config: getDefaultConfig(sectionType),
      section_order: sections.length,
    }
    setSections([...sections, newSection])
  }

  const handleUpdateSection = (sectionId: string, newConfig: any) => {
    setSections(sections.map(s =>
      s.section_id === sectionId ? { ...s, section_config: newConfig } : s
    ))
  }

  const handleSave = async () => {
    await saveSiteSections(sections)
  }

  return (
    <div className="flex h-screen">
      {/* Left sidebar: Section library */}
      <div className="w-64 bg-gray-100 p-4">
        <SectionPicker onAddSection={handleAddSection} />
      </div>

      {/* Center: Live preview */}
      <div className="flex-1 overflow-y-auto bg-white">
        <DndContext collisionDetection={closestCenter}>
          {sections.map((section) => (
            <div
              key={section.section_id}
              onClick={() => setSelectedSection(section)}
              className="border-2 border-transparent hover:border-blue-500 cursor-pointer"
            >
              <SectionRenderer
                type={section.section_type}
                config={section.section_config}
              />
            </div>
          ))}
        </DndContext>
      </div>

      {/* Right sidebar: Config panel */}
      <div className="w-80 bg-gray-50 p-4">
        {selectedSection && (
          <SectionConfigPanel
            section={selectedSection}
            onUpdate={(newConfig) => handleUpdateSection(selectedSection.section_id, newConfig)}
          />
        )}
        <button
          onClick={handleSave}
          className="w-full bg-primary text-white py-3 rounded-lg mt-4"
        >
          Save Changes
        </button>
      </div>
    </div>
  )
}
```

---

### 4.7 LLM Integration Points in Frontend

**Use Cases:**

1. **Content Suggestions in Admin Panel**
   ```tsx
   // components/admin/AIContentSuggester.tsx
   async function generateProductDescription(productName: string) {
     const response = await fetch('/api/llm/generate', {
       method: 'POST',
       body: JSON.stringify({
         prompt_type: 'product_description',
         inputs: { product_name: productName },
       }),
     })
     return response.json()
   }
   ```

2. **SEO Meta Tag Generator**
   ```tsx
   async function generateMetaTags(pageContent: string) {
     // Calls LLM Gateway to create title, description, keywords
   }
   ```

3. **Chatbot Widget on Public Site**
   ```tsx
   // components/sections/ChatbotSection.tsx
   'use client'

   export function ChatbotSection({ botConfig }: { botConfig: any }) {
     const [messages, setMessages] = useState([])

     const sendMessage = async (userMessage: string) => {
       const response = await fetch('/api/chatbot/message', {
         method: 'POST',
         body: JSON.stringify({
           site_id: botConfig.site_id,
           message: userMessage,
           context: botConfig.context,  // Site-specific context
         }),
       })
       const { reply } = await response.json()
       setMessages([...messages, { role: 'user', content: userMessage }, { role: 'bot', content: reply }])
     }

     return <ChatWidget messages={messages} onSend={sendMessage} />
   }
   ```

---

### 4.8 How Different Site Types Share Same Codebase

**Configuration-Driven Approach:**

| Website Type | Template | Enabled Sections | Special Features |
|--------------|----------|------------------|------------------|
| **Departmental Store** | `modern_store` | hero, product_grid, testimonials, contact_form, whatsapp_button | Shopping cart, COD payments |
| **Tiffin Service** | `food_service` | hero, menu_grid (products), subscription_plans, booking (delivery slots), testimonials | Recurring orders |
| **Salon/Spa** | `booking_service` | hero, service_grid, staff_profiles, booking_calendar, testimonials | Appointment booking |
| **Coaching Center** | `education` | hero, course_grid, instructor_profiles, lead_form, blog | Lead capture, courses as products |
| **Clinic** | `healthcare` | hero, services_grid, doctor_profiles, booking_calendar, contact_form | HIPAA-compliant booking |

**Site-Type-Specific Logic:**

```typescript
// lib/site-types.ts
export const SITE_TYPE_CONFIG = {
  departmental_store: {
    features: ['products', 'cart', 'orders', 'cod_payment'],
    default_sections: ['hero', 'product_grid', 'testimonials', 'contact_form'],
    required_services: ['storefront-service'],
  },
  tiffin_service: {
    features: ['products', 'subscriptions', 'delivery_slots'],
    default_sections: ['hero', 'menu_grid', 'subscription_plans', 'testimonials'],
    required_services: ['storefront-service', 'booking-service'],
  },
  salon: {
    features: ['services', 'staff', 'bookings'],
    default_sections: ['hero', 'service_grid', 'staff_profiles', 'booking_calendar'],
    required_services: ['booking-service'],
  },
  // ... more site types
}
```

**New Site Creation Flow:**

1. User selects site type (dropdown)
2. Frontend fetches template for that site type
3. Site Service creates site record with:
   - Pre-configured sections from template
   - Default theme colors/fonts
   - Feature flags based on site type
4. User customizes via admin panel
5. Site goes live

---

## 5. Orchestration Hooks & Event Model

### 5.1 Event-Driven Architecture

**Core Principle:** Domain services emit events for significant state changes. Orchestration layer (future) subscribes to events and coordinates cross-service workflows.

**Event Bus Technology:**

**Recommended: Redis Streams** (for MVP)
- ✅ Lightweight, simple to set up
- ✅ Consumer groups for multiple subscribers
- ✅ Event persistence and replay
- ✅ Already using Redis for caching

**Alternative: RabbitMQ** (for production scale)
- ✅ Advanced routing (topics, exchanges)
- ✅ Better durability guarantees
- ✅ Dead letter queues
- ❌ More operational overhead

---

### 5.2 Event Schema Standard

**All events follow CloudEvents specification:**

```json
{
  "specversion": "1.0",
  "type": "com.yourplatform.order.placed",
  "source": "storefront-service",
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "time": "2025-11-17T10:30:00Z",
  "datacontenttype": "application/json",
  "data": {
    "order_id": "ord_abc123",
    "site_id": "site_xyz",
    "org_id": "org_123",
    "total": 1250.00,
    "customer": {
      "name": "Ram Kumar",
      "phone": "+911234567890",
      "email": "ram@example.com"
    },
    "items": [
      {
        "product_id": "prod_123",
        "product_name": "Tata Salt 1kg",
        "quantity": 2,
        "unit_price": 20.00
      }
    ]
  }
}
```

**Event Naming Convention:**

```
{domain}.{entity}.{action}

Examples:
- site.created
- site.published
- site.suspended
- order.placed
- order.confirmed
- order.dispatched
- order.delivered
- order.cancelled
- booking.created
- booking.confirmed
- booking.completed
- booking.no_show
- lead.created
- lead.contacted
- payment.succeeded
- payment.failed
- subscription.started
- subscription.renewed
- subscription.cancelled
```

---

### 5.3 Event Topics (Redis Streams / RabbitMQ)

```
site-events         # All site-related events
order-events        # Order lifecycle events
booking-events      # Booking lifecycle events
lead-events         # Lead/inquiry events
payment-events      # Payment status changes (from Billing Service)
notification-events # Notification delivery status (from Notification Service)
user-events         # User signup, profile changes (from User Service)
```

---

### 5.4 Domain Service Event Publishing

**Example: Storefront Service publishes ORDER_PLACED event**

```python
# storefront-service/app/services/order_service.py
from app.events.publisher import publish_event
from app.models import Order

async def create_order(order_data: dict) -> Order:
    # 1. Validate and create order in database
    order = Order(**order_data)
    db.add(order)
    await db.commit()

    # 2. Publish event
    await publish_event(
        topic='order-events',
        event_type='order.placed',
        data={
            'order_id': str(order.order_id),
            'site_id': str(order.site_id),
            'org_id': str(order.org_id),
            'total': float(order.total),
            'customer': {
                'name': order.customer_name,
                'phone': order.customer_phone,
                'email': order.customer_email,
            },
            'items': [
                {
                    'product_id': str(item.product_id),
                    'product_name': item.product_name,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                }
                for item in order.items
            ],
        }
    )

    return order
```

**Event Publisher Library:**

```python
# shared/events/publisher.py
import redis.asyncio as redis
import json
from datetime import datetime
from uuid import uuid4

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

async def publish_event(topic: str, event_type: str, data: dict, source: str = None):
    event = {
        'specversion': '1.0',
        'type': f'com.yourplatform.{event_type}',
        'source': source or 'unknown-service',
        'id': str(uuid4()),
        'time': datetime.utcnow().isoformat() + 'Z',
        'datacontenttype': 'application/json',
        'data': data,
    }

    await redis_client.xadd(
        topic,
        {'event': json.dumps(event)},
        maxlen=10000,  # Keep last 10k events
    )
```

---

### 5.5 What Logic Stays in Domain Services vs Orchestration

**Domain Services (Storefront, Booking, etc.):**

✅ **DO Handle:**
- Single-entity validation (is product in stock?)
- State transitions for one entity (order: placed → confirmed)
- Database CRUD operations
- Emitting events for state changes
- Idempotent operations (safe to retry)

❌ **DO NOT Handle:**
- Cross-service coordination (e.g., "create order AND book delivery slot AND charge card")
- Long-running workflows (e.g., "send reminder after 24 hours")
- Retries and compensation logic (e.g., "refund if delivery fails")
- Complex decision trees spanning multiple services

**Orchestration Layer (Temporal / Camunda / n8n):**

✅ **DO Handle:**
- Multi-step workflows (saga patterns)
- Timers and delays (send reminder in 30 minutes)
- Compensation logic (rollback order if payment fails)
- Human-in-the-loop steps (manual order approval)
- Workflow state management (persist workflow progress)
- Retries with exponential backoff
- Calling multiple domain services in sequence

❌ **DO NOT Handle:**
- Direct database access to domain service DBs
- Business validation (delegate to domain services)
- Event publishing (domain services publish events)

---

### 5.6 Future Orchestration Layer Integration

**Recommended: Temporal**

**Why Temporal:**
- ✅ Durable workflows (survive crashes, restarts)
- ✅ Versioning (update workflows without breaking in-flight instances)
- ✅ Strong Python/Go SDKs
- ✅ Excellent visibility and debugging UI
- ✅ Built-in retries, timeouts, saga support

**Example Workflow: Order Confirmation Flow**

```python
# orchestration-service/workflows/order_confirmation.py
from temporalio import workflow
from datetime import timedelta

@workflow.defn
class OrderConfirmationWorkflow:
    @workflow.run
    async def run(self, order_placed_event: dict) -> str:
        order_id = order_placed_event['data']['order_id']
        site_id = order_placed_event['data']['site_id']
        customer_phone = order_placed_event['data']['customer']['phone']

        # Step 1: Send immediate confirmation to customer
        await workflow.execute_activity(
            send_notification,
            args=[{
                'template': 'order_confirmation',
                'recipient': customer_phone,
                'data': {'order_id': order_id},
            }],
            start_to_close_timeout=timedelta(minutes=1),
        )

        # Step 2: Notify store owner
        await workflow.execute_activity(
            send_notification,
            args=[{
                'template': 'new_order_alert',
                'recipient': await get_site_owner_phone(site_id),
                'data': {'order_id': order_id},
            }],
            start_to_close_timeout=timedelta(minutes=1),
        )

        # Step 3: Wait 30 minutes for owner to confirm
        confirmed = await workflow.wait_condition(
            lambda: self.order_confirmed,
            timeout=timedelta(minutes=30),
        )

        if not confirmed:
            # Step 4a: Send reminder to owner
            await workflow.execute_activity(
                send_notification,
                args=[{
                    'template': 'order_confirmation_reminder',
                    'recipient': await get_site_owner_phone(site_id),
                    'data': {'order_id': order_id},
                }],
            )

            # Wait another 30 minutes
            confirmed = await workflow.wait_condition(
                lambda: self.order_confirmed,
                timeout=timedelta(minutes=30),
            )

            if not confirmed:
                # Step 4b: Auto-cancel order
                await workflow.execute_activity(
                    cancel_order,
                    args=[order_id, 'No response from owner'],
                )

                # Notify customer
                await workflow.execute_activity(
                    send_notification,
                    args=[{
                        'template': 'order_cancelled',
                        'recipient': customer_phone,
                        'data': {'order_id': order_id, 'reason': 'Store did not respond'},
                    }],
                )
                return 'cancelled'

        # Step 5: Order confirmed, send update to customer
        await workflow.execute_activity(
            send_notification,
            args=[{
                'template': 'order_confirmed_by_store',
                'recipient': customer_phone,
                'data': {'order_id': order_id},
            }],
        )

        return 'confirmed'

    @workflow.signal
    async def order_confirmed_signal(self):
        self.order_confirmed = True
```

**Activity Definitions (calling domain services):**

```python
# orchestration-service/activities/notifications.py
from temporalio import activity
import httpx

@activity.defn
async def send_notification(payload: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'http://notification-service:8004/v1/notifications/send',
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

@activity.defn
async def cancel_order(order_id: str, reason: str):
    async with httpx.AsyncClient() as client:
        response = await client.patch(
            f'http://storefront-service:8011/v1/orders/{order_id}/cancel',
            json={'reason': reason},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
```

---

### 5.7 How Orchestration Layer Calls Core Services

**Pattern: Activities make HTTP calls to service APIs**

```python
# Billing integration
@activity.defn
async def upgrade_subscription(org_id: str, new_plan: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'http://billing-service:8002/v1/subscriptions/upgrade',
            json={'org_id': org_id, 'plan': new_plan},
            headers={'Authorization': f'Bearer {get_service_token()}'},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

# LLM Gateway integration
@activity.defn
async def generate_order_summary(order_id: str):
    order = await fetch_order(order_id)

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f'http://llm-gateway:8003/v1/prompts/execute',
            json={
                'prompt_id': 'order_summary',
                'inputs': {
                    'items': order['items'],
                    'total': order['total'],
                },
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()['output']

# Logging integration
@activity.defn
async def log_workflow_step(workflow_id: str, step: str, data: dict):
    async with httpx.AsyncClient() as client:
        await client.post(
            f'http://logging-service:8005/v1/logs',
            json={
                'level': 'info',
                'message': f'Workflow {workflow_id} completed step {step}',
                'context': data,
            },
        )
```

---

## 6. Example End-to-End Flow: Local Departmental Store

### Scenario: "Ram's Grocery" Website

**Site Owner:** Ram Kumar
**Site Type:** Departmental Store
**Features:** Product catalog, shopping cart, WhatsApp ordering, COD payments

---

### 6.1 Step: Site Owner Signs Up and Creates Site

**Frontend Flow:**

1. User visits `yourplatform.com` and clicks "Create Your Store"
2. Sign-up form rendered by Next.js frontend
3. User enters: name, email, phone, password, store name, category

**API Calls:**

```
POST /v1/auth/signup (Auth Service:8000)
→ Creates user account, returns JWT token

POST /v1/orgs (User Service:8001)
→ Creates organization "Ram's Grocery"
→ Links user as owner

POST /v1/subscriptions (Billing Service:8002)
→ Creates free trial subscription
→ Returns subscription_id

POST /v1/sites (Site Service:8010)
→ Creates site with:
   - slug: "rams-grocery"
   - site_type: "departmental_store"
   - template_id: "modern_store"
   - org_id from User Service
→ Returns site_id
```

**Events Emitted:**

```json
{
  "type": "com.yourplatform.user.signed_up",
  "source": "auth-service",
  "data": {
    "user_id": "user_123",
    "email": "ram@example.com"
  }
}

{
  "type": "com.yourplatform.site.created",
  "source": "site-service",
  "data": {
    "site_id": "site_xyz",
    "org_id": "org_123",
    "site_type": "departmental_store",
    "slug": "rams-grocery"
  }
}
```

**Orchestration Hook (Future):**

- Listen to `user.signed_up` event
- Workflow:
  1. Send welcome email (Notification Service)
  2. Schedule onboarding email series (day 1, 3, 7)
  3. Log user acquisition (Logging Service)
  4. Create CRM record (if integrated)

**Which Services Involved:**

| Step | Frontend Component | Domain Service | Core Service | Event Emitted |
|------|-------------------|----------------|--------------|---------------|
| Sign-up form | `SignUpForm.tsx` | - | Auth Service (8000) | user.signed_up |
| Create org | - | - | User Service (8001) | org.created |
| Create subscription | - | - | Billing Service (8002) | subscription.created |
| Create site | `SiteSetupWizard.tsx` | Site Service (8010) | - | site.created |
| Welcome email | - | - | Notification Service (8004) | - |

---

### 6.2 Step: Owner Adds Products to Catalog

**Frontend Flow:**

1. Owner logs into Admin Panel at `yourplatform.com/admin/products`
2. Clicks "Add Product"
3. Form: name, description, price, category, image upload
4. Clicks "Generate Description" → calls LLM Gateway for AI-generated copy
5. Saves product

**API Calls:**

```
POST /v1/sites/{site_id}/categories (Storefront Service:8011)
→ Creates category "Groceries"

POST /v1/sites/{site_id}/products (Storefront Service:8011)
→ Creates product:
   - name: "Tata Salt 1kg"
   - price: 20.00
   - stock_quantity: 100

POST /v1/prompts/execute (LLM Gateway:8003)
→ Prompt: "Generate SEO product description"
→ Input: {"product_name": "Tata Salt 1kg"}
→ Output: "Premium iodized salt from Tata, essential for daily cooking..."

POST /v1/logs (Logging Service:8005)
→ Log: "Product created: Tata Salt 1kg by user_123"
```

**Events Emitted:**

```json
{
  "type": "com.yourplatform.product.created",
  "source": "storefront-service",
  "data": {
    "product_id": "prod_123",
    "site_id": "site_xyz",
    "name": "Tata Salt 1kg",
    "price": 20.00
  }
}
```

**Orchestration Hook (Future):**

- None needed (simple CRUD)

**Which Services Involved:**

| Step | Frontend Component | Domain Service | Core Service | Event Emitted |
|------|-------------------|----------------|--------------|---------------|
| Product form | `ProductForm.tsx` | Storefront Service (8011) | - | - |
| AI description | `AIContentSuggester.tsx` | - | LLM Gateway (8003) | - |
| Save product | - | Storefront Service (8011) | Logging Service (8005) | product.created |

---

### 6.3 Step: Customer Browses Products and Adds to Cart

**Frontend Flow:**

1. Customer visits `yourplatform.com/rams-grocery`
2. Middleware resolves slug → site config
3. Home page renders with HeroSection, ProductGridSection
4. Customer clicks "View Products"
5. Product listing page shows all products
6. Customer clicks "Add to Cart" on "Tata Salt 1kg"
7. Cart icon updates (client-side state + session storage)

**API Calls:**

```
GET /v1/sites/by-slug/rams-grocery (Site Service:8010)
→ Returns site config (cached)

GET /v1/sites/{site_id}/pages/ (Site Service:8010)
→ Returns sections for home page

GET /v1/sites/{site_id}/products (Storefront Service:8011)
→ Returns product list

POST /v1/sites/{site_id}/carts (Storefront Service:8011)
→ Creates cart (session-based, no user_id yet)

POST /v1/sites/{site_id}/carts/{cart_id}/items (Storefront Service:8011)
→ Adds item to cart
```

**Events Emitted:**

```json
{
  "type": "com.yourplatform.cart.item_added",
  "source": "storefront-service",
  "data": {
    "cart_id": "cart_abc",
    "product_id": "prod_123",
    "quantity": 1
  }
}
```

**Orchestration Hook (Future):**

- Listen to `cart.item_added`
- Workflow: If cart idle for 30 minutes, send "Complete your order" WhatsApp message (if phone captured)

**Which Services Involved:**

| Step | Frontend Component | Domain Service | Core Service | Event Emitted |
|------|-------------------|----------------|--------------|---------------|
| Site load | `app/[slug]/page.tsx` | Site Service (8010) | - | - |
| Product list | `ProductGridSection.tsx` | Storefront Service (8011) | - | - |
| Add to cart | `AddToCartButton.tsx` | Storefront Service (8011) | - | cart.item_added |

---

### 6.4 Step: Customer Checks Out (Places Order)

**Frontend Flow:**

1. Customer clicks "Checkout" in cart
2. Checkout form: name, phone, delivery address
3. Payment method selection: "Cash on Delivery" (only option for MVP)
4. Clicks "Place Order"
5. Order confirmation page shown with order number

**API Calls:**

```
POST /v1/sites/{site_id}/orders (Storefront Service:8011)
→ Creates order:
   - customer_name: "Anjali Sharma"
   - customer_phone: "+919876543210"
   - payment_method: "cod"
   - order_status: "placed"
→ Deducts stock quantity
→ Clears cart

POST /v1/logs (Logging Service:8005)
→ Log order placement

(Event triggers notification via event listener)
```

**Events Emitted:**

```json
{
  "type": "com.yourplatform.order.placed",
  "source": "storefront-service",
  "data": {
    "order_id": "ord_abc123",
    "site_id": "site_xyz",
    "order_number": "ORD-1001",
    "total": 1250.00,
    "customer": {
      "name": "Anjali Sharma",
      "phone": "+919876543210",
      "email": null
    },
    "items": [
      {
        "product_id": "prod_123",
        "product_name": "Tata Salt 1kg",
        "quantity": 2,
        "unit_price": 20.00
      },
      {
        "product_id": "prod_456",
        "product_name": "Basmati Rice 5kg",
        "quantity": 1,
        "unit_price": 500.00
      }
    ]
  }
}
```

**Which Services Involved:**

| Step | Frontend Component | Domain Service | Core Service | Event Emitted |
|------|-------------------|----------------|--------------|---------------|
| Checkout form | `CheckoutForm.tsx` | - | - | - |
| Place order | - | Storefront Service (8011) | Logging Service (8005) | order.placed |

---

### 6.5 Step: Notifications Sent (Email/WhatsApp)

**Event-Driven Flow:**

1. Notification Service subscribes to `order-events` stream
2. Receives `order.placed` event
3. Looks up notification templates for "order_confirmation"
4. Sends:
   - WhatsApp to customer (+919876543210): "Your order ORD-1001 is placed. Total: ₹1250. We'll confirm soon!"
   - WhatsApp to store owner (fetched from site config): "New order ORD-1001 received. Total: ₹1250. [View Order Link]"

**API Calls (by Notification Service):**

```
POST /v1/notifications/send (Notification Service:8004)
→ Internal call to send WhatsApp via Twilio/Gupshup

POST /v1/logs (Logging Service:8005)
→ Log notification sent
```

**Events Emitted:**

```json
{
  "type": "com.yourplatform.notification.sent",
  "source": "notification-service",
  "data": {
    "notification_id": "notif_123",
    "template": "order_confirmation",
    "channel": "whatsapp",
    "recipient": "+919876543210",
    "status": "delivered"
  }
}
```

**Which Services Involved:**

| Step | Frontend Component | Domain Service | Core Service | Event Emitted |
|------|-------------------|----------------|--------------|---------------|
| Listen to events | - | - | Notification Service (8004) | notification.sent |
| Log notification | - | - | Logging Service (8005) | - |

---

### 6.6 Step: Store Owner Confirms Order

**Frontend Flow:**

1. Owner receives WhatsApp notification with link to admin panel
2. Clicks link → opens `yourplatform.com/admin/orders/ord_abc123`
3. Sees order details
4. Clicks "Confirm Order" button
5. Order status changes to "confirmed"

**API Calls:**

```
PATCH /v1/sites/{site_id}/orders/{order_id}/status (Storefront Service:8011)
→ Updates order_status: "placed" → "confirmed"

POST /v1/logs (Logging Service:8005)
→ Log status change
```

**Events Emitted:**

```json
{
  "type": "com.yourplatform.order.confirmed",
  "source": "storefront-service",
  "data": {
    "order_id": "ord_abc123",
    "confirmed_by_user_id": "user_123",
    "confirmed_at": "2025-11-17T10:45:00Z"
  }
}
```

**Notification Flow:**

- Notification Service listens to `order.confirmed` event
- Sends WhatsApp to customer: "Good news! Your order ORD-1001 is confirmed. Expected delivery in 30 mins."

**Which Services Involved:**

| Step | Frontend Component | Domain Service | Core Service | Event Emitted |
|------|-------------------|----------------|--------------|---------------|
| Order detail page | `OrderDetailPage.tsx` | - | - | - |
| Confirm order | `ConfirmOrderButton.tsx` | Storefront Service (8011) | Logging Service (8005) | order.confirmed |
| Send confirmation | - | - | Notification Service (8004) | notification.sent |

---

### 6.7 Step: Future Orchestration Workflow

**Without Orchestration (Current):**

- Owner manually confirms order
- If owner forgets, order sits in "placed" status forever
- No automated reminders

**With Orchestration (Future):**

**Workflow: Order Confirmation with Auto-Escalation**

```
ORDER_PLACED event received
   ↓
Send confirmation to customer (WhatsApp)
   ↓
Send alert to owner (WhatsApp)
   ↓
Wait 30 minutes
   ↓
Is order confirmed?
   ├─ YES → Send confirmed message to customer → END
   └─ NO  → Send reminder to owner
           ↓
           Wait 30 minutes
           ↓
           Is order confirmed?
              ├─ YES → Send confirmed message to customer → END
              └─ NO  → Auto-cancel order
                      ↓
                      Send cancellation to customer
                      ↓
                      Log to audit trail
                      ↓
                      END
```

**Benefits:**

- ✅ No orders lost due to inattention
- ✅ Better customer experience (timely updates)
- ✅ Automated follow-ups reduce manual work
- ✅ Full audit trail in Temporal UI

**Orchestration Service Calls:**

- **Storefront Service:** Fetch order details, update status, cancel order
- **Notification Service:** Send WhatsApp messages at each step
- **Logging Service:** Log workflow progress
- **Billing Service:** Check if site's plan allows auto-cancellation (feature flag)

---

### 6.8 Complete Flow Diagram

```
┌──────────────┐
│   CUSTOMER   │
└──────┬───────┘
       │
       ▼
┌────────────────────────────────────────────────────────┐
│  FRONTEND (Next.js)                                    │
│  yourplatform.com/rams-grocery                         │
│                                                        │
│  [HeroSection] [ProductGridSection] [CartWidget]      │
└────────┬───────────────────────────────────────────────┘
         │
         │ GET /sites/by-slug/rams-grocery
         │ GET /products
         │ POST /carts, POST /carts/{id}/items
         │ POST /orders
         │
         ▼
┌────────────────────────────────────────────────────────┐
│  DOMAIN SERVICES                                       │
│                                                        │
│  ┌─────────────────┐  ┌─────────────────┐            │
│  │ Site Service    │  │ Storefront Svc  │            │
│  │ (8010)          │  │ (8011)          │            │
│  │                 │  │                 │            │
│  │ - Get site cfg  │  │ - Products      │            │
│  │ - Get sections  │  │ - Cart          │            │
│  └─────────────────┘  │ - Orders        │            │
│                       └────────┬────────┘            │
│                                │                      │
│                                │ Emit events          │
│                                ▼                      │
│                       ┌─────────────────┐            │
│                       │  EVENT BUS      │            │
│                       │  (Redis)        │            │
│                       │                 │            │
│                       │ - order.placed  │            │
│                       │ - order.confirmed│            │
│                       └────────┬────────┘            │
└────────────────────────────────┼────────────────────┘
                                 │
                 ┌───────────────┼───────────────┐
                 │               │               │
                 ▼               ▼               ▼
         ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
         │ Notification │ │  Logging     │ │ Orchestration│
         │ Service      │ │  Service     │ │ (Future)     │
         │ (8004)       │ │  (8005)      │ │ Temporal     │
         │              │ │              │ │              │
         │ - WhatsApp   │ │ - Audit logs │ │ - Workflows  │
         │ - Email      │ │              │ │ - Timers     │
         └──────────────┘ └──────────────┘ └──────────────┘
                 │                                 │
                 │                                 │
                 ▼                                 ▼
         ┌──────────────┐                 ┌──────────────┐
         │   CUSTOMER   │                 │ SITE OWNER   │
         │              │                 │              │
         │ Order conf.  │                 │ New order    │
         │ WhatsApp     │                 │ alert        │
         └──────────────┘                 └──────────────┘
```

---

## 7. Modularity & Extensibility Guidelines

### 7.1 Service Naming Conventions

**Domain Services:**

- Pattern: `{domain}-service`
- Examples: `site-service`, `storefront-service`, `booking-service`
- Port allocation: `801X` (8010-8019 reserved for domain services)

**API Versioning:**

- All APIs use `/v1/` prefix
- Breaking changes require new version: `/v2/`
- Maintain backwards compatibility for at least 6 months

**Database Naming:**

- One database per service: `site_service_db`, `storefront_service_db`
- Tables snake_case: `site_sections`, `order_items`
- Primary keys: `{entity}_id` (e.g., `site_id`, `order_id`)

**Event Naming:**

- Pattern: `{domain}.{entity}.{action}`
- Examples: `order.placed`, `booking.confirmed`, `site.published`

---

### 7.2 How to Add a New Website Type

**Example: Adding "Coaching Center" Website Type**

**Step 1: Define Site Type Config**

```typescript
// lib/site-types.ts
export const SITE_TYPE_CONFIG = {
  // ... existing types

  coaching_center: {
    features: ['courses', 'instructors', 'enrollments', 'leads', 'blog'],
    default_sections: [
      'hero',
      'course_grid',
      'instructor_profiles',
      'testimonials',
      'lead_form',
      'blog_preview',
    ],
    required_services: ['content-service', 'lead-service'],
    optional_services: ['storefront-service'], // If selling courses
  },
}
```

**Step 2: Create Template in Site Service**

```sql
INSERT INTO templates (template_id, template_name, site_type, layout_config, style_config)
VALUES (
  gen_random_uuid(),
  'modern_coaching',
  'coaching_center',
  '{
    "sections": [
      {"type": "hero", "props": {"title": "Welcome to Our Academy", "cta_text": "Explore Courses"}},
      {"type": "course_grid", "props": {"columns": 3, "show_price": true}},
      {"type": "instructor_profiles", "props": {"layout": "carousel"}},
      {"type": "testimonials", "props": {"count": 6}},
      {"type": "lead_form", "props": {"fields": ["name", "phone", "course_interest"]}},
      {"type": "blog_preview", "props": {"count": 3}}
    ]
  }',
  '{
    "primary_color": "#4f46e5",
    "secondary_color": "#06b6d4",
    "font_family": "Poppins, sans-serif"
  }'
);
```

**Step 3: Add New Section Components (if needed)**

```tsx
// components/sections/CourseGridSection.tsx
export function CourseGridSection({
  columns = 3,
  show_price = true,
}: {
  columns?: number
  show_price?: boolean
}) {
  const { siteId } = useSiteConfig()
  const courses = useCourses(siteId) // Fetch from Storefront Service (products as courses)

  return (
    <section className="py-16">
      <div className="container mx-auto px-4">
        <div className={`grid grid-cols-1 md:grid-cols-${columns} gap-8`}>
          {courses.map((course) => (
            <CourseCard
              key={course.product_id}
              title={course.name}
              description={course.short_description}
              price={show_price ? course.price : null}
              image={course.images[0]}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
```

**Step 4: Update Section Renderer**

```typescript
// components/SectionRenderer.tsx
const SECTION_COMPONENTS = {
  // ... existing sections
  course_grid: CourseGridSection,
  instructor_profiles: InstructorProfilesSection,
}
```

**Step 5: No Backend Changes Needed!**

- ✅ Reuse **Storefront Service** (products = courses)
- ✅ Reuse **Content Service** (instructors = blog posts or custom pages)
- ✅ Reuse **Lead Service** (inquiries)
- ✅ Reuse **Booking Service** (if offering consultations/demos)

**Step 6: Test and Deploy**

```bash
# Add coaching_center to site type options in frontend
# Test site creation flow
# Deploy to staging
# QA test
# Deploy to production
```

**Effort Estimate:**
- Configuration: 1 hour
- New section components: 4-8 hours (if needed)
- Testing: 2-4 hours
- **Total: ~1 day** (vs 2-4 weeks for building from scratch)

---

### 7.3 When to Create a New Domain Service vs Reuse

**Create New Service When:**

- ✅ Entities have fundamentally different lifecycles (e.g., Booking vs Order)
- ✅ Domain requires specialized logic (e.g., Inventory Management with bin locations)
- ✅ Service will have different scaling needs (e.g., high-volume Chat Service)
- ✅ Service has external integrations (e.g., Shipping Service integrating with logistics APIs)

**Reuse Existing Service When:**

- ✅ Entities are conceptually similar (Courses = Products, Enrollments = Orders)
- ✅ Logic is generic and configurable (Forms, Widgets, Content)
- ✅ Domain is small and unlikely to grow complex (Simple Contact Forms)

**Example Decision Matrix:**

| Website Type | Catalog Needs | Use Storefront Service? | Booking Needs | Use Booking Service? | New Service Needed? |
|--------------|---------------|------------------------|---------------|---------------------|---------------------|
| Departmental Store | Products | ✅ Yes | No | ❌ No | ❌ No |
| Tiffin Service | Meal plans (products) | ✅ Yes | Delivery slots | ✅ Yes (or extend Storefront) | ❌ No |
| Salon | Services | ✅ Yes (services as products) | Appointments | ✅ Yes | ❌ No |
| Coaching Center | Courses | ✅ Yes (courses as products) | No | ❌ No | ❌ No |
| Real Estate | Properties | ⚠️ Maybe (or create Property Service) | Site visits | ✅ Yes | ⚠️ Maybe (Property Service) |
| Rental Marketplace | Rental items | ⚠️ Maybe (or extend Storefront) | Rental periods | ❌ No (custom Rental Service) | ✅ Yes (Rental Service) |

---

### 7.4 Keeping Core Services Stable

**Golden Rules:**

1. **Never add business-specific logic to core services**
   - ❌ BAD: Adding "calculate store order discount" to Billing Service
   - ✅ GOOD: Domain service calculates discount, Billing Service processes payment

2. **Core services expose generic capabilities**
   - ✅ Auth: "Authenticate user", "Validate token"
   - ✅ Notification: "Send message", not "Send order confirmation"
   - ✅ LLM Gateway: "Execute prompt", not "Generate product description"

3. **Core services are versioned independently**
   - Each core service has own semantic versioning
   - Breaking changes communicated 3 months in advance
   - Deprecation policy: support N-1 version for 6 months

4. **Core services have stable APIs**
   - Add new endpoints, don't change existing ones
   - Use API versioning for breaking changes
   - Provide client SDKs for all services

5. **Core services don't know about domain services**
   - No hardcoded references to Storefront, Booking, etc.
   - Communication via events only (loose coupling)

---

### 7.5 Keeping Domain Services Independent

**Best Practices:**

1. **No direct HTTP calls between domain services**
   - ❌ BAD: Storefront Service calls Booking Service API
   - ✅ GOOD: Storefront emits event, Orchestration calls both

2. **Shared data via events**
   - If Booking Service needs product info, subscribe to `product.*` events
   - Maintain local cache/replica if needed (eventual consistency)

3. **Foreign keys via IDs only**
   - Store `product_id`, not product data
   - Join data at API layer or frontend (BFF pattern)

4. **Database per service**
   - No shared databases
   - Strict schema ownership

5. **Independent deployability**
   - Each service has own CI/CD pipeline
   - Rolling updates without downtime
   - Feature flags for gradual rollout

---

### 7.6 Frontend Configuration-Driven Development

**Principles:**

1. **No hardcoded business logic in components**
   - ✅ Components receive config as props
   - ✅ Business rules fetched from APIs

2. **Section library is extensible**
   - Easy to add new section types
   - Sections are composable
   - Props validated via TypeScript interfaces

3. **Themes are data-driven**
   - Colors, fonts, spacing from site config
   - CSS variables for dynamic theming
   - No hardcoded style values

4. **Routes are dynamic**
   - No separate apps per site
   - Middleware resolves site from slug/domain
   - Pages built from section configs

5. **Admin panel is generic**
   - Same editor for all site types
   - Section library filtered by site type
   - No custom admin UIs per site

---

### 7.7 Testing Strategy

**Unit Tests:**

- Each service: 80%+ coverage
- Focus on business logic, validation
- Mock external dependencies

**Integration Tests:**

- Test service-to-service communication
- Use test database with fixtures
- Test event publishing and consumption

**E2E Tests (Frontend):**

- Test critical user flows:
  - Site creation
  - Product creation
  - Order placement
  - Booking flow
- Use Playwright or Cypress
- Run against staging environment

**Performance Tests:**

- Load testing for domain services (Apache JMeter / k6)
- Frontend performance (Lighthouse CI)
- Database query optimization (explain plans)

**Contract Tests:**

- Ensure API contracts don't break (Pact)
- Test event schema compatibility

---

### 7.8 Deployment Strategy

**Containerization:**

- Docker for all services
- Multi-stage builds (builder + runtime)
- Alpine-based images for small size

**Orchestration:**

- Kubernetes (GKE / EKS / AKS) for production
- Docker Compose for local development
- Helm charts for K8s deployments

**CI/CD Pipeline:**

```yaml
# .github/workflows/deploy-storefront-service.yml
name: Deploy Storefront Service

on:
  push:
    branches: [main]
    paths:
      - 'domain-services/storefront-service/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run unit tests
        run: |
          cd domain-services/storefront-service
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: |
          docker build -t storefront-service:${{ github.sha }} \
            domain-services/storefront-service
      - name: Push to registry
        run: |
          docker tag storefront-service:${{ github.sha }} \
            registry.yourplatform.com/storefront-service:latest
          docker push registry.yourplatform.com/storefront-service:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/storefront-service \
            storefront-service=registry.yourplatform.com/storefront-service:latest
          kubectl rollout status deployment/storefront-service
```

**Monitoring:**

- Logs: Centralized logging (ELK Stack / Grafana Loki)
- Metrics: Prometheus + Grafana
- Tracing: OpenTelemetry + Jaeger
- Alerts: PagerDuty / Opsgenie

---

### 7.9 Documentation Standards

**Required Documentation:**

1. **API Documentation (OpenAPI/Swagger)**
   - All endpoints documented
   - Request/response schemas
   - Example payloads
   - Error codes

2. **Architecture Decision Records (ADRs)**
   - Document major decisions
   - Template: Context, Decision, Consequences
   - Store in `/docs/adr/`

3. **Runbooks**
   - How to deploy services
   - How to troubleshoot common issues
   - How to scale services

4. **Developer Onboarding Guide**
   - Setup local environment
   - Run services locally
   - Make first contribution

---

## 8. Next Steps (Implementation Roadmap)

### Phase 1: MVP (Weeks 1-4)

**Week 1-2: Foundation**
- [ ] Set up monorepo structure (Turborepo / Nx)
- [ ] Implement Site Service (8010)
- [ ] Implement Storefront Service (8011)
- [ ] Set up PostgreSQL databases
- [ ] Set up Redis for caching and event bus

**Week 3-4: Frontend**
- [ ] Build Next.js multi-tenant app
- [ ] Implement dynamic routing (slug-based)
- [ ] Build 5 core section components (hero, product grid, testimonials, contact form, WhatsApp button)
- [ ] Build basic admin panel (site editor, product management)
- [ ] Integrate with LLM Gateway for content suggestions

**MVP Deliverable:**
- 1 website type (Departmental Store) fully functional
- Site creation, product catalog, shopping cart, order placement (COD only)
- WhatsApp notifications

---

### Phase 2: Expand (Weeks 5-8)

**Week 5-6: More Services**
- [ ] Implement Booking Service (8012)
- [ ] Implement Lead Service (8013)
- [ ] Implement Content Service (8014)
- [ ] Implement Widget Service (8015)

**Week 7-8: More Website Types**
- [ ] Add "Tiffin Service" template
- [ ] Add "Salon/Spa" template
- [ ] Add "Coaching Center" template
- [ ] Build advanced admin features (analytics dashboard, bulk product upload)

---

### Phase 3: Orchestration (Weeks 9-12)

**Week 9-10: Event Infrastructure**
- [ ] Migrate from Redis Streams to RabbitMQ (if needed)
- [ ] Implement event schemas and validation
- [ ] Build event monitoring dashboard

**Week 11-12: Temporal Integration**
- [ ] Set up Temporal server
- [ ] Implement 3 core workflows (order confirmation, booking reminders, lead nurturing)
- [ ] Build workflow monitoring UI

---

### Phase 4: Scale (Weeks 13-16)

**Week 13-14: Performance**
- [ ] Implement caching strategies (site configs, product catalogs)
- [ ] Database query optimization
- [ ] Frontend performance tuning (code splitting, image optimization)

**Week 15-16: Production Readiness**
- [ ] Security audit (OWASP top 10)
- [ ] Load testing
- [ ] Disaster recovery plan
- [ ] Production deployment

---

## Conclusion

This architecture provides a **future-proof, modular foundation** for building a multi-website platform for small businesses. Key advantages:

✅ **Reusability:** Core and domain services are generic; new website types added via configuration
✅ **Scalability:** Services independently scalable; event-driven for async processing
✅ **Maintainability:** Clear separation of concerns; stable APIs; well-documented
✅ **Extensibility:** Orchestration layer can be added without rewrites
✅ **Developer Experience:** Monorepo, shared types, consistent patterns

**Total Estimated Effort:** 16 weeks for full implementation (3-4 developers)
**MVP Timeline:** 4 weeks (1 website type + core features)

---

**Document Owner:** System Architect
**Last Updated:** 2025-11-17
**Status:** Ready for Implementation
