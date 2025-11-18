# Production Deployment Guide

Complete guide for deploying the Multi-Website Platform to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Architecture Options](#architecture-options)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Docker Swarm Deployment](#docker-swarm-deployment)
5. [Cloud Platforms](#cloud-platforms)
6. [Database Setup](#database-setup)
7. [Security](#security)
8. [Monitoring](#monitoring)
9. [Scaling](#scaling)
10. [Backup & Recovery](#backup--recovery)

---

## Prerequisites

### Infrastructure Requirements

**Minimum (Single Server):**
- 4 CPU cores
- 16GB RAM
- 100GB SSD storage
- Ubuntu 20.04+ / Debian 11+ / RHEL 8+

**Recommended (Production):**
- 8+ CPU cores
- 32GB+ RAM
- 500GB+ SSD storage
- Load balancer
- Separate database server
- Redis cluster
- RabbitMQ cluster

### Software Requirements

- Docker 24.0+
- Docker Compose 2.20+ OR
- Kubernetes 1.27+ OR
- Docker Swarm mode

---

## Architecture Options

### Option 1: Single Server (Small Scale)

```
┌─────────────────────────────────────┐
│   Single Server (16GB RAM)          │
├─────────────────────────────────────┤
│  Nginx (API Gateway)                │
│  ├─ All 6 Domain Services           │
│  PostgreSQL (all databases)         │
│  Redis                              │
│  RabbitMQ                           │
└─────────────────────────────────────┘
```

**Best for:** <1000 sites, development, staging

**Deployment:** Docker Compose (provided in this repo)

### Option 2: Multi-Server (Medium Scale)

```
┌─────────────┐   ┌──────────────────┐   ┌─────────────┐
│ Load        │   │ App Servers (3+) │   │ Database    │
│ Balancer    ├───┤ Domain Services  ├───┤ Cluster     │
│ (Nginx)     │   │ (Docker/K8s)     │   │ (PostgreSQL)│
└─────────────┘   └──────────────────┘   └─────────────┘
                           │
                  ┌────────┴────────┐
                  │ Redis Cluster   │
                  │ RabbitMQ        │
                  └─────────────────┘
```

**Best for:** 1000-10,000 sites, production

**Deployment:** Kubernetes or Docker Swarm

### Option 3: Cloud Native (Large Scale)

```
┌─────────────┐   ┌──────────────────┐
│ CloudFront/ │   │ ECS/EKS/GKE      │
│ CDN         ├───┤ Auto-scaling     │
└─────────────┘   │ Services         │
                  └──────┬───────────┘
         ┌───────────────┼───────────────┐
    ┌────┴────┐   ┌──────┴──────┐   ┌────┴────┐
    │ RDS/    │   │ ElastiCache/│   │ SQS/    │
    │ Aurora  │   │ Redis       │   │ EventBr.│
    └─────────┘   └─────────────┘   └─────────┘
```

**Best for:** 10,000+ sites, global scale

**Deployment:** Managed Kubernetes (EKS, GKE, AKS)

---

## Kubernetes Deployment

### 1. Create Namespaces

```bash
kubectl create namespace platform-prod
kubectl create namespace platform-infra
```

### 2. Deploy Infrastructure

```yaml
# postgres-deployment.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: platform-infra
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        ports:
        - containerPort: 5432
        volumeMounts:
        - name: postgres-data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: postgres-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 100Gi
---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: platform-infra
spec:
  ports:
  - port: 5432
  clusterIP: None
  selector:
    app: postgres
```

### 3. Deploy Services

```yaml
# storefront-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: storefront-service
  namespace: platform-prod
spec:
  replicas: 3
  selector:
    matchLabels:
      app: storefront-service
  template:
    metadata:
      labels:
        app: storefront-service
    spec:
      containers:
      - name: storefront-service
        image: your-registry/storefront-service:latest
        ports:
        - containerPort: 8011
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: service-secrets
              key: storefront-db-url
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8011
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8011
          initialDelaySeconds: 10
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: storefront-service
  namespace: platform-prod
spec:
  selector:
    app: storefront-service
  ports:
  - port: 8011
    targetPort: 8011
  type: ClusterIP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: storefront-service
  namespace: platform-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: storefront-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 4. Deploy Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: platform-ingress
  namespace: platform-prod
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.yourplatform.com
    secretName: platform-tls
  rules:
  - host: api.yourplatform.com
    http:
      paths:
      - path: /api/sites
        pathType: Prefix
        backend:
          service:
            name: site-service
            port:
              number: 8010
      - path: /api/storefront
        pathType: Prefix
        backend:
          service:
            name: storefront-service
            port:
              number: 8011
      - path: /api/bookings
        pathType: Prefix
        backend:
          service:
            name: booking-service
            port:
              number: 8012
```

---

## Docker Swarm Deployment

### 1. Initialize Swarm

```bash
# On manager node
docker swarm init --advertise-addr <MANAGER-IP>

# On worker nodes
docker swarm join --token <TOKEN> <MANAGER-IP>:2377
```

### 2. Create Overlay Network

```bash
docker network create -d overlay platform_network
```

### 3. Deploy Stack

```bash
# Use the provided docker-compose.yml with swarm-specific configs
docker stack deploy -c docker-compose.yml platform
```

### 4. Scale Services

```bash
docker service scale platform_storefront-service=5
docker service scale platform_booking-service=3
```

---

## Cloud Platforms

### AWS (Elastic Container Service)

```bash
# 1. Create ECR repositories
aws ecr create-repository --repository-name site-service
aws ecr create-repository --repository-name storefront-service
# ... repeat for all services

# 2. Build and push images
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t site-service domain-services/site-service
docker tag site-service:latest <account>.dkr.ecr.us-east-1.amazonaws.com/site-service:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/site-service:latest

# 3. Create ECS cluster
aws ecs create-cluster --cluster-name platform-prod

# 4. Create task definitions and services (use AWS Console or CloudFormation)
```

### Google Cloud (GKE)

```bash
# 1. Create GKE cluster
gcloud container clusters create platform-prod \
  --num-nodes=3 \
  --machine-type=n1-standard-4 \
  --region=us-central1

# 2. Get credentials
gcloud container clusters get-credentials platform-prod

# 3. Deploy using kubectl (see Kubernetes section above)
```

### Azure (AKS)

```bash
# 1. Create resource group
az group create --name platform-rg --location eastus

# 2. Create AKS cluster
az aks create \
  --resource-group platform-rg \
  --name platform-prod \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# 3. Get credentials
az aks get-credentials --resource-group platform-rg --name platform-prod

# 4. Deploy using kubectl
```

---

## Database Setup

### Production PostgreSQL Configuration

**Recommended:** Use managed database services
- AWS RDS PostgreSQL
- Google Cloud SQL
- Azure Database for PostgreSQL
- DigitalOcean Managed Databases

**Self-Hosted:**

```bash
# PostgreSQL tuning for production
# Edit postgresql.conf

max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
maintenance_work_mem = 1GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 10MB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Database Migrations

```bash
# Use Alembic for schema migrations
cd domain-services/storefront-service
alembic upgrade head
```

### Database Backups

```bash
# Automated backups
0 2 * * * pg_dump -U platform_user storefront_service_db | gzip > /backups/storefront_$(date +\%Y\%m\%d).sql.gz

# Retention policy: Keep daily for 7 days, weekly for 4 weeks, monthly for 12 months
```

---

## Security

### 1. Environment Variables

**Never commit secrets!** Use secret management:

```bash
# Kubernetes Secrets
kubectl create secret generic service-secrets \
  --from-literal=storefront-db-url="postgresql://..." \
  --from-literal=jwt-secret="..." \
  -n platform-prod

# Docker Swarm Secrets
echo "postgresql://..." | docker secret create storefront_db_url -
```

### 2. Network Security

```bash
# Firewall rules (UFW example)
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw deny 5432/tcp   # PostgreSQL (only internal)
ufw deny 6379/tcp   # Redis (only internal)
```

### 3. SSL/TLS

```bash
# Use Let's Encrypt with cert-manager (Kubernetes)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Or use CloudFlare/AWS Certificate Manager for managed SSL
```

### 4. API Rate Limiting

Add to nginx config:
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
limit_req zone=api_limit burst=20 nodelay;
```

---

## Monitoring

### Prometheus + Grafana

```yaml
# prometheus-config.yaml
scrape_configs:
  - job_name: 'site-service'
    static_configs:
      - targets: ['site-service:8010']
  - job_name: 'storefront-service'
    static_configs:
      - targets: ['storefront-service:8011']
  # ... add all services
```

### Logging (ELK Stack)

```yaml
# filebeat.yaml
filebeat.inputs:
  - type: docker
    containers.ids: '*'

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

### Health Monitoring

```bash
# Healthchecks.io or similar
*/5 * * * * curl -fsS -m 10 --retry 5 https://hc-ping.com/your-uuid
```

---

## Scaling

### Horizontal Scaling

```bash
# Kubernetes
kubectl scale deployment storefront-service --replicas=10

# Docker Swarm
docker service scale platform_storefront-service=10
```

### Vertical Scaling

Update resource limits in deployment manifests

### Database Scaling

- Read replicas for heavy read workloads
- Connection pooling with PgBouncer
- Sharding for very large datasets

---

## Backup & Recovery

### Automated Backups

```bash
#!/bin/bash
# backup-all.sh

BACKUP_DIR="/backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup all databases
for db in site_service_db storefront_service_db booking_service_db lead_service_db content_service_db widget_service_db; do
    pg_dump -U platform_user $db | gzip > $BACKUP_DIR/$db.sql.gz
done

# Backup Redis
redis-cli --rdb $BACKUP_DIR/dump.rdb

# Upload to S3
aws s3 sync $BACKUP_DIR s3://platform-backups/$(date +%Y%m%d)/
```

### Disaster Recovery Plan

1. **Database:** Point-in-time recovery from backups
2. **Services:** Redeploy from container registry
3. **Configuration:** Store in version control
4. **Recovery Time Objective (RTO):** < 1 hour
5. **Recovery Point Objective (RPO):** < 15 minutes

---

## Checklist

Before going to production:

- [ ] All secrets moved to secret management
- [ ] Database backups configured
- [ ] SSL certificates configured
- [ ] Monitoring and alerting set up
- [ ] Load testing completed
- [ ] Security audit performed
- [ ] Disaster recovery plan documented
- [ ] Rate limiting configured
- [ ] CDN configured for static assets
- [ ] Database connection pooling configured
- [ ] Log aggregation configured
- [ ] Health check endpoints monitored
- [ ] Auto-scaling configured
- [ ] Documentation updated
- [ ] Team trained on operations

---

## Production URLs

After deployment, document your URLs:

- **API Gateway:** https://api.yourplatform.com
- **Service Docs:**
  - Site Service: https://api.yourplatform.com/sites/docs
  - Storefront: https://api.yourplatform.com/storefront/docs
  - Booking: https://api.yourplatform.com/bookings/docs
- **Admin Dashboard:** https://admin.yourplatform.com
- **Monitoring:** https://monitoring.yourplatform.com

---

**Your platform is now production-ready! 🚀**
