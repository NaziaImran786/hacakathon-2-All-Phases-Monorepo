# Kubernetes Quick Start Guide

Quick reference for deploying FlowTask to Kubernetes.

## Prerequisites

```bash
# Start Minikube
minikube start --driver=docker --cpus=4 --memory=8192

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

## Deploy PostgreSQL

```bash
# Option 1: Automated script
./scripts/deploy-postgres.sh

# Option 2: Manual
kubectl create secret generic postgres-secret --from-literal=password='YOUR_PASSWORD'
kubectl apply -f k8s/postgres/statefulset.yaml
kubectl apply -f k8s/postgres/service.yaml

# Verify
kubectl get pods -l app=postgres
kubectl get pvc
```

## Create Application Secrets

```bash
# Generate JWT secret
JWT_SECRET=$(openssl rand -hex 32)

# Create app-secrets
kubectl create secret generic app-secrets \
  --from-literal=database-url='postgresql://todouser:YOUR_PG_PASSWORD@postgres-service:5432/tododb' \
  --from-literal=jwt-secret="$JWT_SECRET" \
  --from-literal=openai-api-key='sk-YOUR_OPENAI_KEY'

# Verify
kubectl get secrets
```

## Build Docker Images

```bash
# Configure Docker to use Minikube daemon
eval $(minikube docker-env)

# Build images
docker build -t backend:latest ./backend
docker build -t frontend:latest ./frontend

# Verify
docker images | grep -E 'backend|frontend'
```

## Deploy Backend (Coming Next)

```bash
kubectl apply -f k8s/backend/deployment.yaml
kubectl apply -f k8s/backend/service.yaml
kubectl get pods -l app=backend
```

## Deploy Frontend (Coming Next)

```bash
kubectl apply -f k8s/frontend/deployment.yaml
kubectl apply -f k8s/frontend/service.yaml
kubectl get pods -l app=frontend
```

## Access Application

```bash
# Get Minikube IP
minikube ip

# Access frontend
# Navigate to: http://<minikube-ip>:30000

# Or use port-forward
kubectl port-forward service/frontend-service 3000:3000
# Navigate to: http://localhost:3000
```

## Common Commands

```bash
# Check all pods
kubectl get pods

# Check all services
kubectl get services

# Check PVCs
kubectl get pvc

# View logs
kubectl logs <pod-name>

# Describe resource
kubectl describe pod <pod-name>

# Delete resources
kubectl delete -f k8s/postgres/
kubectl delete -f k8s/backend/
kubectl delete -f k8s/frontend/

# Delete PVCs (WARNING: Data loss!)
kubectl delete pvc --all
```

## Troubleshooting

```bash
# Pod not starting
kubectl describe pod <pod-name>
kubectl logs <pod-name>

# Service not accessible
kubectl get endpoints <service-name>

# DNS issues
kubectl exec -it <pod-name> -- nslookup postgres-service

# Restart deployment
kubectl rollout restart deployment <deployment-name>
```

## Cleanup

```bash
# Delete all resources
kubectl delete -f k8s/

# Delete PVCs
kubectl delete pvc --all

# Stop Minikube
minikube stop

# Delete Minikube cluster
minikube delete
```

## Documentation

- PostgreSQL: `k8s/postgres/README.md`
- Docker Build: `DOCKER-BUILD-GUIDE.md`
- Full Guide: `README-k8s.md` (coming soon)
