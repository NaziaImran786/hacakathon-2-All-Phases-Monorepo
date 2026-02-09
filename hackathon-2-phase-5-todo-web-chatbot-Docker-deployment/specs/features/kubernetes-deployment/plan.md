# Implementation Plan: Local Kubernetes Deployment

**Feature**: kubernetes-deployment
**Branch**: feat/kubernetes-deployment
**Created**: 2026-01-02
**Status**: Planning
**Spec**: specs/features/kubernetes-deployment.md

---

## Executive Summary

This plan outlines the implementation strategy for containerizing and deploying the FlowTask application (FastAPI backend + Next.js frontend + PostgreSQL) to a local Kubernetes cluster using Minikube. The implementation follows a phased approach: research Docker and Kubernetes best practices, design containerization and orchestration architecture, create Dockerfiles and Kubernetes manifests, package with Helm charts, and deploy with comprehensive health checks and monitoring.

**Success Criteria:**
- All services deploy successfully to Minikube
- Frontend communicates with backend via Kubernetes service DNS
- Database persists data through pod restarts
- Health checks automatically recover from failures
- Helm charts enable parameterized deployments

---

## Technical Context

### Known Information

**Existing Application Stack:**
- **Backend**: FastAPI (Python 3.11) with Uvicorn server on port 8000
- **Frontend**: Next.js 14.1.0 with App Router on port 3000
- **Database**: Neon PostgreSQL (external) or local PostgreSQL 15
- **Dependencies**:
  - Backend: fastapi, uvicorn, sqlmodel, psycopg2-binary, python-jose, openai>=1.0.0, openai-agents==0.6.4, mcp==1.25.0
  - Frontend: react, next, framer-motion, lucide-react, jwt-decode, tailwindcss

**Environment Variables Required:**
- Backend: DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY
- Frontend: NEXT_PUBLIC_API_URL

**Current Deployment:**
- Backend runs via `uvicorn app:app --host 0.0.0.0 --port 8000`
- Frontend runs via `npm run dev` (dev) or `npm run build && npm start` (prod)
- Database connection via DATABASE_URL environment variable

### Unknowns (NEEDS CLARIFICATION)

1. **Multi-stage Build Optimization**: What are the optimal base images for minimal size and security? (python:3.11-slim vs alpine, node:20-alpine vs slim)
2. **Health Endpoint**: Does backend expose /health or / for health checks? Need to verify or create dedicated health endpoint
3. **Database Migration Strategy**: How should database migrations be handled during deployments? (initContainer, Job, manual)
4. **Image Registry**: Should images be built locally for Minikube or pushed to registry? (Minikube Docker daemon vs external registry)
5. **Persistent Volume**: What storage class should be used for PostgreSQL in Minikube? (standard, hostPath)
6. **Resource Limits**: What are appropriate CPU/memory requests and limits for each service based on actual usage?
7. **Rolling Update Strategy**: What maxUnavailable/maxSurge values ensure zero-downtime deployments?
8. **Secrets Management**: Should secrets be created imperatively via kubectl or declaratively via YAML (gitignored)?
9. **Service Mesh**: Is Istio or other service mesh needed for this phase, or simple ClusterIP services sufficient?
10. **Monitoring**: Should Prometheus/Grafana be deployed alongside application for observability?

---

## Constitution Check

### Alignment with Core Principles

✅ **I. Spec-Driven Development (SDD)**
- All infrastructure code will be generated from kubernetes-deployment.md specification
- No manual Dockerfile or manifest creation without spec reference

✅ **II. Standardized Tech Stack**
- Frontend: Next.js 16+ (currently 14.1.0, will maintain compatibility)
- Backend: Python FastAPI with SQLModel ORM
- Database: PostgreSQL (local StatefulSet or Neon external)

✅ **III. Monorepo Architecture**
- All Kubernetes manifests, Dockerfiles, and Helm charts will reside in monorepo
- Directory structure: /backend/Dockerfile, /frontend/Dockerfile, /k8s/, /helm/

✅ **IV. Secure Authentication (JWT)**
- JWT_SECRET_KEY will be stored as Kubernetes Secret
- Backend will continue to verify JWT tokens in all API requests

✅ **V. User Isolation & JWT Verification**
- No changes to backend logic; user isolation remains enforced at database query level

✅ **VI. AI Agents Development (Phase III)**
- OpenAI Agents SDK and MCP SDK dependencies will be included in backend Docker image
- OPENAI_API_KEY will be stored as Kubernetes Secret

✅ **VII. Stateless Architecture (Phase III)**
- Stateless backend design enables horizontal scaling in Kubernetes
- All conversation history persisted to PostgreSQL (StatefulSet with PVC)

### Constraints & Requirements Validation

✅ **No manual code writing**: All manifests generated from spec
✅ **Tech stack adherence**: Docker + Kubernetes + Helm following spec
✅ **Monorepo structure**: All artifacts in single repository
✅ **JWT authentication**: Secrets management via Kubernetes Secrets
✅ **Backend JWT verification**: No changes to existing auth flow
✅ **OpenAI Agents SDK + MCP SDK**: Included in backend container
✅ **Stateless server + Neon persistence**: Architecture preserved in containerized environment

---

## Phase 0: Research & Discovery

### Research Tasks

#### R-001: Docker Multi-Stage Build Best Practices
**Objective**: Determine optimal base images and build strategies for Python FastAPI and Node.js Next.js applications

**Questions:**
- Should we use python:3.11-slim, python:3.11-alpine, or distroless for backend?
- Should we use node:20-alpine, node:20-slim, or node:20 for frontend?
- What are the tradeoffs (image size, security, build time, compatibility)?

**Research Approach:**
- Review official Docker documentation for Python and Node.js
- Compare image sizes and security profiles
- Check compatibility with our dependencies (psycopg2-binary works on alpine?)

**Expected Outcome:**
- Decision matrix with base image recommendations
- Dockerfile templates for backend and frontend

---

#### R-002: Kubernetes Health Check Patterns
**Objective**: Design liveness, readiness, and startup probes for FastAPI and Next.js

**Questions:**
- Does FastAPI backend expose /health endpoint or should we use /?
- What HTTP status codes indicate healthy vs unhealthy state?
- What are appropriate initialDelaySeconds, periodSeconds, and failureThreshold values?
- Should probes check database connectivity or just process health?

**Research Approach:**
- Inspect backend/app.py for existing health endpoints
- Review Kubernetes probe best practices for web applications
- Test probe configurations in local environment

**Expected Outcome:**
- Health endpoint specifications for backend and frontend
- Probe configurations with justified timeout values

---

#### R-003: PostgreSQL StatefulSet Persistence Strategy
**Objective**: Determine how to configure persistent storage for PostgreSQL in Minikube

**Questions:**
- What storage class is available in Minikube (standard, hostPath)?
- Should we use volumeClaimTemplates in StatefulSet or separate PVC?
- How large should the PVC be (5Gi, 10Gi, 20Gi)?
- Should we use Neon external PostgreSQL or local PostgreSQL StatefulSet?

**Research Approach:**
- Query Minikube for available storage classes: `kubectl get storageclass`
- Review StatefulSet documentation for PVC patterns
- Estimate database size requirements based on Phase III usage

**Expected Outcome:**
- Storage class selection (standard recommended for Minikube)
- PVC size recommendation (10Gi for development)
- Decision: local StatefulSet vs Neon external

---

#### R-004: Database Migration Handling in Kubernetes
**Objective**: Determine strategy for running database migrations during deployments

**Questions:**
- Should migrations run as Kubernetes Job before deployment?
- Should migrations run as initContainer in backend pod?
- Should migrations be handled manually before deployment?
- Does SQLModel auto-create tables on startup (create_db_and_tables())?

**Research Approach:**
- Review backend/app.py startup logic: `@app.on_event("startup")`
- Review SQLModel documentation on table creation
- Evaluate Kubernetes Job vs initContainer patterns

**Expected Outcome:**
- Migration strategy recommendation (likely: SQLModel auto-creates on startup)
- Kubernetes manifest patterns if Job/initContainer needed

---

#### R-005: Helm Chart Structure and Templating
**Objective**: Design Helm chart structure for backend, frontend, and PostgreSQL

**Questions:**
- Should we use separate charts for backend, frontend, and PostgreSQL?
- Should we use umbrella chart with subcharts?
- What values should be parameterized (image.tag, replicas, resources)?
- Should we include ConfigMaps and Secrets in Helm charts or manage separately?

**Research Approach:**
- Review Helm best practices documentation
- Examine popular open-source Helm charts for web applications
- Evaluate templating strategies for multi-environment support

**Expected Outcome:**
- Helm chart directory structure
- values.yaml schema for each component
- _helpers.tpl template functions

---

#### R-006: Resource Requests and Limits Tuning
**Objective**: Determine appropriate CPU and memory allocations for each service

**Questions:**
- What are baseline resource requirements for FastAPI + Uvicorn?
- What are baseline resource requirements for Next.js production server?
- What are baseline resource requirements for PostgreSQL 15?
- Should we set requests = limits (guaranteed QoS) or requests < limits (burstable)?

**Research Approach:**
- Run load tests on existing deployment to measure resource usage
- Review Kubernetes resource management documentation
- Consult best practices for Python and Node.js applications

**Expected Outcome:**
- Resource requests/limits for backend (500m CPU, 512Mi memory recommended)
- Resource requests/limits for frontend (250m CPU, 256Mi memory recommended)
- Resource requests/limits for PostgreSQL (250m CPU, 256Mi memory recommended)

---

#### R-007: Secrets Management Best Practices
**Objective**: Determine secure approach for managing Kubernetes Secrets

**Questions:**
- Should secrets be created imperatively via `kubectl create secret`?
- Should secrets be defined in YAML files (base64 encoded, gitignored)?
- Should we use external secret managers (Sealed Secrets, External Secrets Operator)?
- How should secrets be rotated without downtime?

**Research Approach:**
- Review Kubernetes Secrets documentation and security best practices
- Evaluate gitignore patterns for secret files
- Research secret rotation strategies

**Expected Outcome:**
- Secrets creation workflow (imperative kubectl recommended for Phase IV)
- Documentation template for secret creation
- .gitignore patterns for k8s/secrets/ directory

---

#### R-008: Service Discovery and Networking
**Objective**: Design Kubernetes Service architecture for inter-service communication

**Questions:**
- Should all services use ClusterIP or should frontend use NodePort/LoadBalancer?
- How should frontend resolve backend service (http://backend-service:8000)?
- Should we implement Ingress controller for external access?
- What DNS naming convention should be used (service-name vs service-name.namespace.svc.cluster.local)?

**Research Approach:**
- Review Kubernetes Service types and use cases
- Test DNS resolution patterns in Minikube
- Evaluate Ingress vs NodePort for local development

**Expected Outcome:**
- Service type recommendations (ClusterIP for backend, NodePort for frontend)
- DNS naming convention (short name sufficient within same namespace)
- Network diagram showing service communication

---

#### R-009: Rolling Update Strategy
**Objective**: Define deployment strategy for zero-downtime updates

**Questions:**
- What maxUnavailable and maxSurge values prevent downtime?
- Should we use RollingUpdate or Recreate strategy?
- How many replicas should each service run (1, 2, 3)?
- Should we implement PodDisruptionBudget for high availability?

**Research Approach:**
- Review Kubernetes Deployment strategies documentation
- Calculate replica requirements based on availability targets
- Test rolling update scenarios in Minikube

**Expected Outcome:**
- Deployment strategy: RollingUpdate with maxUnavailable=0, maxSurge=1
- Replica recommendations: backend=3, frontend=2, postgres=1
- PodDisruptionBudget configurations (optional for Phase IV)

---

#### R-010: Image Build and Registry Strategy
**Objective**: Determine how to build and store Docker images for Kubernetes

**Questions:**
- Should we use Minikube's Docker daemon (`eval $(minikube docker-env)`)?
- Should we push images to Docker Hub, GitHub Container Registry, or local registry?
- How should image tags be managed (latest, git sha, semantic versioning)?
- Should we implement CI/CD for automated builds?

**Research Approach:**
- Review Minikube image management documentation
- Evaluate image registry options for local development
- Research tagging best practices

**Expected Outcome:**
- Image build workflow: Use Minikube Docker daemon for Phase IV
- Image pull policy: IfNotPresent (or Never for local builds)
- Tagging strategy: latest for development, git sha for production

---

### Research Consolidation (research.md)

**Output Location**: `specs/features/kubernetes-deployment/research.md`

**Structure:**
```markdown
# Research Findings: Kubernetes Deployment

## 1. Docker Multi-Stage Build Strategy
- **Decision**: [Base image selections]
- **Rationale**: [Why chosen]
- **Alternatives Considered**: [Other options]

## 2. Health Check Configuration
- **Decision**: [Probe settings]
- **Rationale**: [Why chosen]
- **Alternatives Considered**: [Other options]

[... continue for all 10 research tasks ...]
```

---

## Phase 1: Design & Contracts

### 1.1 Data Model Design

**Output Location**: `specs/features/kubernetes-deployment/data-model.md`

#### Infrastructure Entities

**Docker Images:**
```yaml
Entity: BackendDockerImage
Attributes:
  - base_image: python:3.11-slim
  - working_dir: /app
  - exposed_port: 8000
  - entry_point: ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
  - size_limit: < 500MB
  - user: non-root (UID 1000)

Entity: FrontendDockerImage
Attributes:
  - base_image: node:20-alpine
  - working_dir: /app
  - exposed_port: 3000
  - entry_point: ["npm", "start"]
  - size_limit: < 300MB
  - user: non-root (UID 1000)
```

**Kubernetes Resources:**
```yaml
Entity: BackendDeployment
Attributes:
  - name: backend
  - replicas: 3
  - selector: app=backend
  - strategy: RollingUpdate (maxUnavailable=0, maxSurge=1)
  - containers:
      - image: backend:latest
      - ports: [8000]
      - env: [DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY]
      - resources:
          requests: {cpu: 500m, memory: 512Mi}
          limits: {cpu: 1000m, memory: 1Gi}
  - probes:
      livenessProbe: {path: /, port: 8000, initialDelaySeconds: 30}
      readinessProbe: {path: /, port: 8000, initialDelaySeconds: 5}

Entity: FrontendDeployment
Attributes:
  - name: frontend
  - replicas: 2
  - selector: app=frontend
  - strategy: RollingUpdate (maxUnavailable=0, maxSurge=1)
  - containers:
      - image: frontend:latest
      - ports: [3000]
      - env: [NEXT_PUBLIC_API_URL]
      - resources:
          requests: {cpu: 250m, memory: 256Mi}
          limits: {cpu: 500m, memory: 512Mi}
  - probes:
      livenessProbe: {path: /, port: 3000, initialDelaySeconds: 30}
      readinessProbe: {path: /, port: 3000, initialDelaySeconds: 10}

Entity: PostgresStatefulSet
Attributes:
  - name: postgres
  - replicas: 1
  - selector: app=postgres
  - serviceName: postgres-service
  - volumeClaimTemplates:
      - name: postgres-storage
      - size: 10Gi
      - accessModes: [ReadWriteOnce]
  - containers:
      - image: postgres:15-alpine
      - ports: [5432]
      - env: [POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB]
      - volumeMounts: [{name: postgres-storage, mountPath: /var/lib/postgresql/data}]
      - resources:
          requests: {cpu: 250m, memory: 256Mi}
          limits: {cpu: 500m, memory: 512Mi}
```

**Services:**
```yaml
Entity: BackendService
Attributes:
  - name: backend-service
  - type: ClusterIP
  - selector: app=backend
  - ports: [{protocol: TCP, port: 8000, targetPort: 8000}]

Entity: FrontendService
Attributes:
  - name: frontend-service
  - type: NodePort
  - selector: app=frontend
  - ports: [{protocol: TCP, port: 3000, targetPort: 3000, nodePort: 30000}]

Entity: PostgresService
Attributes:
  - name: postgres-service
  - type: ClusterIP
  - selector: app=postgres
  - ports: [{protocol: TCP, port: 5432, targetPort: 5432}]
```

**Secrets:**
```yaml
Entity: AppSecrets
Attributes:
  - name: app-secrets
  - type: Opaque
  - data:
      database-url: <base64-encoded>
      jwt-secret: <base64-encoded>
      openai-api-key: <base64-encoded>

Entity: PostgresSecret
Attributes:
  - name: postgres-secret
  - type: Opaque
  - data:
      password: <base64-encoded>
```

---

### 1.2 Infrastructure Contracts

**Output Location**: `specs/features/kubernetes-deployment/contracts/`

#### Docker Build Contracts

**backend/Dockerfile:**
```dockerfile
# Contract: Multi-stage build producing <500MB image
# Stage 1: Builder
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
RUN useradd -m -u 1000 appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY . .
RUN chown -R appuser:appuser /app
USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**frontend/Dockerfile:**
```dockerfile
# Contract: Multi-stage build producing <300MB image
# Stage 1: Dependencies
FROM node:20-alpine as deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Stage 2: Builder
FROM node:20-alpine as builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Runtime
FROM node:20-alpine
WORKDIR /app
RUN addgroup -g 1000 appuser && adduser -D -u 1000 -G appuser appuser
COPY --from=deps /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 3000
CMD ["npm", "start"]
```

---

#### Kubernetes Manifest Contracts

**k8s/backend/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  labels:
    app: backend
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
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
        imagePullPolicy: IfNotPresent
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
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          failureThreshold: 3
```

**k8s/backend/service.yaml:**
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

**k8s/frontend/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  labels:
    app: frontend
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 0
      maxSurge: 1
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
        imagePullPolicy: IfNotPresent
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
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
          failureThreshold: 3
```

**k8s/frontend/service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
spec:
  type: NodePort
  selector:
    app: frontend
  ports:
  - protocol: TCP
    port: 3000
    targetPort: 3000
    nodePort: 30000
```

**k8s/postgres/statefulset.yaml:**
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
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
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

**k8s/postgres/service.yaml:**
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

---

#### Helm Chart Contracts

**helm/backend/Chart.yaml:**
```yaml
apiVersion: v2
name: backend
description: FlowTask Backend Helm Chart
type: application
version: 1.0.0
appVersion: "1.0.0"
```

**helm/backend/values.yaml:**
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

secrets:
  databaseUrl: "postgresql://todouser:password@postgres-service:5432/tododb"
  jwtSecret: "your-secret-key"
  openaiApiKey: "sk-..."

healthCheck:
  liveness:
    path: /
    port: 8000
    initialDelaySeconds: 30
    periodSeconds: 10
  readiness:
    path: /
    port: 8000
    initialDelaySeconds: 5
    periodSeconds: 5

strategy:
  type: RollingUpdate
  rollingUpdate:
    maxUnavailable: 0
    maxSurge: 1
```

**helm/backend/templates/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Chart.Name }}
  labels:
    app: {{ .Chart.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
  strategy:
    type: {{ .Values.strategy.type }}
    rollingUpdate:
      maxUnavailable: {{ .Values.strategy.rollingUpdate.maxUnavailable }}
      maxSurge: {{ .Values.strategy.rollingUpdate.maxSurge }}
  selector:
    matchLabels:
      app: {{ .Chart.Name }}
  template:
    metadata:
      labels:
        app: {{ .Chart.Name }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - containerPort: {{ .Values.service.port }}
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
            cpu: {{ .Values.resources.requests.cpu }}
            memory: {{ .Values.resources.requests.memory }}
          limits:
            cpu: {{ .Values.resources.limits.cpu }}
            memory: {{ .Values.resources.limits.memory }}
        livenessProbe:
          httpGet:
            path: {{ .Values.healthCheck.liveness.path }}
            port: {{ .Values.healthCheck.liveness.port }}
          initialDelaySeconds: {{ .Values.healthCheck.liveness.initialDelaySeconds }}
          periodSeconds: {{ .Values.healthCheck.liveness.periodSeconds }}
        readinessProbe:
          httpGet:
            path: {{ .Values.healthCheck.readiness.path }}
            port: {{ .Values.healthCheck.readiness.port }}
          initialDelaySeconds: {{ .Values.healthCheck.readiness.initialDelaySeconds }}
          periodSeconds: {{ .Values.healthCheck.readiness.periodSeconds }}
```

---

### 1.3 Quick Start Guide

**Output Location**: `specs/features/kubernetes-deployment/quickstart.md`

```markdown
# Quick Start: Kubernetes Deployment

## Prerequisites
- Minikube installed
- kubectl installed
- Helm 3.x installed
- Docker installed

## Step 1: Start Minikube
```bash
minikube start --driver=docker --cpus=4 --memory=8192
```

## Step 2: Build Docker Images
```bash
eval $(minikube docker-env)
cd backend && docker build -t backend:latest .
cd ../frontend && docker build -t frontend:latest .
```

## Step 3: Create Secrets
```bash
kubectl create secret generic app-secrets \
  --from-literal=database-url='postgresql://todouser:password@postgres-service:5432/tododb' \
  --from-literal=jwt-secret='your-secret-key' \
  --from-literal=openai-api-key='sk-...'

kubectl create secret generic postgres-secret \
  --from-literal=password='securepassword123'
```

## Step 4: Deploy with Helm
```bash
helm install postgres ./helm/postgres
helm install backend ./helm/backend
helm install frontend ./helm/frontend
```

## Step 5: Verify Deployment
```bash
kubectl get pods
kubectl get services
```

## Step 6: Access Application
```bash
minikube ip  # Get IP address
# Navigate to http://<minikube-ip>:30000
```
```

---

### 1.4 Agent Context Update

**Action**: Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`

**Expected Updates to CLAUDE.md:**
- Add Docker containerization technology
- Add Kubernetes orchestration platform
- Add Helm package manager
- Add Minikube local development cluster
- Preserve existing Phase III (OpenAI Agents SDK, MCP SDK) context

---

## Phase 2: Implementation Strategy

### Implementation Phases

#### Phase 2.1: Docker Containerization
**Objective**: Create optimized Docker images for backend and frontend

**Tasks:**
1. Create backend/Dockerfile with multi-stage build
2. Create backend/.dockerignore to exclude unnecessary files
3. Create frontend/Dockerfile with multi-stage build
4. Create frontend/.dockerignore
5. Build images locally and verify size constraints (<500MB backend, <300MB frontend)
6. Test images locally before Kubernetes deployment

**Acceptance Criteria:**
- ✅ Images build without errors
- ✅ Backend image < 500MB
- ✅ Frontend image < 300MB
- ✅ Images run as non-root users
- ✅ Environment variables correctly injected

---

#### Phase 2.2: Kubernetes Manifests
**Objective**: Create Kubernetes resource definitions for all components

**Tasks:**
1. Create k8s/backend/ directory with deployment.yaml, service.yaml
2. Create k8s/frontend/ directory with deployment.yaml, service.yaml
3. Create k8s/postgres/ directory with statefulset.yaml, service.yaml
4. Create k8s/secrets/ directory with secret templates (gitignored)
5. Configure resource requests/limits for all pods
6. Configure liveness and readiness probes
7. Configure rolling update strategies

**Acceptance Criteria:**
- ✅ All manifests validate with `kubectl apply --dry-run=client`
- ✅ Resource limits prevent excessive consumption
- ✅ Health probes configured correctly
- ✅ Services use appropriate types (ClusterIP, NodePort)

---

#### Phase 2.3: Helm Charts
**Objective**: Package manifests as templated, versioned Helm charts

**Tasks:**
1. Create helm/backend/ with Chart.yaml, values.yaml, templates/
2. Create helm/frontend/ with Chart.yaml, values.yaml, templates/
3. Create helm/postgres/ with Chart.yaml, values.yaml, templates/
4. Implement template helpers in _helpers.tpl
5. Parameterize image tags, replica counts, resource limits
6. Validate charts with `helm lint` and `helm template`

**Acceptance Criteria:**
- ✅ Helm charts lint without errors
- ✅ Template rendering produces valid Kubernetes YAML
- ✅ Values can be overridden per environment
- ✅ Charts install and uninstall cleanly

---

#### Phase 2.4: Minikube Deployment
**Objective**: Deploy all components to local Minikube cluster

**Tasks:**
1. Start Minikube with sufficient resources
2. Configure Docker to use Minikube daemon
3. Build images in Minikube context
4. Create secrets imperatively
5. Deploy PostgreSQL StatefulSet first
6. Deploy backend Deployment after database is ready
7. Deploy frontend Deployment after backend is ready
8. Verify pod status and logs
9. Test service connectivity

**Acceptance Criteria:**
- ✅ All pods reach Running state
- ✅ Frontend can communicate with backend via service DNS
- ✅ Backend can connect to PostgreSQL
- ✅ Health checks pass for all services
- ✅ Application accessible via NodePort

---

#### Phase 2.5: End-to-End Testing
**Objective**: Verify full application functionality in Kubernetes

**Tasks:**
1. Access frontend via Minikube IP and NodePort
2. Test user registration and login
3. Test task CRUD operations
4. Test AI chatbot functionality
5. Test data persistence (delete postgres pod, verify data survives)
6. Test rolling updates (update image, verify zero downtime)
7. Test pod failure recovery (delete pod, verify automatic restart)

**Acceptance Criteria:**
- ✅ User can register and login
- ✅ Tasks can be created, read, updated, deleted
- ✅ AI chatbot responds to natural language commands
- ✅ Data persists through pod restarts
- ✅ Rolling updates complete without downtime
- ✅ Failed pods are automatically replaced

---

#### Phase 2.6: Documentation
**Objective**: Create comprehensive deployment documentation

**Tasks:**
1. Create README-k8s.md with deployment instructions
2. Document troubleshooting guide for common issues
3. Document secrets creation workflow
4. Document image build process
5. Document Helm chart usage
6. Create architecture diagrams

**Acceptance Criteria:**
- ✅ Documentation covers all deployment steps
- ✅ Troubleshooting guide addresses common errors
- ✅ Secrets management documented securely
- ✅ Diagrams illustrate system architecture

---

## Risk Analysis & Mitigation

### High Priority Risks

**R-001: Image Build Failures**
- **Impact**: High - Blocks deployment
- **Probability**: Medium - Dependency conflicts
- **Mitigation**: Use multi-stage builds, test builds locally before CI/CD
- **Contingency**: Maintain working base image versions

**R-002: Database Connection Failures**
- **Impact**: High - Application non-functional
- **Probability**: Low - StatefulSet ensures stable endpoints
- **Mitigation**: Implement retry logic, verify DATABASE_URL format
- **Contingency**: Use external Neon PostgreSQL as fallback

**R-003: Secret Exposure**
- **Impact**: Critical - Security breach
- **Probability**: Low - If secrets committed to git
- **Mitigation**: Add k8s/secrets/ to .gitignore, use imperative secret creation
- **Contingency**: Rotate secrets immediately if exposed

### Medium Priority Risks

**R-004: Resource Exhaustion**
- **Impact**: Medium - Pods evicted or OOMKilled
- **Probability**: Medium - If limits too low
- **Mitigation**: Set appropriate requests/limits based on profiling
- **Contingency**: Increase cluster resources, tune limits

**R-005: Health Check False Positives**
- **Impact**: Medium - Unnecessary pod restarts
- **Probability**: Medium - If probes too aggressive
- **Mitigation**: Tune initialDelaySeconds and failureThreshold
- **Contingency**: Adjust probe configurations based on logs

**R-006: Service Discovery Failures**
- **Impact**: Medium - Inter-service communication broken
- **Probability**: Low - Kubernetes DNS reliable
- **Mitigation**: Use standard service naming, verify with nslookup
- **Contingency**: Use ClusterIP addresses directly as fallback

---

## Success Metrics

### Deployment Success
- ✅ All pods reach Running state within 2 minutes
- ✅ Health checks pass within 30 seconds of pod readiness
- ✅ Zero deployment errors during `kubectl apply` or `helm install`

### Performance
- ✅ Backend response time < 500ms for API requests
- ✅ Frontend page load time < 2 seconds
- ✅ Database query time < 100ms

### Reliability
- ✅ Pods survive node restarts (StatefulSet ensures data persistence)
- ✅ Rolling updates complete without 5xx errors
- ✅ Failed pods are replaced within 30 seconds

### Security
- ✅ All containers run as non-root users
- ✅ Secrets are not committed to version control
- ✅ Network policies restrict unnecessary traffic (future enhancement)

---

## Post-Phase 2 Re-evaluation

### Constitution Check (Post-Design)

✅ **All core principles maintained**:
- Spec-driven approach followed throughout planning
- Tech stack preserved (Next.js, FastAPI, PostgreSQL)
- Monorepo structure maintained with new /k8s and /helm directories
- JWT authentication unchanged
- User isolation enforced at database level
- OpenAI Agents SDK + MCP SDK containerized correctly
- Stateless architecture enables Kubernetes horizontal scaling

✅ **No new violations introduced**:
- All design decisions align with constitution
- Security best practices applied (non-root users, secrets management)
- No manual code writing during planning phase

---

## Appendix A: Directory Structure

```
hackathon-2-phase-4-todo-web-chatbot/
├── backend/
│   ├── Dockerfile                    # Multi-stage build for FastAPI
│   ├── .dockerignore                 # Exclude venv, __pycache__, .env
│   └── ...
├── frontend/
│   ├── Dockerfile                    # Multi-stage build for Next.js
│   ├── .dockerignore                 # Exclude node_modules, .next
│   └── ...
├── k8s/
│   ├── backend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── postgres/
│   │   ├── statefulset.yaml
│   │   └── service.yaml
│   └── secrets/                      # .gitignore this directory
│       ├── app-secrets.yaml.example
│       └── postgres-secret.yaml.example
├── helm/
│   ├── backend/
│   │   ├── Chart.yaml
│   │   ├── values.yaml
│   │   └── templates/
│   │       ├── deployment.yaml
│   │       ├── service.yaml
│   │       ├── secret.yaml
│   │       └── _helpers.tpl
│   ├── frontend/
│   │   └── ...
│   └── postgres/
│       └── ...
├── scripts/
│   ├── build-images.sh               # Automate image builds
│   ├── deploy-all.sh                 # Automate Helm deployments
│   └── cleanup.sh                    # Cleanup resources
├── specs/
│   └── features/
│       └── kubernetes-deployment/
│           ├── plan.md               # This file
│           ├── research.md           # Research findings
│           ├── data-model.md         # Infrastructure entities
│           ├── quickstart.md         # Deployment guide
│           └── contracts/
│               ├── backend-dockerfile.md
│               ├── frontend-dockerfile.md
│               └── kubernetes-manifests.md
└── README-k8s.md                     # Main documentation
```

---

## Appendix B: Validation Checklist

### Pre-Implementation Checklist
- [ ] All research tasks completed and documented in research.md
- [ ] Data model reviewed and approved
- [ ] Contracts validated against spec requirements
- [ ] Constitution check passed
- [ ] Quick start guide reviewed

### Implementation Checklist
- [ ] Dockerfiles created and tested
- [ ] Kubernetes manifests created and validated
- [ ] Helm charts created and linted
- [ ] Secrets created securely
- [ ] All services deployed to Minikube
- [ ] End-to-end tests passed
- [ ] Documentation completed

### Post-Implementation Checklist
- [ ] Performance benchmarks meet targets
- [ ] Security audit passed
- [ ] No secrets committed to git
- [ ] All pods running with non-root users
- [ ] Monitoring and logging configured (future)

---

## Next Steps

After plan approval:

1. **Execute Research Phase (Phase 0)**:
   - Run all 10 research tasks
   - Consolidate findings in research.md
   - Resolve all NEEDS CLARIFICATION items

2. **Generate Tasks (/sp.tasks)**:
   - Convert plan into actionable tasks
   - Order tasks by dependencies
   - Assign test cases to each task

3. **Begin Implementation**:
   - Start with Docker containerization
   - Progress through Kubernetes manifests
   - Deploy to Minikube
   - Validate end-to-end functionality

---

**Plan Status**: Ready for Approval
**Next Command**: `/sp.tasks` to generate task list
**Estimated Complexity**: High (containerization + orchestration + Helm)
**Estimated Tasks**: 40-50 granular tasks across 6 implementation phases
