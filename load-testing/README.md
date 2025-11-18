# Load Testing

Comprehensive load testing suite for validating platform performance and auto-scaling behavior.

## Overview

This directory contains load testing scripts using **Locust**, a modern load testing framework that simulates realistic user behavior.

## Setup

```bash
cd load-testing
pip install -r requirements.txt
```

## Running Tests

### Web UI Mode (Recommended)

```bash
# Start Locust web interface
locust -f locustfile.py --host=http://localhost:3000

# Open browser to http://localhost:8089
# Configure:
# - Number of users (e.g., 100)
# - Spawn rate (e.g., 10 users/second)
# - Host: http://localhost:3000

# Click "Start Swarming"
```

### Headless Mode

```bash
# Run without web UI
locust -f locustfile.py \
    --headless \
    --users 100 \
    --spawn-rate 10 \
    --run-time 5m \
    --host=http://localhost:3000
```

## Test Scenarios

### 1. Mixed Traffic (Default)

Simulates realistic user distribution:
- **70%** Storefront users (browsing, adding to cart)
- **30%** Booking users (checking services, availability)

```bash
locust -f locustfile.py --users 100 --spawn-rate 10
```

### 2. Storefront Load Test

Heavy load on e-commerce endpoints:

```bash
locust -f locustfile.py \
    --users 200 \
    --spawn-rate 20 \
    --tags storefront \
    StorefrontOnlyUser
```

**Endpoints Tested:**
- `GET /api/products` - Product listing
- `GET /api/products/{id}` - Product details
- `POST /api/cart` - Create cart
- `POST /api/cart/{id}/items` - Add to cart
- `GET /api/cart/{id}` - View cart

### 3. Booking Load Test

Load test for appointment booking:

```bash
locust -f locustfile.py \
    --users 100 \
    --spawn-rate 10 \
    BookingOnlyUser
```

**Endpoints Tested:**
- `GET /api/services` - Service listing
- `POST /api/availability` - Check availability
- `GET /api/providers` - Provider listing

### 4. Spike Test

Simulates sudden traffic spike:

```bash
locust -f locustfile.py \
    --users 500 \
    --spawn-rate 100 \
    --run-time 2m \
    SpikeUser
```

**Purpose:** Test HPA scale-up behavior

## Testing HPA Autoscaling

### Step 1: Start with Low Load

```bash
# Start with 10 users
locust -f locustfile.py --users 10 --spawn-rate 2

# Watch HPA (in another terminal)
watch kubectl get hpa -n platform
```

### Step 2: Gradually Increase Load

```bash
# Increase to 50 users
# (Use web UI to ramp up)

# Check pod count
kubectl get pods -n platform | grep storefront
```

### Step 3: Spike Load

```bash
# Jump to 200 users
# Watch HPA scale up pods

# Expected: HPA should add pods within 15-30 seconds
```

### Step 4: Reduce Load

```bash
# Drop to 10 users
# Watch HPA scale down (takes 5+ minutes due to stabilization window)
```

## Monitoring During Load Tests

### Locust Dashboard

Access: http://localhost:8089

Metrics shown:
- **RPS** - Requests per second
- **Response times** - P50, P95, P99
- **Failure rate** - % of failed requests
- **Users** - Current number of simulated users

### Kubernetes Metrics

```bash
# Watch HPA decisions
watch kubectl get hpa -n platform

# Monitor pod CPU/Memory
watch kubectl top pods -n platform

# View events
kubectl get events -n platform --watch

# Check pod count over time
watch "kubectl get pods -n platform | grep -c Running"
```

### Service Metrics

```bash
# Storefront service health
curl http://localhost:8011/health

# Check specific endpoint
curl http://localhost:8011/api/v1/demo-site/products | jq
```

## Load Test Scenarios

### Scenario 1: Normal Traffic

**Goal:** Establish baseline performance

```bash
locust -f locustfile.py \
    --users 50 \
    --spawn-rate 5 \
    --run-time 10m \
    --host=http://localhost:3000
```

**Expected:**
- 2 pods (min replicas)
- 30-50% CPU utilization
- Response time < 200ms

### Scenario 2: Peak Traffic

**Goal:** Test scale-up

```bash
locust -f locustfile.py \
    --users 200 \
    --spawn-rate 20 \
    --run-time 15m
```

**Expected:**
- Scale to 4-6 pods
- 60-70% CPU utilization
- Response time < 500ms
- No failures

### Scenario 3: Traffic Spike

**Goal:** Test rapid scale-up

```bash
locust -f locustfile.py \
    --users 500 \
    --spawn-rate 100 \
    --run-time 5m \
    SpikeUser
```

**Expected:**
- Scale to 8-10 pods within 1 minute
- Some latency spike initially (< 2s)
- Recovery to normal latency within 2 minutes
- < 1% error rate

### Scenario 4: Sustained Load

**Goal:** Test stability under sustained high load

```bash
locust -f locustfile.py \
    --users 300 \
    --spawn-rate 10 \
    --run-time 30m
```

**Expected:**
- Stable pod count (6-8 pods)
- Consistent response times
- No memory leaks
- No error accumulation

## Performance Targets

### Response Time (P95)

| Endpoint | Target | Max Acceptable |
|----------|--------|---------------|
| Product Listing | < 200ms | 500ms |
| Product Detail | < 150ms | 400ms |
| Add to Cart | < 100ms | 300ms |
| Checkout | < 500ms | 1000ms |
| Service Listing | < 200ms | 500ms |
| Check Availability | < 300ms | 800ms |

### Throughput

| Service | Target RPS | Max RPS |
|---------|-----------|---------|
| Storefront | 1000 | 5000 |
| Booking | 500 | 2000 |
| Frontend | 2000 | 10000 |

### Error Rate

- **Target:** < 0.1%
- **Max Acceptable:** 1%
- **During Spike:** < 5% (temporary)

## Results Analysis

### Good Results

✓ Response times within targets
✓ Error rate < 1%
✓ HPA scaled appropriately
✓ No pod crashes
✓ Stable performance under sustained load

### Warning Signs

⚠ Response time P95 > 500ms
⚠ Error rate 1-5%
⚠ HPA at max replicas
⚠ Pods restarting
⚠ Memory growing over time

### Critical Issues

❌ Response time > 1s
❌ Error rate > 5%
❌ Pod crashes
❌ Out of memory errors
❌ Database connection pool exhausted

## Troubleshooting

### High Response Times

```bash
# Check if CPU bound
kubectl top pods -n platform

# If CPU > 80%, increase HPA max replicas or resource limits
kubectl edit hpa storefront-service-hpa -n platform

# Check database
# Look for slow queries, connection pool exhaustion
```

### High Error Rate

```bash
# Check pod logs
kubectl logs -n platform deployment/storefront-service --tail=100

# Common causes:
# - Database connection timeout
# - Out of memory
# - Dependency service down
# - Rate limiting
```

### HPA Not Scaling

```bash
# Check metrics are available
kubectl top pods -n platform

# Check HPA status
kubectl describe hpa storefront-service-hpa -n platform

# Verify resource requests are set
kubectl get deployment storefront-service -n platform -o yaml | grep -A 5 resources
```

## CI/CD Integration

### Run in Pipeline

```yaml
# .github/workflows/load-test.yml
name: Load Test
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: pip install -r load-testing/requirements.txt
      - name: Run load test
        run: |
          locust -f load-testing/locustfile.py \
            --headless \
            --users 100 \
            --spawn-rate 10 \
            --run-time 5m \
            --host=${{ secrets.STAGING_URL }} \
            --html=report.html
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: load-test-report
          path: report.html
```

## Best Practices

✓ **Start small** - Begin with low user count
✓ **Ramp gradually** - Increase load incrementally
✓ **Monitor continuously** - Watch metrics during tests
✓ **Test regularly** - Run load tests on schedule
✓ **Document results** - Keep performance history
✓ **Test realistic scenarios** - Match production patterns
✓ **Include think time** - Simulate real user delays

## Advanced Scenarios

### Testing with Real Data

```python
# Load test with actual product IDs from database
import requests

def get_product_ids():
    response = requests.get("http://localhost:8011/api/v1/demo-site/products")
    return [p["product_id"] for p in response.json()["items"]]

PRODUCT_IDS = get_product_ids()

class RealDataUser(HttpUser):
    @task
    def view_real_product(self):
        product_id = random.choice(PRODUCT_IDS)
        self.client.get(f"/api/v1/demo-site/products/{product_id}")
```

### Custom Metrics

```python
from locust import events

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, **kwargs):
    if response_time > 1000:
        print(f"SLOW REQUEST: {name} took {response_time}ms")
```

## References

- [Locust Documentation](https://docs.locust.io/)
- [Load Testing Best Practices](https://locust.io/documentation.html)
- [Kubernetes HPA](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
