# Helm Charts for FlowTask

This directory contains Helm charts for deploying FlowTask application components to Kubernetes.

## Charts

- **backend** - FastAPI backend API with MCP and SQLModel
- **frontend** - Next.js frontend web application
- **postgres** - PostgreSQL database with persistent storage

## Quick Start

### Prerequisites

```bash
# Install Helm
brew install helm  # macOS
# Or download from: https://helm.sh/docs/intro/install/

# Start Minikube
minikube start --driver=docker --cpus=4 --memory=8192

# Configure Docker for Minikube
eval $(minikube docker-env)

# Build images
docker build -t backend:latest ./backend
docker build -t frontend:latest ./frontend
```

### Deploy All Components

```bash
# 1. Deploy PostgreSQL (must be first)
helm install postgres ./helm/postgres

# 2. Wait for postgres to be ready
kubectl wait --for=condition=ready pod/postgres-postgres-0 --timeout=120s

# 3. Deploy Backend
helm install backend ./helm/backend \
  --set env.DATABASE_URL='postgresql://todouser:changeme@postgres-postgres-service:5432/tododb' \
  --set env.JWT_SECRET_KEY='your-jwt-secret-here' \
  --set env.OPENAI_API_KEY='sk-your-openai-key'

# 4. Deploy Frontend
helm install frontend ./helm/frontend \
  --set env.NEXT_PUBLIC_API_URL='http://backend-backend-service:8000'

# 5. Verify deployments
helm list
kubectl get pods
```

### Access Application

```bash
# Get Minikube IP
minikube ip

# Access frontend
# Navigate to: http://<minikube-ip>:30000

# Or use port-forward
kubectl port-forward service/frontend-frontend-service 3000:3000
# Navigate to: http://localhost:3000
```

## Individual Chart Usage

### PostgreSQL Chart

```bash
# Install with default values
helm install postgres ./helm/postgres

# Install with custom password
helm install postgres ./helm/postgres \
  --set postgresql.password='my-secure-password'

# Install with custom storage size
helm install postgres ./helm/postgres \
  --set persistence.size=20Gi

# Verify installation
kubectl get statefulset postgres-postgres
kubectl get pvc
kubectl get service postgres-postgres-service
```

**Values Configuration:**
```yaml
# values.yaml or custom values file
replicaCount: 1
image:
  tag: "15-alpine"
postgresql:
  database: tododb
  username: todouser
  password: "changeme"  # CHANGE IN PRODUCTION
persistence:
  size: 10Gi
  storageClassName: standard
resources:
  requests:
    cpu: 250m
    memory: 256Mi
```

---

### Backend Chart

```bash
# Install with default values
helm install backend ./helm/backend

# Install with custom configuration
helm install backend ./helm/backend \
  --set replicaCount=3 \
  --set env.DATABASE_URL='postgresql://todouser:password@postgres-postgres-service:5432/tododb' \
  --set env.JWT_SECRET_KEY='your-jwt-secret' \
  --set env.OPENAI_API_KEY='sk-your-key'

# Install with values file
helm install backend ./helm/backend -f backend-prod-values.yaml

# Verify installation
kubectl get deployment backend-backend
kubectl get pods -l app=backend
kubectl get service backend-backend-service
```

**Values Configuration:**
```yaml
# values.yaml or custom values file
replicaCount: 3
image:
  repository: backend
  tag: "latest"
  pullPolicy: IfNotPresent
env:
  DATABASE_URL: "postgresql://todouser:password@postgres-postgres-service:5432/tododb"
  JWT_SECRET_KEY: "your-secret-key"
  OPENAI_API_KEY: "sk-your-key"
resources:
  requests:
    cpu: 500m
    memory: 512Mi
```

---

### Frontend Chart

```bash
# Install with default values
helm install frontend ./helm/frontend

# Install with custom backend URL
helm install frontend ./helm/frontend \
  --set env.NEXT_PUBLIC_API_URL='http://backend-backend-service:8000'

# Install with custom nodePort
helm install frontend ./helm/frontend \
  --set service.nodePort=31000

# Verify installation
kubectl get deployment frontend-frontend
kubectl get pods -l app=frontend
kubectl get service frontend-frontend-service
```

**Values Configuration:**
```yaml
# values.yaml or custom values file
replicaCount: 2
image:
  repository: frontend
  tag: "latest"
  pullPolicy: IfNotPresent
service:
  type: NodePort
  nodePort: 30000
env:
  NEXT_PUBLIC_API_URL: "http://backend-backend-service:8000"
resources:
  requests:
    cpu: 250m
    memory: 256Mi
```

---

## Chart Management

### List Installed Charts

```bash
helm list
helm list --all-namespaces
```

### Get Chart Status

```bash
helm status postgres
helm status backend
helm status frontend
```

### Upgrade Charts

```bash
# Upgrade with new values
helm upgrade backend ./helm/backend \
  --set replicaCount=5

# Upgrade with values file
helm upgrade backend ./helm/backend -f backend-prod-values.yaml

# Upgrade and reuse previous values
helm upgrade backend ./helm/backend --reuse-values
```

### Rollback Charts

```bash
# View revision history
helm history backend

# Rollback to previous version
helm rollback backend

# Rollback to specific revision
helm rollback backend 2
```

### Uninstall Charts

```bash
# Uninstall individual charts
helm uninstall frontend
helm uninstall backend
helm uninstall postgres

# Note: Uninstalling postgres does NOT delete PVC
# To delete PVC:
kubectl delete pvc postgres-storage-postgres-postgres-0
```

---

## Values Customization

### Using Values Files

Create custom values files for different environments:

**backend-dev-values.yaml:**
```yaml
replicaCount: 1
image:
  pullPolicy: Never  # For Minikube
resources:
  requests:
    cpu: 250m
    memory: 256Mi
env:
  DATABASE_URL: "postgresql://todouser:dev@postgres-postgres-service:5432/tododb"
```

**backend-prod-values.yaml:**
```yaml
replicaCount: 5
image:
  repository: gcr.io/my-project/backend
  tag: "v1.2.3"
  pullPolicy: Always
resources:
  requests:
    cpu: 1000m
    memory: 1Gi
  limits:
    cpu: 2000m
    memory: 2Gi
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
```

**Install with custom values:**
```bash
helm install backend ./helm/backend -f backend-prod-values.yaml
```

---

### Using --set Flags

Override specific values on command line:

```bash
# Single value
helm install backend ./helm/backend \
  --set replicaCount=5

# Multiple values
helm install backend ./helm/backend \
  --set replicaCount=5 \
  --set image.tag=v1.2.3

# Nested values
helm install backend ./helm/backend \
  --set resources.requests.cpu=1000m \
  --set resources.requests.memory=1Gi

# Array values
helm install backend ./helm/backend \
  --set imagePullSecrets[0].name=my-secret
```

---

## Template Validation

### Lint Charts

```bash
# Lint all charts
helm lint ./helm/backend
helm lint ./helm/frontend
helm lint ./helm/postgres

# Lint with custom values
helm lint ./helm/backend -f backend-prod-values.yaml
```

### Template Rendering

```bash
# Render templates without installing
helm template backend ./helm/backend

# Render with custom values
helm template backend ./helm/backend \
  --set replicaCount=3 \
  --set env.DATABASE_URL='postgresql://...'

# Save rendered templates to file
helm template backend ./helm/backend > backend-manifests.yaml

# Validate rendered YAML
helm template backend ./helm/backend | kubectl apply --dry-run=client -f -
```

---

## Troubleshooting

### Chart Installation Fails

```bash
# View installation events
helm status <release-name>

# View pod events
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>

# Debug template rendering
helm template <release> ./helm/<chart> --debug
```

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -l app=<component>

# Describe pod
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### Service Not Accessible

```bash
# Check service endpoints
kubectl get endpoints <service-name>

# Verify service selector matches pod labels
kubectl get pods --show-labels
kubectl describe service <service-name>
```

### Secret/ConfigMap Not Found

```bash
# List secrets
kubectl get secrets

# List configmaps
kubectl get configmaps

# If secret missing, check values:
# - secrets.create: true
# - secrets.enabled: true
```

---

## Production Considerations

### Security

1. **Never use default passwords in production**
   ```bash
   # Generate secure password
   openssl rand -base64 32

   # Pass via --set or values file
   helm install postgres ./helm/postgres \
     --set postgresql.password='YOUR_SECURE_PASSWORD'
   ```

2. **Use external secrets management**
   - Sealed Secrets
   - External Secrets Operator
   - HashiCorp Vault

3. **Enable RBAC and network policies**

### High Availability

1. **Increase replica counts**
   ```yaml
   backend:
     replicaCount: 5
   frontend:
     replicaCount: 3
   ```

2. **Enable autoscaling**
   ```yaml
   autoscaling:
     enabled: true
     minReplicas: 3
     maxReplicas: 10
     targetCPUUtilizationPercentage: 80
   ```

3. **Configure pod disruption budgets**
   ```yaml
   podDisruptionBudget:
     enabled: true
     minAvailable: 2
   ```

### Resource Management

1. **Set appropriate resource limits**
2. **Monitor resource usage**: `kubectl top pods`
3. **Adjust based on actual usage patterns**

### Backup & Recovery

1. **Regular database backups**
2. **Volume snapshots for PVCs**
3. **Test restore procedures**
4. **Store backups off-cluster**

---

## Additional Resources

- [Helm Documentation](https://helm.sh/docs/)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [FlowTask Documentation](../README.md)
