# Feature Specification: Local Kubernetes Deployment

**Feature Branch**: `feat/kubernetes-deployment`
**Created**: 2026-01-02
**Status**: Draft
**Phase**: IV - Infrastructure & Deployment

## Overview

This specification covers the containerization and orchestration of the FlowTask application using Docker and Kubernetes (Minikube). The goal is to deploy the FastAPI backend, Next.js frontend, and PostgreSQL database to a local Kubernetes cluster with proper networking, secrets management, and resource allocation.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Deploy Backend to Kubernetes (Priority: P1)

As a DevOps engineer, I want to deploy the FastAPI backend as a containerized service in Kubernetes so that it can scale horizontally and be managed declaratively.

**Why this priority**: The backend is the core service that handles authentication, API requests, and MCP server operations.

**Independent Test**: Can be tested by applying backend manifests and verifying pod status and service accessibility.

**Acceptance Scenarios**:

1. **Given** backend Dockerfile exists, **When** Docker image is built, **Then** image contains all Python dependencies and application code
2. **Given** backend Helm chart is applied, **When** kubectl get pods is run, **Then** backend pod is in Running state
3. **Given** backend service is created, **When** port-forward is established, **Then** backend health endpoint returns 200 OK
4. **Given** backend requires environment variables, **When** pod starts, **Then** all required secrets are mounted correctly
5. **Given** database connection is configured, **When** backend starts, **Then** SQLModel successfully connects to PostgreSQL

---

### User Story 2 - Deploy Frontend to Kubernetes (Priority: P1)

As a DevOps engineer, I want to deploy the Next.js frontend as a containerized service in Kubernetes so that users can access the web interface.

**Why this priority**: The frontend is the user-facing interface that must be accessible and scalable.

**Independent Test**: Can be tested by applying frontend manifests and accessing the application through port-forward or ingress.

**Acceptance Scenarios**:

1. **Given** frontend Dockerfile exists, **When** Docker image is built, **Then** image contains optimized Next.js production build
2. **Given** frontend Helm chart is applied, **When** kubectl get pods is run, **Then** frontend pod is in Running state
3. **Given** frontend service is created, **When** browser accesses service, **Then** login page is displayed correctly
4. **Given** frontend environment variables are set, **When** app loads, **Then** API_URL points to backend service
5. **Given** frontend and backend are deployed, **When** user authenticates, **Then** JWT token is successfully issued and stored

---

### User Story 3 - Configure Database Persistence (Priority: P1)

As a DevOps engineer, I want to configure persistent storage for PostgreSQL so that data survives pod restarts and redeployments.

**Why this priority**: Data persistence is critical for production-grade deployments to prevent data loss.

**Independent Test**: Can be tested by creating a task, deleting the database pod, and verifying the task still exists after pod recreation.

**Acceptance Scenarios**:

1. **Given** PersistentVolumeClaim is created, **When** PostgreSQL pod starts, **Then** PVC is bound and mounted to /var/lib/postgresql/data
2. **Given** tasks exist in database, **When** PostgreSQL pod is deleted and recreated, **Then** all tasks are still accessible
3. **Given** database credentials are configured, **When** backend connects, **Then** connection uses credentials from Kubernetes Secret
4. **Given** database is initialized, **When** backend starts, **Then** tables (users, tasks, conversations, messages) are created

---

### User Story 4 - Implement Service Discovery (Priority: P1)

As a DevOps engineer, I want to configure Kubernetes Services for internal communication so that frontend can reliably communicate with backend.

**Why this priority**: Service discovery enables reliable communication between microservices in a Kubernetes cluster.

**Independent Test**: Can be tested by exec-ing into frontend pod and curling the backend service by DNS name.

**Acceptance Scenarios**:

1. **Given** backend service is named "backend-service", **When** frontend pod resolves DNS, **Then** backend-service.default.svc.cluster.local resolves to backend pod IP
2. **Given** services are created, **When** frontend makes API call, **Then** request routes to backend pod successfully
3. **Given** multiple backend replicas exist, **When** frontend makes requests, **Then** load is balanced across replicas
4. **Given** backend service is type ClusterIP, **When** accessed internally, **Then** service is accessible only within cluster

---

### User Story 5 - Manage Secrets Securely (Priority: P1)

As a DevOps engineer, I want to store sensitive configuration (DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY) as Kubernetes Secrets so that credentials are not hardcoded.

**Why this priority**: Security best practices require secrets to be stored encrypted and mounted at runtime.

**Independent Test**: Can be tested by creating secrets, deploying pods, and verifying environment variables are correctly injected.

**Acceptance Scenarios**:

1. **Given** secret "app-secrets" is created, **When** backend pod starts, **Then** DATABASE_URL is available as environment variable
2. **Given** secrets are base64 encoded, **When** pod reads environment, **Then** values are automatically decoded
3. **Given** secret is updated, **When** pods are restarted, **Then** new secret values are loaded
4. **Given** OPENAI_API_KEY is required, **When** MCP server initializes, **Then** API key is read from environment

---

### User Story 6 - Create Helm Charts (Priority: P2)

As a DevOps engineer, I want to package application manifests as Helm charts so that deployments are templated and configurable.

**Why this priority**: Helm charts enable versioning, templating, and easier management of Kubernetes resources.

**Independent Test**: Can be tested by running `helm install` and verifying all resources are created with correct values.

**Acceptance Scenarios**:

1. **Given** backend Helm chart exists, **When** `helm install backend ./helm/backend` is run, **Then** all backend resources are created
2. **Given** values.yaml contains image.tag, **When** chart is installed, **Then** pod uses specified image tag
3. **Given** multiple environments (dev, prod), **When** chart is installed with different values files, **Then** correct configurations are applied
4. **Given** chart dependencies exist, **When** `helm dependency update` is run, **Then** dependencies are resolved and charts are downloaded

---

### User Story 7 - Configure Resource Limits (Priority: P2)

As a DevOps engineer, I want to set CPU and memory requests/limits so that pods have guaranteed resources and don't consume excessive cluster capacity.

**Why this priority**: Resource management prevents resource starvation and ensures predictable performance.

**Independent Test**: Can be tested by describing pods and verifying requests/limits are set correctly.

**Acceptance Scenarios**:

1. **Given** backend pod has resource requests, **When** pod is scheduled, **Then** Kubernetes reserves CPU and memory
2. **Given** backend pod has resource limits, **When** pod exceeds memory limit, **Then** pod is OOMKilled and restarted
3. **Given** frontend pod has smaller resource footprint, **When** pods are scheduled, **Then** frontend uses fewer resources than backend
4. **Given** cluster has limited capacity, **When** pods are scheduled, **Then** scheduler places pods based on available resources

---

### User Story 8 - Implement Health Checks (Priority: P2)

As a DevOps engineer, I want to configure liveness and readiness probes so that Kubernetes can automatically restart unhealthy pods and route traffic only to ready pods.

**Why this priority**: Health checks ensure high availability and automatic recovery from failures.

**Independent Test**: Can be tested by simulating failure conditions and verifying Kubernetes restarts pods.

**Acceptance Scenarios**:

1. **Given** backend has readiness probe on /health, **When** pod starts, **Then** pod is marked Ready only after probe succeeds
2. **Given** backend becomes unresponsive, **When** liveness probe fails 3 times, **Then** Kubernetes restarts the pod
3. **Given** database connection is lost, **When** readiness probe checks, **Then** pod is marked Unready until connection is restored
4. **Given** frontend has startup probe, **When** Next.js build completes, **Then** pod transitions to Ready state

---

### Edge Cases

- What happens when database connection fails during pod startup?
- How does the system handle image pull failures from private registries?
- What happens when secrets are missing or malformed?
- How does the system handle pod evictions due to resource pressure?
- What happens when persistent volume claims cannot be bound?
- How does the system handle rolling updates with database migrations?
- What happens when service endpoints are temporarily unavailable?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide Dockerfile for FastAPI backend with multi-stage build
- **FR-002**: System MUST provide Dockerfile for Next.js frontend with optimized production build
- **FR-003**: System MUST provide Kubernetes manifests (Deployment, Service, ConfigMap, Secret)
- **FR-004**: System MUST provide Helm charts for backend and frontend
- **FR-005**: System MUST configure PostgreSQL StatefulSet with persistent storage
- **FR-006**: System MUST implement service discovery using ClusterIP services
- **FR-007**: System MUST store sensitive configuration in Kubernetes Secrets
- **FR-008**: System MUST configure resource requests and limits for all pods
- **FR-009**: System MUST implement liveness and readiness probes for health checks
- **FR-010**: System MUST support deployment to Minikube for local development

### Key Entities

- **Docker Image (Backend)**: Containerized FastAPI application with Python dependencies
- **Docker Image (Frontend)**: Containerized Next.js application with optimized production build
- **Kubernetes Deployment**: Declarative pod template with replica count and update strategy
- **Kubernetes Service**: Network abstraction for pod communication (ClusterIP, NodePort, LoadBalancer)
- **Kubernetes Secret**: Encrypted storage for sensitive data (DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY)
- **Kubernetes ConfigMap**: Non-sensitive configuration data
- **PersistentVolume/PersistentVolumeClaim**: Storage abstraction for stateful workloads
- **Helm Chart**: Packaged Kubernetes manifests with templating and versioning

### Technical Stack

**Containerization:**
- Docker 24+
- Multi-stage builds for optimized image size
- Alpine Linux base images where applicable

**Orchestration:**
- Kubernetes 1.28+
- Minikube for local development
- kubectl CLI for cluster management
- Helm 3.x for package management

**Infrastructure:**
- PostgreSQL 15 (StatefulSet with PVC)
- Neon PostgreSQL connection string support
- Service mesh considerations for future scaling

## Architecture Design

### Container Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Docker Images                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────┐     ┌──────────────────────┐     │
│  │   Backend Image      │     │   Frontend Image     │     │
│  │                      │     │                      │     │
│  │  Base: python:3.11   │     │  Base: node:20-alpine│     │
│  │  Port: 8000          │     │  Port: 3000          │     │
│  │  CMD: uvicorn app:app│     │  CMD: npm start      │     │
│  └──────────────────────┘     └──────────────────────┘     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Kubernetes Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster (Minikube)             │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   Namespace: default                  │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │                                                        │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────┐  │   │
│  │  │  Frontend   │───▶│  Backend    │───▶│ Postgres│  │   │
│  │  │  Deployment │    │  Deployment │    │StatefulS│  │   │
│  │  │  (2 replicas)│    │  (3 replicas)│    │et (1 pod│  │   │
│  │  └─────────────┘    └─────────────┘    └─────────┘  │   │
│  │        │                   │                 │        │   │
│  │        ▼                   ▼                 ▼        │   │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────┐  │   │
│  │  │  frontend-  │    │  backend-   │    │postgres-│  │   │
│  │  │  service    │    │  service    │    │ service │  │   │
│  │  │  (ClusterIP)│    │  (ClusterIP)│    │(ClusterI│  │   │
│  │  │  Port: 3000 │    │  Port: 8000 │    │P) 5432  │  │   │
│  │  └─────────────┘    └─────────────┘    └─────────┘  │   │
│  │                                              │        │   │
│  │                                              ▼        │   │
│  │                                        ┌─────────┐   │   │
│  │                                        │   PVC   │   │   │
│  │                                        │10Gi RWO │   │   │
│  │                                        └─────────┘   │   │
│  │                                                        │   │
│  │  ┌──────────────────────────────────────────────┐   │   │
│  │  │            Kubernetes Secrets                 │   │   │
│  │  │  - DATABASE_URL (postgres connection string) │   │   │
│  │  │  - JWT_SECRET_KEY (authentication secret)    │   │   │
│  │  │  - OPENAI_API_KEY (OpenAI API credentials)   │   │   │
│  │  └──────────────────────────────────────────────┘   │   │
│  │                                                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Helm Chart Structure

```
helm/
├── backend/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── templates/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── secret.yaml
│   │   ├── configmap.yaml
│   │   ├── hpa.yaml (optional)
│   │   └── _helpers.tpl
│   └── .helmignore
│
├── frontend/
│   ├── Chart.yaml
│   ├── values.yaml
│   ├── templates/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   │   └── _helpers.tpl
│   └── .helmignore
│
└── postgres/
    ├── Chart.yaml
    ├── values.yaml
    ├── templates/
    │   ├── statefulset.yaml
    │   ├── service.yaml
    │   ├── pvc.yaml
    │   └── _helpers.tpl
    └── .helmignore
```

## Implementation Details

### Backend Dockerfile

**Multi-stage build strategy:**

1. **Stage 1 - Builder**: Install dependencies and compile if needed
2. **Stage 2 - Runtime**: Copy only necessary files, minimal attack surface

**Key considerations:**
- Use `python:3.11-slim` for smaller image size
- Create non-root user for security
- Copy requirements.txt first for layer caching
- Set working directory to /app
- Expose port 8000
- Use CMD with list syntax (not shell form)

**Environment variables required:**
- DATABASE_URL
- JWT_SECRET_KEY
- OPENAI_API_KEY
- MCP_SERVER_HOST (if MCP runs separately)

### Frontend Dockerfile

**Multi-stage build strategy:**

1. **Stage 1 - Dependencies**: Install node_modules
2. **Stage 2 - Builder**: Run `next build` to create optimized production build
3. **Stage 3 - Runtime**: Copy build artifacts and serve with `next start`

**Key considerations:**
- Use `node:20-alpine` for smaller image size
- Set NODE_ENV=production
- Copy package.json and package-lock.json first for layer caching
- Use `npm ci` instead of `npm install` for reproducible builds
- Copy .next, public, and node_modules to runtime stage
- Expose port 3000
- Use non-root user

**Environment variables required:**
- NEXT_PUBLIC_API_URL (points to backend service)

### Backend Deployment Manifest

**Key configurations:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: database-url
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: jwt-secret
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: openai-api-key
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "1000m"
            memory: "1Gi"
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Frontend Deployment Manifest

**Key configurations:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: NEXT_PUBLIC_API_URL
          value: "http://backend-service:8000"
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### PostgreSQL StatefulSet

**Key configurations:**

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
spec:
  serviceName: postgres-service
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
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_USER
          value: "todouser"
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-secret
              key: password
        - name: POSTGRES_DB
          value: "tododb"
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            cpu: "250m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

### Service Manifests

**Backend Service:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
```

**Frontend Service:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: NodePort  # For Minikube access
  selector:
    app: frontend
  ports:
  - protocol: TCP
    port: 3000
    targetPort: 3000
    nodePort: 30000  # Access via http://minikube-ip:30000
```

**PostgreSQL Service:**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
spec:
  type: ClusterIP
  selector:
    app: postgres
  ports:
  - protocol: TCP
    port: 5432
    targetPort: 5432
```

### Secrets Management

**Create secrets using kubectl:**

```bash
# Create app secrets
kubectl create secret generic app-secrets \
  --from-literal=database-url='postgresql://todouser:password@postgres-service:5432/tododb' \
  --from-literal=jwt-secret='your-secret-key-here' \
  --from-literal=openai-api-key='sk-...'

# Create postgres secrets
kubectl create secret generic postgres-secret \
  --from-literal=password='securepassword123'
```

**Alternative: Create from YAML (not recommended for production):**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
data:
  database-url: cG9zdGdyZXNxbDovL3RvZG91c2VyOnBhc3N3b3JkQHBvc3RncmVzLXNlcnZpY2U6NTQzMi90b2RvZGI=
  jwt-secret: eW91ci1zZWNyZXQta2V5LWhlcmU=
  openai-api-key: c2stLi4u
```

### Helm Values Configuration

**backend/values.yaml:**

```yaml
replicaCount: 3

image:
  repository: backend
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8000

resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 1000m
    memory: 1Gi

env:
  DATABASE_URL: "postgresql://todouser:password@postgres-service:5432/tododb"
  JWT_SECRET_KEY: "your-secret-key"
  OPENAI_API_KEY: "sk-..."

healthCheck:
  liveness:
    path: /
    initialDelaySeconds: 30
    periodSeconds: 10
  readiness:
    path: /
    initialDelaySeconds: 5
    periodSeconds: 5
```

**frontend/values.yaml:**

```yaml
replicaCount: 2

image:
  repository: frontend
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: NodePort
  port: 3000
  nodePort: 30000

resources:
  requests:
    cpu: 250m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi

env:
  NEXT_PUBLIC_API_URL: "http://backend-service:8000"

healthCheck:
  liveness:
    path: /
    initialDelaySeconds: 30
    periodSeconds: 10
  readiness:
    path: /
    initialDelaySeconds: 10
    periodSeconds: 5
```

## Deployment Workflow

### Prerequisites

1. Install Minikube: `brew install minikube` (macOS) or download from minikube.sigs.k8s.io
2. Install kubectl: `brew install kubectl`
3. Install Helm: `brew install helm`
4. Install Docker: docker.com/get-docker
5. Start Minikube: `minikube start --driver=docker --cpus=4 --memory=8192`

### Step 1: Build Docker Images

```bash
# Configure Docker to use Minikube's Docker daemon
eval $(minikube docker-env)

# Build backend image
cd backend
docker build -t backend:latest .

# Build frontend image
cd ../frontend
docker build -t frontend:latest .

# Verify images
docker images | grep -E "backend|frontend"
```

### Step 2: Create Namespace (Optional)

```bash
kubectl create namespace flowtask
kubectl config set-context --current --namespace=flowtask
```

### Step 3: Create Secrets

```bash
# Create app secrets
kubectl create secret generic app-secrets \
  --from-literal=database-url='postgresql://todouser:password@postgres-service:5432/tododb' \
  --from-literal=jwt-secret='your-secret-key-here' \
  --from-literal=openai-api-key='sk-...'

# Create postgres secrets
kubectl create secret generic postgres-secret \
  --from-literal=password='securepassword123'

# Verify secrets
kubectl get secrets
```

### Step 4: Deploy PostgreSQL

```bash
# Option 1: Using kubectl
kubectl apply -f k8s/postgres/

# Option 2: Using Helm
helm install postgres ./helm/postgres

# Verify deployment
kubectl get statefulsets
kubectl get pods -l app=postgres
kubectl get pvc
```

### Step 5: Deploy Backend

```bash
# Option 1: Using kubectl
kubectl apply -f k8s/backend/

# Option 2: Using Helm
helm install backend ./helm/backend

# Verify deployment
kubectl get deployments
kubectl get pods -l app=backend
kubectl logs -l app=backend --tail=50
```

### Step 6: Deploy Frontend

```bash
# Option 1: Using kubectl
kubectl apply -f k8s/frontend/

# Option 2: Using Helm
helm install frontend ./helm/frontend

# Verify deployment
kubectl get deployments
kubectl get pods -l app=frontend
kubectl logs -l app=frontend --tail=50
```

### Step 7: Verify Services

```bash
# Check all services
kubectl get services

# Check endpoints
kubectl get endpoints

# Verify DNS resolution
kubectl run test-pod --image=busybox --rm -it --restart=Never -- nslookup backend-service
```

### Step 8: Access Application

```bash
# Get Minikube IP
minikube ip

# Access frontend (if using NodePort)
# Navigate to http://<minikube-ip>:30000

# Alternative: Use port-forward
kubectl port-forward service/frontend-service 3000:3000
kubectl port-forward service/backend-service 8000:8000

# Access via localhost
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
```

### Step 9: Verify End-to-End Flow

```bash
# Test backend health
curl http://localhost:8000/

# Test signup
curl -X POST http://localhost:8000/signup \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# Test login
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass"

# Open browser and test full flow
open http://localhost:3000
```

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Backend Docker image builds successfully and is under 500MB
- **SC-002**: Frontend Docker image builds successfully and is under 300MB
- **SC-003**: All pods reach Running state within 2 minutes of deployment
- **SC-004**: Health checks pass for all services within 30 seconds of pod readiness
- **SC-005**: Frontend successfully communicates with backend via service DNS
- **SC-006**: PostgreSQL data persists after pod deletion and recreation
- **SC-007**: Secrets are correctly mounted and readable by pods
- **SC-008**: Application supports at least 10 concurrent users without errors
- **SC-009**: Helm charts successfully install and uninstall without errors
- **SC-010**: Resource limits prevent pods from consuming excessive CPU/memory

## Non-Functional Requirements

- **NFR-001**: Docker images MUST use multi-stage builds for optimization
- **NFR-002**: All pods MUST run as non-root users
- **NFR-003**: Secrets MUST NOT be committed to version control
- **NFR-004**: Resource requests MUST be set to ensure scheduling guarantees
- **NFR-005**: Health probes MUST detect failures and trigger automatic restarts
- **NFR-006**: StatefulSet MUST use PersistentVolumeClaim for data persistence
- **NFR-007**: Services MUST use ClusterIP for internal communication
- **NFR-008**: Deployment MUST support rolling updates with zero downtime
- **NFR-009**: Helm charts MUST be templated and support multiple environments
- **NFR-010**: Documentation MUST include troubleshooting guide for common issues

## Troubleshooting Guide

### Pod Stuck in Pending State

**Symptoms**: Pod shows `Pending` status indefinitely

**Possible Causes**:
- Insufficient cluster resources (CPU/memory)
- PVC cannot be bound to PV
- Image pull errors

**Resolution**:
```bash
# Check pod events
kubectl describe pod <pod-name>

# Check cluster resources
kubectl top nodes

# Check PVC status
kubectl get pvc
```

### ImagePullBackOff Error

**Symptoms**: Pod shows `ImagePullBackOff` or `ErrImagePull`

**Possible Causes**:
- Image doesn't exist in Docker daemon
- Wrong image name or tag
- Not using Minikube's Docker daemon

**Resolution**:
```bash
# Ensure you're using Minikube's Docker daemon
eval $(minikube docker-env)

# Rebuild images
docker build -t backend:latest ./backend
docker build -t frontend:latest ./frontend

# Set imagePullPolicy to Never in Helm values
image:
  pullPolicy: Never
```

### CrashLoopBackOff Error

**Symptoms**: Pod repeatedly crashes and restarts

**Possible Causes**:
- Application errors on startup
- Missing environment variables
- Database connection failures

**Resolution**:
```bash
# Check pod logs
kubectl logs <pod-name>

# Check previous logs (if restarted)
kubectl logs <pod-name> --previous

# Check environment variables
kubectl exec <pod-name> -- env
```

### Service Cannot Reach Backend

**Symptoms**: Frontend gets connection errors when calling backend

**Possible Causes**:
- Service selector doesn't match pod labels
- Backend pods not ready
- CORS configuration issues

**Resolution**:
```bash
# Verify service endpoints
kubectl get endpoints backend-service

# Test connectivity from frontend pod
kubectl exec -it <frontend-pod> -- wget -O- http://backend-service:8000/

# Check backend logs for CORS errors
kubectl logs -l app=backend
```

### Database Connection Refused

**Symptoms**: Backend logs show "connection refused" to PostgreSQL

**Possible Causes**:
- PostgreSQL pod not ready
- Wrong DATABASE_URL format
- Network policy blocking traffic

**Resolution**:
```bash
# Check PostgreSQL pod status
kubectl get pods -l app=postgres

# Verify PostgreSQL service
kubectl get service postgres-service

# Test connectivity
kubectl exec -it <backend-pod> -- nc -zv postgres-service 5432

# Check DATABASE_URL format
kubectl exec <backend-pod> -- env | grep DATABASE_URL
```

## Future Enhancements

- **Ingress Controller**: Replace NodePort with Ingress for production-like routing
- **Horizontal Pod Autoscaler**: Auto-scale pods based on CPU/memory metrics
- **Monitoring**: Integrate Prometheus and Grafana for observability
- **Logging**: Deploy EFK (Elasticsearch, Fluentd, Kibana) stack for centralized logging
- **CI/CD**: Integrate with GitHub Actions for automated builds and deployments
- **Multi-environment**: Configure separate namespaces for dev, staging, and production
- **Service Mesh**: Implement Istio for advanced traffic management and security
- **Database Replication**: Configure PostgreSQL read replicas for high availability
- **Backup & Restore**: Implement Velero for cluster backup and disaster recovery
- **Network Policies**: Restrict pod-to-pod communication for zero-trust security

## References

- Kubernetes Documentation: https://kubernetes.io/docs/
- Helm Documentation: https://helm.sh/docs/
- Minikube Documentation: https://minikube.sigs.k8s.io/docs/
- Docker Best Practices: https://docs.docker.com/develop/dev-best-practices/
- Next.js Docker Deployment: https://nextjs.org/docs/deployment#docker-image
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/docker/

## Appendix: File Structure

```
hackathon-2-phase-4-todo-web-chatbot/
├── backend/
│   ├── Dockerfile                    # Backend Docker configuration
│   ├── .dockerignore                 # Docker ignore patterns
│   ├── app.py                        # FastAPI application
│   ├── requirements.txt              # Python dependencies
│   └── ...
├── frontend/
│   ├── Dockerfile                    # Frontend Docker configuration
│   ├── .dockerignore                 # Docker ignore patterns
│   ├── package.json                  # Node.js dependencies
│   ├── next.config.js                # Next.js configuration
│   └── ...
├── k8s/
│   ├── backend/
│   │   ├── deployment.yaml           # Backend Deployment manifest
│   │   ├── service.yaml              # Backend Service manifest
│   │   └── configmap.yaml            # Backend ConfigMap
│   ├── frontend/
│   │   ├── deployment.yaml           # Frontend Deployment manifest
│   │   ├── service.yaml              # Frontend Service manifest
│   │   └── configmap.yaml            # Frontend ConfigMap
│   ├── postgres/
│   │   ├── statefulset.yaml          # PostgreSQL StatefulSet
│   │   ├── service.yaml              # PostgreSQL Service
│   │   └── pvc.yaml                  # PersistentVolumeClaim
│   └── secrets/
│       ├── app-secrets.yaml          # Application secrets (gitignored)
│       └── postgres-secret.yaml      # PostgreSQL secrets (gitignored)
├── helm/
│   ├── backend/
│   │   ├── Chart.yaml                # Helm chart metadata
│   │   ├── values.yaml               # Default configuration values
│   │   └── templates/
│   │       ├── deployment.yaml       # Templated Deployment
│   │       ├── service.yaml          # Templated Service
│   │       ├── secret.yaml           # Templated Secret
│   │       └── _helpers.tpl          # Template helpers
│   ├── frontend/
│   │   └── ...                       # Similar structure
│   └── postgres/
│       └── ...                       # Similar structure
├── scripts/
│   ├── build-images.sh               # Script to build all Docker images
│   ├── deploy-all.sh                 # Script to deploy all components
│   └── cleanup.sh                    # Script to cleanup deployments
└── README-k8s.md                     # Kubernetes deployment guide
```

## Test Plan

### Unit Tests

- Dockerfile builds complete without errors
- Image size is within acceptable limits
- All required files are copied to images
- Environment variables are correctly set

### Integration Tests

- Pods start and reach Running state
- Health checks pass for all services
- Service discovery resolves correct endpoints
- Database connection succeeds from backend pods

### End-to-End Tests

- User can register and login via frontend
- Tasks can be created, read, updated, and deleted
- AI chatbot can communicate with backend
- Data persists after pod restarts
- Application handles concurrent users

### Performance Tests

- Application responds within acceptable latency
- Resource usage stays within limits
- Rolling updates complete without downtime
- Database handles expected query load

## Risk Analysis

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Image build failures | High | Medium | Multi-stage builds with clear error messages |
| Insufficient cluster resources | High | Medium | Set appropriate resource requests/limits |
| Database connection failures | High | Low | Implement retry logic and connection pooling |
| Secret exposure | Critical | Low | Use Kubernetes Secrets, never commit to git |
| Data loss during pod restarts | Critical | Low | Use PersistentVolumes for stateful workloads |
| Service discovery failures | Medium | Low | Use standard Kubernetes DNS naming conventions |
| Health check false negatives | Medium | Medium | Tune probe thresholds and timeouts |
| Rolling update failures | Medium | Low | Implement readiness probes and rollback strategy |

## Glossary

- **Docker**: Platform for building and running containerized applications
- **Kubernetes**: Container orchestration platform for managing containerized workloads
- **Minikube**: Local Kubernetes cluster for development and testing
- **Helm**: Package manager for Kubernetes manifests
- **Pod**: Smallest deployable unit in Kubernetes (one or more containers)
- **Deployment**: Kubernetes resource for managing stateless applications
- **StatefulSet**: Kubernetes resource for managing stateful applications
- **Service**: Kubernetes network abstraction for exposing pods
- **PersistentVolume**: Storage resource in Kubernetes cluster
- **PersistentVolumeClaim**: Request for storage by a pod
- **ConfigMap**: Kubernetes resource for non-sensitive configuration
- **Secret**: Kubernetes resource for sensitive configuration
- **Liveness Probe**: Health check to determine if pod should be restarted
- **Readiness Probe**: Health check to determine if pod can receive traffic
- **NodePort**: Service type that exposes port on all cluster nodes
- **ClusterIP**: Service type for internal cluster communication only
