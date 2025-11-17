# Implementation Guide
## Multi-Website Platform - Step-by-Step Development Guide

This guide walks through the implementation of the multi-website platform architecture, from initial setup to production deployment.

---

## Phase 1: Foundation (Weeks 1-2)

### Week 1: Infrastructure Setup

#### Day 1-2: Monorepo Structure

**Tasks:**
1. Initialize monorepo structure
2. Set up shared configuration
3. Configure TypeScript and build tools

**Commands:**
```bash
# Initialize project
mkdir beautifulwebsites
cd beautifulwebsites
git init

# Create directory structure
mkdir -p apps/web domain-services/{site-service,storefront-service,booking-service,lead-service,content-service,widget-service}/app
mkdir -p domain-services/shared/{events,integrations}
mkdir -p infrastructure/{docker,k8s,postgres}
mkdir -p docs

# Initialize package.json for workspaces
npm init -y

# Install Turborepo (optional but recommended)
npm install -D turbo

# Create turbo.json for build orchestration
cat > turbo.json << 'EOF'
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": [".next/**", "dist/**"]
    },
    "dev": {
      "cache": false
    },
    "lint": {},
    "test": {
      "dependsOn": ["^build"]
    }
  }
}
EOF
```

**Deliverables:**
- ✅ Clean monorepo structure
- ✅ Shared TypeScript config
- ✅ Build system configured

---

#### Day 3-4: Site Service (Port 8010)

**Tasks:**
1. Create FastAPI service skeleton
2. Implement database models
3. Create CRUD endpoints
4. Add event publishing

**Implementation:**

```bash
cd domain-services/site-service

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn sqlalchemy asyncpg pydantic python-dotenv redis aioredis

# Create requirements.txt
pip freeze > requirements.txt
```

**File: `app/models.py`**
```python
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Site(Base):
    __tablename__ = "sites"

    site_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(UUID(as_uuid=True), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    domain = Column(String(255))
    site_type = Column(String(50), nullable=False)
    template_id = Column(UUID(as_uuid=True))
    status = Column(String(20), default='draft')
    meta_title = Column(String(200))
    meta_description = Column(Text)
    favicon_url = Column(String(500))
    logo_url = Column(String(500))
    primary_color = Column(String(7))
    secondary_color = Column(String(7))
    font_family = Column(String(100))
    config = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Template(Base):
    __tablename__ = "templates"

    template_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_name = Column(String(100), nullable=False)
    site_type = Column(String(50), nullable=False)
    layout_config = Column(JSON, nullable=False)
    style_config = Column(JSON)
    preview_url = Column(String(500))
    is_premium = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SiteSection(Base):
    __tablename__ = "site_sections"

    section_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    site_id = Column(UUID(as_uuid=True), nullable=False)
    page_path = Column(String(200), default='/')
    section_type = Column(String(50), nullable=False)
    section_order = Column(Integer, nullable=False)
    section_config = Column(JSON, nullable=False)
    is_visible = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**File: `app/routers/sites.py`**
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.database import get_db
from app.models import Site
from app.schemas import SiteCreate, SiteUpdate, SiteResponse
from app.services.site_service import SiteService
from app.middleware.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    site_data: SiteCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new site"""
    service = SiteService(db)
    site = await service.create_site(site_data, current_user['org_id'])
    return site

@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get site by ID"""
    service = SiteService(db)
    site = await service.get_site(site_id, current_user['org_id'])
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site

@router.get("/", response_model=List[SiteResponse])
async def list_sites(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all sites for current org"""
    service = SiteService(db)
    sites = await service.list_sites(current_user['org_id'])
    return sites

@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: UUID,
    site_data: SiteUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update site"""
    service = SiteService(db)
    site = await service.update_site(site_id, site_data, current_user['org_id'])
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site

@router.get("/by-slug/{slug}", response_model=SiteResponse)
async def get_site_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get site by slug (public endpoint)"""
    service = SiteService(db)
    site = await service.get_site_by_slug(slug)
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return site
```

**File: `Dockerfile`**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Expose port
EXPOSE 8010

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8010"]
```

**Testing:**
```bash
# Start service
uvicorn app.main:app --reload --port 8010

# Test health endpoint
curl http://localhost:8010/health

# Test create site (requires auth token)
curl -X POST http://localhost:8010/v1/sites \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "test-store",
    "site_type": "departmental_store",
    "template_id": "template_uuid"
  }'
```

**Deliverables:**
- ✅ Site Service running on port 8010
- ✅ Database migrations created
- ✅ CRUD endpoints working
- ✅ Event publishing configured

---

#### Day 5: Storefront Service (Port 8011)

**Tasks:**
1. Implement Storefront Service
2. Create product and order models
3. Add cart functionality

**Follow similar pattern as Site Service:**
- Models: Product, Category, Cart, CartItem, Order, OrderItem
- Endpoints: Products CRUD, Cart operations, Order placement
- Events: order.placed, order.confirmed, order.dispatched

**Key Differences:**
- More complex validation (inventory checks, price calculations)
- Integration with Billing Service for quota checks
- Integration with Notification Service for order confirmations

---

### Week 2: Core Domain Services

#### Day 6-7: Booking Service (Port 8012)

**Key Features:**
- Service definitions
- Staff management
- Availability slots (weekly recurring schedule)
- Booking creation with conflict detection

**Complex Logic:**
```python
# app/services/booking_service.py
async def check_availability(
    self,
    service_id: UUID,
    staff_id: UUID,
    date: datetime.date,
    start_time: datetime.time,
    duration_minutes: int
) -> bool:
    """Check if time slot is available"""

    # 1. Get staff availability for day of week
    day_of_week = date.weekday()
    availability = await self.get_staff_availability(staff_id, day_of_week)
    if not availability:
        return False

    # 2. Check if requested time falls within availability window
    if not (availability.start_time <= start_time < availability.end_time):
        return False

    # 3. Check for conflicting bookings
    end_time = (datetime.combine(date, start_time) + timedelta(minutes=duration_minutes)).time()
    conflicts = await self.get_conflicting_bookings(staff_id, date, start_time, end_time)

    return len(conflicts) == 0
```

---

#### Day 8-9: Lead, Content, Widget Services (Ports 8013-8015)

These are simpler CRUD services. Can be implemented in parallel by different team members.

**Lead Service (8013):**
- Lead capture (public endpoint)
- Lead management (authenticated)
- Status tracking

**Content Service (8014):**
- Pages, blog posts, FAQs
- Media library
- LLM integration for content generation

**Widget Service (8015):**
- Widget configuration
- Widget submission handling
- Dynamic widget rendering

---

#### Day 10: Integration & Testing

**Tasks:**
1. Test all services independently
2. Test service-to-service communication via events
3. Load test with mock data
4. Fix bugs and optimize queries

**Integration Tests:**
```python
# tests/test_integration.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_site_and_products():
    """Test creating a site and adding products"""

    async with AsyncClient() as client:
        # 1. Create site
        site_response = await client.post(
            "http://localhost:8010/v1/sites",
            json={
                "slug": "test-store",
                "site_type": "departmental_store",
                "template_id": str(template_id)
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert site_response.status_code == 201
        site_id = site_response.json()["site_id"]

        # 2. Add product
        product_response = await client.post(
            f"http://localhost:8011/v1/sites/{site_id}/products",
            json={
                "name": "Test Product",
                "price": 99.99,
                "stock_quantity": 10
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert product_response.status_code == 201

        # 3. Create cart and add item
        cart_response = await client.post(
            f"http://localhost:8011/v1/sites/{site_id}/carts",
            headers={"Authorization": f"Bearer {token}"}
        )
        cart_id = cart_response.json()["cart_id"]

        # 4. Place order
        order_response = await client.post(
            f"http://localhost:8011/v1/sites/{site_id}/orders",
            json={
                "cart_id": cart_id,
                "customer_name": "Test Customer",
                "customer_phone": "+911234567890",
                "delivery_address": {...},
                "payment_method": "cod"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        assert order_response.status_code == 201

        # 5. Verify event was published
        # Check event bus for order.placed event
```

---

## Phase 2: Frontend (Weeks 3-4)

### Week 3: Next.js Setup

#### Day 11-12: Next.js Project Setup

```bash
cd apps/web

# Create Next.js app
npx create-next-app@latest . --typescript --tailwind --app --import-alias "@/*"

# Install additional dependencies
npm install @tanstack/react-query axios zod clsx tailwind-merge
npm install -D @types/node

# Configure environment variables
cat > .env.local << 'EOF'
NEXT_PUBLIC_SITE_SERVICE_URL=http://localhost:8010
NEXT_PUBLIC_STOREFRONT_SERVICE_URL=http://localhost:8011
NEXT_PUBLIC_BOOKING_SERVICE_URL=http://localhost:8012
NEXT_PUBLIC_LEAD_SERVICE_URL=http://localhost:8013
NEXT_PUBLIC_CONTENT_SERVICE_URL=http://localhost:8014
NEXT_PUBLIC_WIDGET_SERVICE_URL=http://localhost:8015

SITE_SERVICE_URL=http://localhost:8010
PLATFORM_DOMAIN=localhost:3000
EOF
```

**Deliverables:**
- ✅ Next.js 14 with App Router
- ✅ Tailwind CSS configured
- ✅ Environment variables set up

---

#### Day 13-14: Dynamic Routing & Middleware

Files to create:
1. `middleware.ts` (already provided)
2. `app/(public)/[slug]/page.tsx` (already provided)
3. `app/(public)/[slug]/layout.tsx`

```tsx
// app/(public)/[slug]/layout.tsx
import { headers } from 'next/headers'
import { Header } from '@/components/layout/Header'
import { Footer } from '@/components/layout/Footer'

export default function SiteLayout({ children }: { children: React.ReactNode }) {
  const headersList = headers()
  const siteConfigHeader = headersList.get('x-site-config')
  const siteConfig = siteConfigHeader ? JSON.parse(siteConfigHeader) : null

  return (
    <div className="min-h-screen flex flex-col">
      <Header siteConfig={siteConfig} />
      <main className="flex-1">{children}</main>
      <Footer siteConfig={siteConfig} />
    </div>
  )
}
```

---

#### Day 15-16: Section Components

Create 8-10 essential section components:
1. HeroSection (already provided)
2. ProductGridSection
3. ServiceGridSection
4. TestimonialsSection
5. ContactFormSection
6. FAQSection
7. BookingCalendarSection
8. WhatsAppButtonSection

**Example: ProductGridSection**
```tsx
// components/sections/ProductGridSection.tsx
'use client'

import { useQuery } from '@tanstack/react-query'
import { getProducts } from '@/lib/api/storefront-service'
import { ProductCard } from '@/components/ProductCard'

interface ProductGridSectionProps {
  siteId: string
  columns?: number
  category_filter?: string
  show_price?: boolean
  show_add_to_cart?: boolean
}

export function ProductGridSection({
  siteId,
  columns = 3,
  category_filter,
  show_price = true,
  show_add_to_cart = true,
}: ProductGridSectionProps) {
  const { data: products, isLoading } = useQuery({
    queryKey: ['products', siteId, category_filter],
    queryFn: () => getProducts(siteId, { category: category_filter }),
  })

  if (isLoading) {
    return <div>Loading products...</div>
  }

  return (
    <section className="py-16 bg-gray-50">
      <div className="container mx-auto px-4">
        <div className={`grid grid-cols-1 md:grid-cols-${columns} gap-8`}>
          {products?.map((product) => (
            <ProductCard
              key={product.product_id}
              product={product}
              showPrice={show_price}
              showAddToCart={show_add_to_cart}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
```

---

### Week 4: Admin Panel

#### Day 17-19: Site Editor

Create admin routes:
```
apps/web/app/(admin)/
├── dashboard/
│   └── page.tsx
├── site-editor/
│   └── page.tsx
├── products/
│   ├── page.tsx
│   └── [id]/page.tsx
├── orders/
│   ├── page.tsx
│   └── [id]/page.tsx
└── layout.tsx
```

**Site Editor with Drag-and-Drop:**
```bash
npm install @dnd-kit/core @dnd-kit/sortable
```

```tsx
// app/(admin)/site-editor/page.tsx
'use client'

import { DndContext, closestCenter } from '@dnd-kit/core'
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable'
import { SectionPicker } from '@/components/admin/SectionPicker'
import { SectionEditor } from '@/components/admin/SectionEditor'

export default function SiteEditorPage() {
  const [sections, setSections] = useState([])

  const handleDragEnd = (event) => {
    const { active, over } = event
    if (active.id !== over.id) {
      setSections((items) => {
        const oldIndex = items.findIndex((i) => i.id === active.id)
        const newIndex = items.findIndex((i) => i.id === over.id)
        return arrayMove(items, oldIndex, newIndex)
      })
    }
  }

  return (
    <div className="flex h-screen">
      {/* Section library */}
      <aside className="w-64 bg-gray-100 p-4 overflow-y-auto">
        <SectionPicker onAddSection={addSection} />
      </aside>

      {/* Canvas */}
      <main className="flex-1 overflow-y-auto">
        <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
          <SortableContext items={sections} strategy={verticalListSortingStrategy}>
            {sections.map((section) => (
              <SectionEditor key={section.id} section={section} />
            ))}
          </SortableContext>
        </DndContext>
      </main>

      {/* Properties panel */}
      <aside className="w-80 bg-gray-50 p-4 overflow-y-auto">
        {selectedSection && <PropertiesPanel section={selectedSection} />}
      </aside>
    </div>
  )
}
```

---

#### Day 20: Testing & Polish

**E2E Tests:**
```bash
npm install -D @playwright/test

# Create test
# tests/e2e/site-creation.spec.ts
import { test, expect } from '@playwright/test'

test('create and view site', async ({ page }) => {
  // Login
  await page.goto('/admin/login')
  await page.fill('[name=email]', 'test@example.com')
  await page.fill('[name=password]', 'password')
  await page.click('button[type=submit]')

  // Create site
  await page.goto('/admin/sites/new')
  await page.fill('[name=slug]', 'test-store')
  await page.selectOption('[name=site_type]', 'departmental_store')
  await page.click('button[type=submit]')

  // Verify site created
  await expect(page.locator('text=Site created successfully')).toBeVisible()

  // Visit public site
  await page.goto('/test-store')
  await expect(page.locator('h1')).toContainText('Welcome')
})

# Run tests
npx playwright test
```

---

## Phase 3: Orchestration (Weeks 9-12)

### Temporal Setup

```bash
# Start Temporal server (Docker)
docker run -d -p 7233:7233 temporalio/auto-setup:latest

# Install Temporal Python SDK
pip install temporalio

# Create workflow
# orchestration-service/workflows/order_confirmation.py
from temporalio import workflow, activity
from datetime import timedelta

@workflow.defn
class OrderConfirmationWorkflow:
    @workflow.run
    async def run(self, order_id: str) -> str:
        # Send confirmation
        await workflow.execute_activity(
            send_notification,
            args=['order_confirmation', order_id],
            start_to_close_timeout=timedelta(minutes=1)
        )

        # Wait for owner confirmation
        confirmed = await workflow.wait_condition(
            lambda: self.order_confirmed,
            timeout=timedelta(minutes=30)
        )

        if not confirmed:
            # Send reminder
            await workflow.execute_activity(
                send_notification,
                args=['order_reminder', order_id]
            )

        return 'confirmed' if confirmed else 'timeout'
```

---

## Deployment Checklist

### Pre-Production

- [ ] All tests passing (unit, integration, E2E)
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Database migrations tested
- [ ] Rollback procedures documented
- [ ] Monitoring and alerting configured
- [ ] Backup strategy in place

### Production Deployment

```bash
# 1. Build Docker images
./scripts/build-images.sh

# 2. Push to registry
./scripts/push-images.sh

# 3. Apply K8s manifests
kubectl apply -f infrastructure/k8s/production/

# 4. Verify deployment
kubectl rollout status deployment/site-service
kubectl rollout status deployment/storefront-service

# 5. Run smoke tests
./scripts/smoke-test-production.sh
```

---

## Monitoring

### Metrics to Track

**Service Health:**
- Request rate (requests/second)
- Error rate (4xx, 5xx)
- Response time (p50, p95, p99)
- Database connection pool usage

**Business Metrics:**
- Sites created per day
- Orders placed per hour
- Bookings confirmed per hour
- Active sessions

**Infrastructure:**
- CPU usage
- Memory usage
- Disk I/O
- Network bandwidth

### Alerts

Critical alerts (PagerDuty):
- Service down (health check failing)
- Error rate > 5%
- Response time p99 > 5s
- Database connection pool exhausted

---

## Conclusion

This implementation guide provides a concrete, step-by-step plan for building the multi-website platform. Follow the phases sequentially, and use the provided code examples as starting points.

**Key Success Factors:**
1. **Start small, iterate fast** - Build MVP first, add features later
2. **Test continuously** - Write tests alongside code
3. **Document as you go** - Keep docs up to date
4. **Monitor everything** - Can't improve what you don't measure
5. **Ship frequently** - Deploy multiple times per week

Good luck! 🚀
