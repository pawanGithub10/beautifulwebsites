# Architecture Diagram Guide

## How to Use the Draw.io Diagram

### Opening the Diagram

1. **Online (Recommended)**
   - Go to https://app.diagrams.net/
   - Click "Open Existing Diagram"
   - Select `docs/architecture-diagram.drawio`
   - The diagram will open with full interactivity

2. **VS Code**
   - Install the "Draw.io Integration" extension
   - Open `docs/architecture-diagram.drawio`
   - Edit directly in VS Code

3. **Desktop App**
   - Download draw.io desktop app from https://github.com/jgraph/drawio-desktop/releases
   - Open the file

### Diagram Features

- **Color Coding**
  - 🔵 Blue (Client Layer): Frontend applications
  - 🟡 Yellow (API Gateway): Entry points and routing
  - 🟢 Green (Core Services): Authentication, user, billing, notification
  - 🔴 Red (Domain Services): Site-specific business logic
  - 🟣 Purple (Infrastructure): Databases, caches, queues
  - ⚪ Gray (External): Third-party integrations

- **Connection Types**
  - Solid line → HTTP/REST API calls
  - Thick solid line → Database connections
  - Dashed line → External API calls
  - Dotted line → Event/message queue

- **Interactive Elements**
  - Click on services to view details
  - Hover for tooltips
  - Zoom in/out for different views

### Exporting

From draw.io, you can export to:
- **PNG**: High-resolution image
- **SVG**: Vector graphic for documentation
- **PDF**: For presentations
- **HTML**: Interactive web page

**Export Steps:**
1. File → Export as → [Choose format]
2. Select quality/size settings
3. Download

## Text-Based Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CLIENT LAYER                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                    │
│  │   Web    │  │   iOS    │  │ Android  │  │  Admin   │                    │
│  │ Next.js  │  │   RN     │  │    RN    │  │  React   │                    │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘                    │
└───────┼─────────────┼─────────────┼─────────────┼────────────────────────────┘
        │             │             │             │
        └─────────────┴─────────────┴─────────────┘
                      │
┌─────────────────────┼─────────────────────────────────────────────────────────┐
│                     ▼      API GATEWAY LAYER                                  │
│           ┌──────────────────┐      ┌──────────────────┐                     │
│           │   API Gateway    │      │  Load Balancer   │                     │
│           │  Kong / NGINX    │      │  K8s Ingress     │                     │
│           │   Port 80/443    │      │                  │                     │
│           └────────┬─────────┘      └────────┬─────────┘                     │
└────────────────────┼─────────────────────────┼────────────────────────────────┘
                     │                         │
        ┌────────────┴──────────┬──────────────┴──────────────┬──────────┐
        │                       │                              │          │
┌───────▼─────────────────────────────────────┐  ┌────────────▼──────────────────────────┐
│       CORE SERVICES (8000-8003)             │  │   DOMAIN SERVICES (8010-8020)         │
│                                             │  │                                        │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐    │  │  ┌──────┐  ┌──────┐  ┌──────┐         │
│  │  Auth   │  │  User   │  │ Billing │    │  │  │ Site │  │Store │  │ Book │         │
│  │  :8000  │  │  :8001  │  │  :8002  │    │  │  │:8010 │  │:8011 │  │:8012 │         │
│  │         │  │         │  │         │    │  │  │      │  │      │  │      │         │
│  │• JWT    │  │• Profile│  │• Stripe │    │  │  │Multi │  │Prod  │  │Appts │         │
│  │• 2FA    │  │• Address│  │• Invoice│    │  │  │tenant│  │Cart  │  │Staff │         │
│  │• OAuth  │  │• Verify │  │• Subscrp│    │  │  │Theme │  │Order │  │Cal   │         │
│  │• RBAC   │  │• Device │  │         │    │  │  └──┬───┘  └──┬───┘  └──┬───┘         │
│  └────┬────┘  └────┬────┘  └────┬────┘    │  │     │         │         │             │
│       │            │            │          │  │  ┌──▼───┐  ┌──▼───┐  ┌──▼───┐         │
│  ┌────▼─────────────────────────┐          │  │  │Hotel │  │Content│ │Lead │         │
│  │    Notification :8003         │          │  │  │:8017 │  │:8013 │  │:8014│         │
│  │                               │          │  │  │      │  │      │  │     │         │
│  │ • Email (SMTP)                │          │  │  │Rooms │  │Pages │  │Forms│         │
│  │ • SMS (Twilio)                │          │  │  │Reserv│  │Media │  │CRM  │         │
│  │ • Push (Firebase)             │          │  │  │House │  │SEO   │  │     │         │
│  │ • In-App                      │          │  │  └──────┘  └──────┘  └─────┘         │
│  └───────────────────────────────┘          │  │                                        │
└─────────────┬───────────────────────────────┘  └────────────┬───────────────────────────┘
              │                                               │
              │                                               │
┌─────────────┴───────────────────────────────────────────────┴─────────────────────────────┐
│                        INFRASTRUCTURE & DATA LAYER                                        │
│                                                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│  │ PostgreSQL  │  │ PostgreSQL  │  │  Redis  │  │   AWS   │  │Elastic  │              │
│  │  (Core)     │  │ (Domain)    │  │         │  │   S3    │  │ Search  │              │
│  │             │  │             │  │         │  │         │  │         │              │
│  │• auth_db    │  │• site_db    │  │• Cache  │  │• Avatar │  │• Search │              │
│  │• user_db    │  │• store_db   │  │• Session│  │• Media  │  │• Logs   │              │
│  │• billing_db │  │• booking_db │  │• Rate   │  │• Docs   │  │• Analyt │              │
│  │• notif_db   │  │• hotel_db   │  │  Limit  │  │         │  │         │              │
│  └─────────────┘  └─────────────┘  └─────────┘  └─────────┘  └─────────┘              │
│                                                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                    │
│  │  Temporal   │  │    Kafka    │  │ Kubernetes  │  │ Prometheus  │                    │
│  │             │  │             │  │             │  │  Grafana    │                    │
│  │• Workflows  │  │• Events     │  │• K8s HPA    │  │• Monitoring │                    │
│  │• Saga       │  │• Streaming  │  │• Deploy     │  │• Metrics    │                    │
│  │• Schedule   │  │• Queue      │  │• Scale      │  │• Alerts     │                    │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘                    │
└───────────────────────────────────────┬───────────────────────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼───────────────────────────────────────────────────┐
│                        EXTERNAL SERVICES & INTEGRATIONS                                   │
│                                                                                           │
│  ┌────────┐  ┌────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │ Stripe │  │ Twilio │  │SendGrid │  │Firebase │  │ Google  │  │Facebook │            │
│  │Payment │  │  SMS   │  │  Email  │  │  Push   │  │  OAuth  │  │  OAuth  │            │
│  └────────┘  └────────┘  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

## Service Dependency Map

```
Auth Service (8000)
├── Depends on: PostgreSQL (auth_db), Redis
├── Used by: All services for authentication
└── Integrates: Google OAuth, Facebook OAuth

User Service (8001)
├── Depends on: PostgreSQL (user_db), Redis, AWS S3
├── Calls: Auth Service (for validation)
└── Integrates: AWS S3 (image storage)

Billing Service (8002)
├── Depends on: PostgreSQL (billing_db)
├── Calls: User Service, Notification Service
└── Integrates: Stripe (payments)

Notification Service (8003)
├── Depends on: PostgreSQL (notif_db), Redis
├── Called by: All services
└── Integrates: Twilio (SMS), SendGrid (email), Firebase (push)

Site Service (8010)
├── Depends on: PostgreSQL (site_db), Redis
├── Calls: Auth Service, User Service
└── Used by: All domain services

Storefront Service (8011)
├── Depends on: PostgreSQL (store_db), Elasticsearch
├── Calls: Site Service, Billing Service, Notification Service
└── Integrates: Temporal (order workflows)

Booking Service (8012)
├── Depends on: PostgreSQL (booking_db)
├── Calls: Site Service, Billing Service, Notification Service
└── Integrates: Temporal (booking workflows)

Hotel Service (8017)
├── Depends on: PostgreSQL (hotel_db)
├── Calls: Site Service, Billing Service, Notification Service
└── Integrates: Temporal (reservation workflows)

Content Service (8013)
├── Depends on: PostgreSQL (content_db), Elasticsearch, S3
└── Calls: Site Service

Lead Service (8014)
├── Depends on: PostgreSQL (lead_db)
└── Calls: Site Service, Notification Service

Widget Service (8015)
├── Depends on: PostgreSQL (widget_db)
└── Calls: Site Service
```

## Key Integration Patterns

### Pattern 1: API Gateway Authentication Flow
```
1. Client → API Gateway (with JWT in header)
2. API Gateway → Auth Service (validate token)
3. Auth Service → Response (user info + permissions)
4. API Gateway → Target Service (with validated user context)
5. Target Service → Response
6. API Gateway → Client (response)
```

### Pattern 2: Event-Driven Notification
```
1. Service A → Kafka (publish event: user.created)
2. Kafka → Notification Service (consume event)
3. Notification Service → External Provider (Twilio/SendGrid/Firebase)
4. External Provider → User (deliver notification)
5. External Provider → Notification Service (webhook: delivery status)
6. Notification Service → PostgreSQL (update delivery status)
```

### Pattern 3: Distributed Transaction (Saga)
```
1. Storefront Service → Temporal (start order workflow)
2. Temporal → Billing Service (charge payment)
   ├─ Success → Continue
   └─ Failure → Compensate (cancel order)
3. Temporal → Inventory Service (reserve stock)
   ├─ Success → Continue
   └─ Failure → Compensate (refund payment)
4. Temporal → Notification Service (send confirmation)
5. Temporal → Complete workflow
```

## Quick Reference

### Service URLs (Development)

```bash
# Core Services
http://localhost:8000  # Auth Service
http://localhost:8001  # User Service
http://localhost:8002  # Billing Service
http://localhost:8003  # Notification Service

# Domain Services
http://localhost:8010  # Site Service
http://localhost:8011  # Storefront Service
http://localhost:8012  # Booking Service
http://localhost:8013  # Content Service
http://localhost:8014  # Lead Service
http://localhost:8015  # Widget Service
http://localhost:8017  # Hotel Service

# Infrastructure
http://localhost:5432  # PostgreSQL
http://localhost:6379  # Redis
http://localhost:9200  # Elasticsearch
http://localhost:9092  # Kafka
http://localhost:7233  # Temporal
http://localhost:9090  # Prometheus
http://localhost:3000  # Grafana
```

### API Documentation

Each service has its own API documentation:

```bash
# Auth Service
http://localhost:8000/docs

# User Service
http://localhost:8001/docs

# Billing Service
http://localhost:8002/docs

# Notification Service
http://localhost:8003/docs

# ... and so on
```

### Health Checks

```bash
# Check all services
curl http://localhost:8000/health  # Auth
curl http://localhost:8001/health  # User
curl http://localhost:8002/health  # Billing
curl http://localhost:8003/health  # Notification
```

## Common Scenarios

### Scenario 1: Adding a New Service

1. **Create Service**
   - Choose port number (follow pattern: 8xxx)
   - Create Dockerfile
   - Define database schema
   - Implement API endpoints

2. **Update Infrastructure**
   - Add to docker-compose.yml
   - Create Kubernetes deployment
   - Configure service discovery
   - Add health checks

3. **Update Documentation**
   - Add to architecture diagram
   - Update ARCHITECTURE.md
   - Add API documentation
   - Update dependency map

4. **Configure Monitoring**
   - Add Prometheus metrics
   - Create Grafana dashboard
   - Set up alerts
   - Configure logging

### Scenario 2: Debugging Service Communication

1. **Check Service Health**
   ```bash
   curl http://service-name:port/health
   ```

2. **View Logs**
   ```bash
   kubectl logs -f deployment/service-name
   ```

3. **Trace Request**
   - Check distributed tracing (Jaeger)
   - Look for trace ID in logs
   - Follow request path through services

4. **Check Network**
   ```bash
   kubectl get svc  # Check service endpoints
   kubectl get pods # Check pod status
   ```

## Best Practices

### 1. Service Communication
- ✅ Use API Gateway for external requests
- ✅ Use service discovery for internal requests
- ✅ Implement circuit breakers
- ✅ Set appropriate timeouts
- ✅ Use idempotency keys

### 2. Data Management
- ✅ Each service owns its database
- ✅ Use events for data synchronization
- ✅ Implement eventual consistency
- ✅ Avoid distributed transactions when possible
- ✅ Use sagas for complex workflows

### 3. Security
- ✅ Validate JWT at API Gateway
- ✅ Propagate user context to services
- ✅ Use TLS for all communications
- ✅ Encrypt sensitive data
- ✅ Implement rate limiting

### 4. Monitoring
- ✅ Log all errors
- ✅ Track key metrics
- ✅ Set up alerts
- ✅ Use distributed tracing
- ✅ Monitor business metrics

## Troubleshooting Guide

### Problem: Service Not Responding

**Steps:**
1. Check if service is running: `kubectl get pods`
2. Check service logs: `kubectl logs service-name`
3. Check health endpoint: `curl http://service:port/health`
4. Check database connectivity
5. Check resource usage (CPU, memory)

### Problem: High Latency

**Steps:**
1. Check Prometheus metrics
2. Look at distributed traces
3. Check database query performance
4. Check cache hit rates
5. Review network latency

### Problem: Authentication Failing

**Steps:**
1. Verify JWT token format
2. Check token expiration
3. Verify Auth Service is healthy
4. Check Redis for session data
5. Review API Gateway logs

## Additional Resources

- **Full Architecture Doc**: `/docs/ARCHITECTURE.md`
- **Draw.io Diagram**: `/docs/architecture-diagram.drawio`
- **Service READMEs**: `/core-services/{service-name}/README.md`
- **API Specs**: Available at each service's `/docs` endpoint

---

**Last Updated**: January 2025
**Version**: 2.0
**Maintained By**: Platform Team
