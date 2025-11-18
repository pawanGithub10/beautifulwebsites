# Kubernetes Horizontal Pod Autoscaling (HPA)

Automatic scaling configuration for all platform services based on CPU, memory, and custom metrics.

## Overview

The platform uses Kubernetes HPA v2 to automatically scale services based on:
- **CPU utilization** - Target 60-70%
- **Memory utilization** - Target 75-80%
- **Custom metrics** - Request rate, queue depth, etc.

## HPA Configurations

### Frontend Service
- **Min Replicas:** 3
- **Max Replicas:** 20
- **CPU Target:** 60%
- **Memory Target:** 75%
- **Scale Up:** Fast (can add 5 pods at once or 100% in 15s)
- **Scale Down:** Conservative (max 50% or 3 pods per minute)

### Storefront Service
- **Min Replicas:** 2
- **Max Replicas:** 10
- **CPU Target:** 70%
- **Memory Target:** 80%
- **Custom Metric:** http_requests_per_second (target: 1000)
- **Scale Up:** Can double pods or add 4 pods in 15s
- **Scale Down:** Max 50% or 2 pods per minute

### Booking Service
- **Min Replicas:** 2
- **Max Replicas:** 8
- **CPU Target:** 70%
- **Memory Target:** 80%
- **Scale Up:** Can double pods or add 3 pods in 15s
- **Scale Down:** Max 50% per minute

## Deployment

### Apply HPA Configurations

```bash
# Apply all HPAs
kubectl apply -f kubernetes/autoscaling/

# Apply specific HPA
kubectl apply -f kubernetes/autoscaling/hpa-frontend.yaml

# Verify HPAs
kubectl get hpa -n platform

# Watch HPAs in real-time
kubectl get hpa -n platform --watch
```

### View HPA Status

```bash
# Get detailed HPA status
kubectl describe hpa frontend-hpa -n platform

# Check current metrics
kubectl top pods -n platform

# Check node resources
kubectl top nodes
```

## Scaling Behavior

### Scale Up Policy

HPAs are configured for **fast scale-up** to handle traffic spikes:

```yaml
scaleUp:
  stabilizationWindowSeconds: 0  # No delay
  policies:
  - type: Percent
    value: 100  # Can double pods
    periodSeconds: 15
  - type: Pods
    value: 4  # Or add fixed number
    periodSeconds: 15
  selectPolicy: Max  # Choose most aggressive
```

### Scale Down Policy

HPAs use **conservative scale-down** to avoid flapping:

```yaml
scaleDown:
  stabilizationWindowSeconds: 300  # Wait 5 minutes
  policies:
  - type: Percent
    value: 50  # Max 50% reduction
    periodSeconds: 60
  - type: Pods
    value: 2  # Or fixed number
    periodSeconds: 60
  selectPolicy: Min  # Choose most conservative
```

## Metrics

### Resource Metrics

Built-in metrics from Metrics Server:
- **CPU** - `kubectl top pods`
- **Memory** - `kubectl top pods`

### Custom Metrics

Requires Prometheus Adapter or similar:
- `http_requests_per_second` - Request rate
- `queue_depth` - Message queue length
- `database_connections` - Active DB connections

### Installing Metrics Server

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

## Load Testing

Test autoscaling with load:

```bash
# Run load test (see ../load-testing/)
cd load-testing
python load_test.py --target storefront --duration 300 --rps 1000

# Watch HPA scale
watch kubectl get hpa -n platform
```

## Monitoring

### Grafana Dashboards

Key metrics to monitor:
- Current replica count vs desired
- CPU/Memory utilization per pod
- Scale up/down events
- Request latency during scaling

### Alerts

Set up alerts for:
- HPA at max replicas (need to increase limit)
- Frequent scaling events (tune thresholds)
- Failed scale operations

## Tuning Guidelines

### CPU/Memory Targets

- **Too Low (< 50%)** - Overprovisioning, wasted resources
- **Optimal (60-80%)** - Good utilization, room for spikes
- **Too High (> 90%)** - Risk of saturation, slow responses

### Min/Max Replicas

- **Min Replicas** - Enough for baseline traffic + 1 failure
- **Max Replicas** - Based on peak traffic + 50% buffer
- **Ratio** - Max should be 3-10x min for effective scaling

### Stabilization Windows

- **Scale Up** - 0 seconds (immediate response to load)
- **Scale Down** - 300+ seconds (avoid flapping)

## Cluster Autoscaler

For automatic node scaling:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: cluster-autoscaler
  namespace: kube-system
data:
  min-nodes: "3"
  max-nodes: "20"
  scale-down-delay: "10m"
```

## Cost Optimization

### Strategies

1. **Right-size min replicas** - Don't overprovision baseline
2. **Use spot instances** - For non-critical workloads
3. **Schedule scale-down** - Reduce during off-peak hours
4. **Monitor waste** - Check for pods at < 30% utilization

### Scheduled Scaling

Scale based on time of day:

```yaml
# Using external tool like Keda or CronHPA
apiVersion: autoscaling.keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: storefront-scheduled
spec:
  scaleTargetRef:
    name: storefront-service
  triggers:
  - type: cron
    metadata:
      timezone: Asia/Kolkata
      start: 0 9 * * *   # Scale up at 9 AM
      end: 0 21 * * *     # Scale down at 9 PM
      desiredReplicas: "10"
```

## Troubleshooting

### HPA Not Scaling

```bash
# Check if metrics are available
kubectl get --raw /apis/metrics.k8s.io/v1beta1/pods

# Check HPA conditions
kubectl describe hpa <name> -n platform

# Common issues:
# 1. Metrics Server not installed
# 2. Resource requests not set on pods
# 3. Metrics API unavailable
```

### Unexpected Scaling

```bash
# Check recent events
kubectl get events -n platform --sort-by='.lastTimestamp'

# Review HPA decision making
kubectl describe hpa <name> -n platform | grep -A 10 Conditions

# Common causes:
# 1. Traffic spike (expected)
# 2. Memory leak (fix application)
# 3. Incorrect target thresholds (tune HPA)
```

### Resource Limits

Ensure pods have resource requests/limits:

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

## Best Practices

✓ **Set resource requests** - HPA needs them for calculations
✓ **Start conservative** - Easier to tune down than up
✓ **Monitor before tuning** - Collect data for 1-2 weeks
✓ **Test scaling** - Use load tests to verify behavior
✓ **Document decisions** - Record why thresholds were chosen
✓ **Review regularly** - Revisit settings quarterly

## Production Checklist

- [ ] Metrics Server installed and working
- [ ] Resource requests set on all deployments
- [ ] HPA configurations applied
- [ ] Load testing validated scaling behavior
- [ ] Monitoring dashboards created
- [ ] Alerts configured for scaling issues
- [ ] Runbook documented for scaling problems
- [ ] Team trained on HPA operations

## References

- [Kubernetes HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [HPA Walkthrough](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/)
- [Metrics Server](https://github.com/kubernetes-sigs/metrics-server)
- [Prometheus Adapter](https://github.com/kubernetes-sigs/prometheus-adapter)
