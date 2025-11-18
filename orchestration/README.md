# Orchestration Layer

Temporal-based workflow orchestration for order processing and booking lifecycle management.

## Overview

This layer provides reliable, durable workflow execution for business processes that span multiple services and require:
- Long-running workflows (hours to days)
- Automatic retries and error handling
- State persistence and recovery
- Manual interventions (signals)
- Complex timing logic

## Architecture

```
┌─────────────┐
│  Temporal   │
│   Server    │
└──────┬──────┘
       │
       ├─────► Order Processing Workflow
       │       - Inventory validation
       │       - Payment processing
       │       - Status updates
       │       - Notifications
       │
       └─────► Booking Lifecycle Workflow
               - Confirmations
               - Reminders
               - Completion tracking
               - Feedback requests
```

## Workflows

### Order Processing Workflow

**Task Queue:** `order-task-queue`

**Lifecycle:**
1. **Placed** → Validate inventory → Process payment
2. **Confirmed** → Send confirmation → Wait for preparation
3. **Preparing** → Wait for dispatch
4. **Dispatched** → Send tracking → Wait for delivery
5. **Delivered** → Send completion notification

**Signals:**
- `cancel_order_signal` - Cancel at any stage
- `mark_preparing_signal` - Start preparation
- `dispatch_signal` - Dispatch with tracking
- `mark_delivered_signal` - Mark as delivered

**Activities:**
- `validate_inventory` - Check stock availability
- `process_payment` - Process payment via gateway
- `confirm_order` - Update status to confirmed
- `mark_preparing` - Update status to preparing
- `dispatch_order` - Update status to dispatched
- `mark_delivered` - Update status to delivered
- `cancel_order` - Cancel and restore inventory
- `send_*_notification` - Send notifications

### Booking Lifecycle Workflow

**Task Queue:** `booking-task-queue`

**Lifecycle:**
1. **Confirmed** → Send confirmation
2. **Reminder** → Send reminder 24h before
3. **Completed** → Mark as completed after appointment
4. **Feedback** → Request customer feedback

**Signals:**
- `cancel_booking_signal` - Cancel booking
- `mark_completed_signal` - Mark as completed
- `mark_no_show_signal` - Mark as no-show

**Activities:**
- `mark_completed` - Update status to completed
- `mark_no_show` - Update status to no-show
- `cancel_booking` - Cancel booking
- `send_*_notification` - Send notifications

## Running the Worker

### Local Development

```bash
# Install dependencies
cd orchestration
pip install -r requirements.txt

# Start Temporal server (via Docker Compose)
docker-compose up temporal temporal-ui

# Run the worker
python workers/worker.py
```

### Docker

```bash
# Build and run with docker-compose
docker-compose up temporal-worker
```

## Triggering Workflows

### From Python

```python
from temporalio.client import Client
from orchestration.workflows.order.order_workflow import OrderProcessingWorkflow

# Connect to Temporal
client = await Client.connect("localhost:7233")

# Start order workflow
result = await client.start_workflow(
    OrderProcessingWorkflow.run,
    {
        "order_id": "ord-123",
        "site_id": "site-456",
        "customer_email": "customer@example.com",
        "total_amount": 1500.00,
        "items": [...]
    },
    id=f"order-workflow-ord-123",
    task_queue="order-task-queue",
)
```

### From HTTP API

```bash
curl -X POST http://localhost:8011/api/v1/{site_id}/orders \
  -H "Content-Type: application/json" \
  -d '{"cart_id": "cart-123", "customer_details": {...}}'

# This will automatically trigger the workflow
```

## Monitoring

### Temporal UI

Access at: http://localhost:8088

- View running workflows
- See workflow history
- Trigger signals manually
- Debug failed executions

### n8n Integration

Access at: http://localhost:5678

- Configure notification workflows
- Set up email/SMS templates
- Add webhook integrations
- Create custom automation

## Environment Variables

```bash
# Temporal connection
TEMPORAL_ADDRESS=localhost:7233

# Service URLs
STOREFRONT_SERVICE_URL=http://localhost:8011
BOOKING_SERVICE_URL=http://localhost:8012
NOTIFICATION_SERVICE_URL=http://localhost:8003

# n8n webhook URL
N8N_WEBHOOK_URL=http://localhost:5678/webhook
```

## Error Handling

### Automatic Retries

All activities have retry policies:
- Initial interval: 1 second
- Maximum interval: 60 seconds
- Backoff coefficient: 2.0
- Maximum attempts: 3

### Compensation

Failed workflows trigger compensation:
- Order failures restore inventory
- Payment failures cancel orders
- Notifications failures are logged but don't fail workflows

### Manual Intervention

For stuck workflows:
1. View in Temporal UI
2. Check activity logs
3. Send signal to continue/cancel
4. Restart if needed

## Development

### Adding New Workflows

1. Create workflow file in `workflows/{domain}/`
2. Define workflow class with `@workflow.defn`
3. Implement `@workflow.run` method
4. Add signals with `@workflow.signal`
5. Register in worker.py

### Adding New Activities

1. Create activity in `activities/{domain}/`
2. Define with `@activity.defn`
3. Implement idempotent logic
4. Add error handling
5. Register in worker.py

### Testing

```bash
# Run tests
pytest tests/

# Test individual workflow
python -m orchestration.workflows.order.order_workflow
```

## Production Deployment

### Scaling Workers

```yaml
# kubernetes/temporal-worker-deployment.yaml
replicas: 3  # Scale horizontally
```

### High Availability

- Run multiple worker instances
- Use Temporal Cloud for managed service
- Set up Temporal server cluster

### Monitoring

- Prometheus metrics
- Grafana dashboards
- Alert on workflow failures
- Track workflow duration

## Architecture Benefits

✓ **Reliability** - Automatic retries and error recovery
✓ **Durability** - State persisted to database
✓ **Scalability** - Horizontal worker scaling
✓ **Visibility** - Complete execution history
✓ **Testability** - Replay and time-travel debugging
✓ **Maintainability** - Clean separation of workflows and activities
