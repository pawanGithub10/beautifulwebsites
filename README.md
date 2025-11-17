# Beautiful Websites - Multi-Website Platform

A modular, scalable platform for creating and managing multiple small business websites.

## 🎯 Overview

This platform enables rapid deployment of custom-branded websites for small businesses (departmental stores, salons, tiffin services, coaching centers, etc.) using a shared infrastructure and reusable domain services.

### Key Features

✅ **Plug-and-Play Architecture** - Add new website types via configuration, not code
✅ **Multi-Tenant by Design** - Complete data isolation between organizations
✅ **Event-Driven** - Ready for orchestration layer (Temporal/Camunda/n8n)
✅ **Highly Scalable** - Services independently scalable, cached at multiple layers
✅ **AI-Powered** - Integrated LLM Gateway for content generation and chatbots
✅ **Modular Core Services** - Reuse existing Auth, User, Billing, Notification services

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                       │
│  Next.js 14+ Multi-Tenant App (SSR + Dynamic Routes)  │
│  • Public Sites  • Admin Panel  • Owner Dashboard     │
└────────────────────┬────────────────────────────────────┘
                     │
                     │ REST APIs
                     ▼
┌────────────────────────────────────────────────────────┐
│                 Domain Services Layer                  │
│  • Site Service (8010)      • Lead Service (8013)     │
│  • Storefront Service (8011) • Content Service (8014) │
│  • Booking Service (8012)    • Widget Service (8015)  │
└────────────────────┬───────────────────────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
         ▼           ▼           ▼
┌──────────────┐  ┌──────────────┐  ┌─────────────┐
│ Core Services│  │  Event Bus   │  │ PostgreSQL  │
│ (Existing)   │  │ Redis/RabbitMQ│  │  Per Service│
│ 8000-8005    │  └──────────────┘  └─────────────┘
└──────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────┐
│          Orchestration Layer (Future)                  │
│  Temporal / Camunda / n8n - Workflow Engine           │
└────────────────────────────────────────────────────────┘
```

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed design documentation.

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for frontend)
- Python 3.11+ (for domain services)
- PostgreSQL 15+
- Redis 7+

### Local Development Setup

1. **Clone and setup environment**

```bash
git clone <repository-url>
cd beautifulwebsites

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
```

2. **Start infrastructure and domain services**

```bash
# Start all domain services + PostgreSQL + Redis
docker-compose up -d

# Check service health
docker-compose ps
curl http://localhost:8010/health  # Site Service
curl http://localhost:8011/health  # Storefront Service
curl http://localhost:8012/health  # Booking Service
```

3. **Initialize databases**

```bash
# Run migrations for all services
./scripts/migrate-all.sh
```

4. **Start frontend**

```bash
cd apps/web
npm install
npm run dev

# Frontend available at http://localhost:3000
```

5. **Verify setup**

```bash
# Create test site
curl -X POST http://localhost:8010/v1/sites \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "test-store",
    "site_type": "departmental_store",
    "template_id": "<template_id>"
  }'

# Visit http://localhost:3000/test-store
```

## 📦 Project Structure

```
beautifulwebsites/
├── apps/
│   └── web/                    # Next.js multi-tenant frontend
│       ├── app/
│       │   ├── (public)/[slug]/   # Dynamic site routes
│       │   └── (admin)/           # Admin panel
│       ├── components/
│       │   └── sections/          # Reusable site sections
│       └── lib/
│           ├── api/               # API clients
│           └── theme/             # Theme engine
│
├── domain-services/            # Domain microservices
│   ├── site-service/          # Site configs & templates (8010)
│   ├── storefront-service/    # Products, orders, cart (8011)
│   ├── booking-service/       # Appointments & scheduling (8012)
│   ├── lead-service/          # Inquiries & leads (8013)
│   ├── content-service/       # Pages, blog, FAQs (8014)
│   ├── widget-service/        # Calculators, forms, widgets (8015)
│   └── shared/                # Shared libraries
│       ├── events/            # Event publisher/consumer
│       └── integrations/      # Core services clients
│
├── infrastructure/
│   ├── docker/               # Dockerfiles
│   ├── k8s/                  # Kubernetes manifests
│   └── postgres/             # DB initialization scripts
│
├── docs/
│   ├── ARCHITECTURE.md       # Detailed architecture
│   ├── API.md               # API specifications
│   └── DEPLOYMENT.md        # Deployment guide
│
├── docker-compose.yml       # Local dev environment
└── README.md               # This file
```

## 🛠️ Core Technologies

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14 (App Router) | SSR, dynamic routing, SEO |
| **Domain Services** | FastAPI (Python) | High-performance async APIs |
| **Database** | PostgreSQL 15 | Per-service databases, JSONB support |
| **Cache** | Redis 7 | Caching + event streaming |
| **Event Bus** | Redis Streams → RabbitMQ | Async communication |
| **Orchestration** | Temporal (planned) | Workflow engine |
| **Monitoring** | Prometheus + Grafana | Metrics & dashboards |
| **Logging** | Grafana Loki | Centralized logs |

## 🎨 Creating a New Website Type

Example: Adding "Yoga Studio" website type

### Step 1: Define Site Type Config

```typescript
// apps/web/lib/site-types.ts
export const SITE_TYPE_CONFIG = {
  yoga_studio: {
    features: ['services', 'instructors', 'bookings', 'blog'],
    default_sections: ['hero', 'class_schedule', 'instructor_profiles', 'testimonials', 'lead_form'],
    required_services: ['booking-service', 'content-service'],
  }
}
```

### Step 2: Create Template

```bash
# Use Site Service API or admin panel
curl -X POST http://localhost:8010/v1/templates \
  -H "Authorization: Bearer <token>" \
  -d '{
    "template_name": "zen_yoga",
    "site_type": "yoga_studio",
    "layout_config": { ... },
    "style_config": { ... }
  }'
```

### Step 3: Add Custom Sections (if needed)

```tsx
// apps/web/components/sections/ClassScheduleSection.tsx
export function ClassScheduleSection({ columns = 3 }: Props) {
  // Reuse Booking Service APIs
  const classes = useBookings(siteId)

  return (
    <section>
      {/* Render class schedule */}
    </section>
  )
}
```

### Step 4: Test

```bash
# Create site
curl -X POST http://localhost:8010/v1/sites \
  -d '{"slug": "zen-yoga", "site_type": "yoga_studio", ...}'

# Visit http://localhost:3000/zen-yoga
```

**Effort:** ~4-8 hours (vs 2-4 weeks building from scratch)

## 📊 Domain Services Overview

### Site Service (8010)
**Purpose:** Manage site definitions, templates, sections, themes

**Key Endpoints:**
- `POST /v1/sites` - Create new site
- `GET /v1/sites/{slug}` - Get site by slug
- `POST /v1/sites/{id}/sections` - Add section to page
- `GET /v1/templates` - List templates

---

### Storefront Service (8011)
**Purpose:** Products, categories, cart, orders

**Key Endpoints:**
- `POST /v1/sites/{id}/products` - Add product
- `GET /v1/sites/{id}/products` - List products
- `POST /v1/sites/{id}/carts` - Create cart
- `POST /v1/sites/{id}/orders` - Place order

---

### Booking Service (8012)
**Purpose:** Appointments, services, staff, availability

**Key Endpoints:**
- `POST /v1/sites/{id}/services` - Add bookable service
- `GET /v1/sites/{id}/availability` - Check available slots
- `POST /v1/sites/{id}/bookings` - Create booking
- `PATCH /v1/sites/{id}/bookings/{id}/status` - Confirm/cancel

---

### Lead Service (8013)
**Purpose:** Capture and manage inquiries

**Key Endpoints:**
- `POST /v1/sites/{id}/leads` - Submit inquiry (public)
- `GET /v1/sites/{id}/leads` - List leads (authenticated)
- `PATCH /v1/sites/{id}/leads/{id}/status` - Update status

---

### Content Service (8014)
**Purpose:** Pages, blog, FAQs, testimonials, media

**Key Endpoints:**
- `POST /v1/sites/{id}/pages` - Create page
- `GET /v1/sites/{id}/blog/posts` - List blog posts
- `POST /v1/sites/{id}/faqs` - Add FAQ
- `POST /v1/sites/{id}/media` - Upload media

---

### Widget Service (8015)
**Purpose:** Calculators, forms, chatbots, WhatsApp buttons

**Key Endpoints:**
- `POST /v1/sites/{id}/widgets` - Create widget
- `POST /v1/widgets/{id}/submit` - Submit widget data (public)

## 🔌 Integrating with Core Services

All domain services use the shared `CoreServicesClient` library:

```python
from shared.integrations.core_services import (
    BillingServiceClient,
    LLMGatewayClient,
    NotificationServiceClient
)

# Check if org can create more sites
quota = await BillingServiceClient.check_quota(org_id, "sites")
if quota['current'] >= quota['limit']:
    raise HTTPException(status_code=403, detail="Site limit reached")

# Generate product description with AI
description = await LLMGatewayClient.execute_prompt(
    prompt_id="product_description",
    inputs={"product_name": "Tata Salt 1kg"}
)

# Send notification
await NotificationServiceClient.send_notification(
    template="order_confirmation",
    recipient=customer_phone,
    channel="whatsapp",
    data={"order_id": order_id, "total": total}
)
```

## 📡 Event-Driven Communication

All domain services publish events for state changes:

```python
from shared.events.publisher import publish_event

# Publish event
await publish_event(
    event_type="order.placed",
    data={
        "order_id": str(order.order_id),
        "site_id": str(order.site_id),
        "total": float(order.total),
        "customer": { ... }
    },
    topic="order-events",
    subject=str(order.order_id)
)
```

Services can subscribe to events:

```python
from shared.events.publisher import EventConsumer

async def handle_order_placed(event: dict):
    # React to order placement
    pass

consumer = EventConsumer(
    topic="order-events",
    consumer_group="notification-consumer",
    handler_func=handle_order_placed
)

await consumer.start()
```

## 🧪 Testing

```bash
# Run unit tests for all services
./scripts/test-all.sh

# Run specific service tests
cd domain-services/site-service
pytest

# Run integration tests
./scripts/test-integration.sh

# Run E2E tests (frontend)
cd apps/web
npm run test:e2e
```

## 🚢 Deployment

### Docker

```bash
# Build all services
docker-compose build

# Push to registry
./scripts/push-images.sh
```

### Kubernetes

```bash
# Deploy to staging
kubectl apply -f infrastructure/k8s/staging/

# Deploy to production
kubectl apply -f infrastructure/k8s/production/
```

See [DEPLOYMENT.md](./docs/DEPLOYMENT.md) for detailed deployment guide.

## 📈 Monitoring

- **Metrics:** Prometheus scrapes `/metrics` endpoint from each service
- **Dashboards:** Grafana dashboards in `infrastructure/grafana/`
- **Alerts:** PagerDuty integration for critical alerts
- **Logs:** Centralized in Grafana Loki
- **Tracing:** OpenTelemetry → Jaeger

## 🔒 Security

- **Authentication:** JWT tokens from Auth Service
- **Authorization:** Role-based access control (RBAC) from User Service
- **Multi-Tenancy:** Row-level security (RLS) in PostgreSQL
- **Secrets:** Managed via environment variables / Kubernetes Secrets
- **HTTPS:** Enforced via Cloudflare / Load Balancer

## 🗺️ Roadmap

### Phase 1: MVP (Weeks 1-4) ✅
- [x] Architecture design
- [ ] Core domain services (Site, Storefront, Booking)
- [ ] Basic Next.js frontend
- [ ] 1 website type (Departmental Store)

### Phase 2: Expand (Weeks 5-8)
- [ ] All domain services implemented
- [ ] 3 more website types (Tiffin, Salon, Coaching)
- [ ] Admin panel with site editor
- [ ] LLM integration for content generation

### Phase 3: Orchestration (Weeks 9-12)
- [ ] Event infrastructure (RabbitMQ)
- [ ] Temporal workflows
- [ ] Order confirmation flow
- [ ] Booking reminders flow

### Phase 4: Scale (Weeks 13-16)
- [ ] Performance optimization
- [ ] Production deployment
- [ ] Monitoring & alerting
- [ ] Load testing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

Copyright © 2025. All rights reserved.

## 📞 Support

- **Documentation:** `/docs`
- **API Docs:** Each service exposes `/docs` (Swagger UI)
- **Issues:** GitHub Issues
- **Slack:** #beautiful-websites-dev

---

**Built with ❤️ by the Beautiful Websites Team**
