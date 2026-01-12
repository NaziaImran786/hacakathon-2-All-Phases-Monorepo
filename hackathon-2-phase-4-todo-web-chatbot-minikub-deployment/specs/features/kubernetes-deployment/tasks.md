# Implementation Tasks: Local Kubernetes Deployment

**Feature**: kubernetes-deployment
**Branch**: feat/kubernetes-deployment
**Created**: 2026-01-02
**Spec**: specs/features/kubernetes-deployment.md
**Plan**: specs/features/kubernetes-deployment/plan.md

---

## Overview

This document contains the complete task list for implementing Phase IV: Local Kubernetes Deployment. Tasks are organized by user story to enable independent, incremental delivery. Each user story can be developed and tested independently once foundational tasks are complete.

**Total Estimated Tasks**: 52 tasks across 10 phases
**MVP Scope**: User Story 1 (Backend Deployment) + User Story 3 (Database Persistence) + User Story 5 (Secrets Management)
**Independent Test Criteria**: Each user story phase includes specific validation steps

---

## Task Legend

- `[P]` = Parallelizable (can run concurrently with other [P] tasks in same phase)
- `[US#]` = User Story number (from spec.md)
- Task IDs: T001-T052 in dependency order

---

## Phase 1: Project Setup & Prerequisites

**Goal**: Initialize project structure and verify prerequisites

**Dependencies**: None (start here)

**Tasks**:

- [ ] T001 Verify Minikube installation (`minikube version` outputs v1.28+)
- [ ] T002 Verify kubectl installation (`kubectl version --client` outputs v1.28+)
- [ ] T003 Verify Helm installation (`helm version` outputs v3+)
- [ ] T004 Verify Docker installation (`docker --version` outputs 24+)
- [ ] T005 Start Minikube cluster with `minikube start --driver=docker --cpus=4 --memory=8192`
- [ ] T006 Verify Minikube cluster status (`minikube status` shows Running)
- [ ] T007 Configure Docker to use Minikube daemon (`eval $(minikube docker-env)`)
- [ ] T008 Create k8s/ directory structure: k8s/backend/, k8s/frontend/, k8s/postgres/, k8s/secrets/
- [ ] T009 Create helm/ directory structure: helm/backend/, helm/frontend/, helm/postgres/
- [ ] T010 Create scripts/ directory for automation: scripts/build-images.sh, scripts/deploy-all.sh, scripts/cleanup.sh
- [ ] T011 Add k8s/secrets/ to .gitignore to prevent secret exposure
- [ ] T012 Create README-k8s.md placeholder for deployment documentation

**Validation**:
```bash
# All prerequisites installed
minikube status
kubectl get nodes
helm version

# Directory structure created
ls -la k8s/ helm/ scripts/
```

---

## Phase 2: Foundational Tasks

**Goal**: Set up core infrastructure that blocks all user stories

**Dependencies**: Phase 1 complete

**Tasks**:

- [ ] T013 Query Minikube storage classes (`kubectl get storageclass`) to identify available storage
- [ ] T014 Create k8s/secrets/app-secrets.yaml.example with placeholder values for DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY
- [ ] T015 Create k8s/secrets/postgres-secret.yaml.example with placeholder POSTGRES_PASSWORD
- [ ] T016 Document secret creation process in README-k8s.md (imperative kubectl create secret commands)
- [ ] T017 [P] Create backend/.dockerignore excluding .venv, __pycache__/, *.pyc, .env, .git
- [ ] T018 [P] Create frontend/.dockerignore excluding node_modules/, .next/, .git, *.log

**Validation**:
```bash
# Storage class identified
kubectl get storageclass

# Secret templates created
ls k8s/secrets/*.example

# Dockerignore files created
cat backend/.dockerignore frontend/.dockerignore
```

---

## Phase 3: User Story 1 - Deploy Backend to Kubernetes (P1)

**Goal**: Containerize and deploy FastAPI backend to Kubernetes

**Independent Test**: Backend pod runs, health endpoint accessible, connects to database

**Dependencies**: Phase 2 complete

**Story Dependencies**: User Story 3 (database must exist), User Story 5 (secrets must exist)

### US1: Docker Containerization

- [ ] T019 [US1] Create backend/Dockerfile with multi-stage build (builder + runtime stages)
- [ ] T020 [US1] Set Dockerfile base image to python:3.11-slim for compatibility with psycopg2-binary
- [ ] T021 [US1] Configure Dockerfile to create non-root user (UID 1000) and run as appuser
- [ ] T022 [US1] Set Dockerfile WORKDIR to /app and EXPOSE port 8000
- [ ] T023 [US1] Add Dockerfile CMD: `["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]`
- [ ] T024 [US1] Build backend Docker image: `docker build -t backend:latest ./backend`
- [ ] T025 [US1] Verify backend image size is < 500MB (`docker images backend:latest`)
- [ ] T026 [US1] Test backend image locally: `docker run -p 8000:8000 -e DATABASE_URL=... backend:latest`

**Validation**:
```bash
# Image built successfully
docker images | grep backend

# Image size acceptable
docker images backend:latest --format "{{.Size}}"

# Container runs and responds
docker run -d --name test-backend -p 8000:8000 backend:latest
curl http://localhost:8000/
docker rm -f test-backend
```

### US1: Kubernetes Manifests

- [ ] T027 [US1] Create k8s/backend/deployment.yaml with 3 replicas, RollingUpdate strategy (maxUnavailable=0, maxSurge=1)
- [ ] T028 [US1] Configure deployment to reference backend:latest with imagePullPolicy: IfNotPresent
- [ ] T029 [US1] Add environment variables from secrets (DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY) via secretKeyRef
- [ ] T030 [US1] Configure resource requests (500m CPU, 512Mi memory) and limits (1000m CPU, 1Gi memory)
- [ ] T031 [US1] Add livenessProbe (httpGet / on port 8000, initialDelaySeconds: 30, periodSeconds: 10, failureThreshold: 3)
- [ ] T032 [US1] Add readinessProbe (httpGet / on port 8000, initialDelaySeconds: 5, periodSeconds: 5, failureThreshold: 3)
- [ ] T033 [US1] Create k8s/backend/service.yaml with type ClusterIP exposing port 8000 to targetPort 8000
- [ ] T034 [US1] Set service selector to app: backend

**Validation**:
```bash
# Manifests validate
kubectl apply --dry-run=client -f k8s/backend/

# Verify YAML structure
kubectl explain deployment.spec.template.spec.containers.resources
```

### US1: Deployment & Testing

- [ ] T035 [US1] Apply backend deployment: `kubectl apply -f k8s/backend/deployment.yaml`
- [ ] T036 [US1] Apply backend service: `kubectl apply -f k8s/backend/service.yaml`
- [ ] T037 [US1] Verify backend pods reach Running state: `kubectl get pods -l app=backend`
- [ ] T038 [US1] Check backend logs for startup success: `kubectl logs -l app=backend --tail=50`
- [ ] T039 [US1] Port-forward backend service: `kubectl port-forward service/backend-service 8000:8000`
- [ ] T040 [US1] Test backend health endpoint: `curl http://localhost:8000/` returns 200 OK
- [ ] T041 [US1] Verify environment variables mounted: `kubectl exec -it <backend-pod> -- env | grep DATABASE_URL`

**Independent Test Criteria**:
```bash
# All acceptance scenarios from spec
✅ Backend Dockerfile builds successfully
✅ Backend image < 500MB
✅ Backend pod in Running state
✅ Health endpoint returns 200 OK
✅ Secrets mounted correctly
✅ Database connection successful
```

---

## Phase 4: User Story 2 - Deploy Frontend to Kubernetes (P1)

**Goal**: Containerize and deploy Next.js frontend to Kubernetes

**Independent Test**: Frontend pod runs, UI accessible, communicates with backend

**Dependencies**: Phase 2 complete, User Story 4 (service discovery)

**Story Dependencies**: User Story 1 (backend must exist), User Story 4 (backend service must exist)

### US2: Docker Containerization

- [ ] T042 [US2] Create frontend/Dockerfile with multi-stage build (deps + builder + runtime stages)
- [ ] T043 [US2] Set Dockerfile base image to node:20-alpine for minimal size
- [ ] T044 [US2] Configure Dockerfile to create non-root user (UID 1000) and run as appuser
- [ ] T045 [US2] Add stage 1: Install production dependencies with `npm ci --only=production`
- [ ] T046 [US2] Add stage 2: Run `npm run build` to create optimized Next.js production build
- [ ] T047 [US2] Add stage 3: Copy node_modules, .next/, public/, package.json to runtime stage
- [ ] T048 [US2] Set Dockerfile WORKDIR to /app, EXPOSE port 3000, CMD: `["npm", "start"]`
- [ ] T049 [US2] Build frontend Docker image: `docker build -t frontend:latest ./frontend`
- [ ] T050 [US2] Verify frontend image size is < 300MB (`docker images frontend:latest`)
- [ ] T051 [US2] Test frontend image locally: `docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000 frontend:latest`

**Validation**:
```bash
# Image built successfully
docker images | grep frontend

# Image size acceptable
docker images frontend:latest --format "{{.Size}}"

# Container runs and serves pages
docker run -d --name test-frontend -p 3000:3000 frontend:latest
curl http://localhost:3000/
docker rm -f test-frontend
```

### US2: Kubernetes Manifests

- [ ] T052 [US2] Create k8s/frontend/deployment.yaml with 2 replicas, RollingUpdate strategy (maxUnavailable=0, maxSurge=1)
- [ ] T053 [US2] Configure deployment to reference frontend:latest with imagePullPolicy: IfNotPresent
- [ ] T054 [US2] Add environment variable NEXT_PUBLIC_API_URL=http://backend-service:8000
- [ ] T055 [US2] Configure resource requests (250m CPU, 256Mi memory) and limits (500m CPU, 512Mi memory)
- [ ] T056 [US2] Add livenessProbe (httpGet / on port 3000, initialDelaySeconds: 30, periodSeconds: 10, failureThreshold: 3)
- [ ] T057 [US2] Add readinessProbe (httpGet / on port 3000, initialDelaySeconds: 10, periodSeconds: 5, failureThreshold: 3)
- [ ] T058 [US2] Create k8s/frontend/service.yaml with type NodePort exposing port 3000, nodePort: 30000
- [ ] T059 [US2] Set service selector to app: frontend

**Validation**:
```bash
# Manifests validate
kubectl apply --dry-run=client -f k8s/frontend/

# Verify NodePort configuration
grep nodePort k8s/frontend/service.yaml
```

### US2: Deployment & Testing

- [ ] T060 [US2] Apply frontend deployment: `kubectl apply -f k8s/frontend/deployment.yaml`
- [ ] T061 [US2] Apply frontend service: `kubectl apply -f k8s/frontend/service.yaml`
- [ ] T062 [US2] Verify frontend pods reach Running state: `kubectl get pods -l app=frontend`
- [ ] T063 [US2] Check frontend logs for startup success: `kubectl logs -l app=frontend --tail=50`
- [ ] T064 [US2] Get Minikube IP: `minikube ip`
- [ ] T065 [US2] Access frontend via NodePort: Navigate to `http://<minikube-ip>:30000`
- [ ] T066 [US2] Verify login page displays correctly in browser
- [ ] T067 [US2] Test user authentication flow (register + login) and verify JWT token issuance

**Independent Test Criteria**:
```bash
# All acceptance scenarios from spec
✅ Frontend Dockerfile builds successfully
✅ Frontend image < 300MB
✅ Frontend pod in Running state
✅ Login page accessible via browser
✅ NEXT_PUBLIC_API_URL points to backend service
✅ User can authenticate and receive JWT token
```

---

## Phase 5: User Story 3 - Configure Database Persistence (P1)

**Goal**: Deploy PostgreSQL StatefulSet with persistent storage

**Independent Test**: Database survives pod deletion, data persists

**Dependencies**: Phase 2 complete

**Story Dependencies**: None (foundational for US1)

### US3: PostgreSQL StatefulSet

- [ ] T068 [US3] Create k8s/postgres/statefulset.yaml with serviceName: postgres-service, replicas: 1
- [ ] T069 [US3] Configure StatefulSet to use postgres:15-alpine image
- [ ] T070 [US3] Add environment variables: POSTGRES_USER=todouser, POSTGRES_DB=tododb, PGDATA=/var/lib/postgresql/data/pgdata
- [ ] T071 [US3] Add POSTGRES_PASSWORD from secret via secretKeyRef (postgres-secret.password)
- [ ] T072 [US3] Configure volumeMount for postgres-storage to /var/lib/postgresql/data
- [ ] T073 [US3] Add volumeClaimTemplate: postgres-storage with 10Gi, accessModes: [ReadWriteOnce]
- [ ] T074 [US3] Configure resource requests (250m CPU, 256Mi memory) and limits (500m CPU, 512Mi memory)
- [ ] T075 [US3] Create k8s/postgres/service.yaml with type ClusterIP, port 5432, selector: app=postgres

**Validation**:
```bash
# Manifests validate
kubectl apply --dry-run=client -f k8s/postgres/

# Verify volumeClaimTemplate
kubectl explain statefulset.spec.volumeClaimTemplates
```

### US3: Secret Creation

- [ ] T076 [US3] Create postgres-secret imperatively: `kubectl create secret generic postgres-secret --from-literal=password='securepassword123'`
- [ ] T077 [US3] Verify secret created: `kubectl get secret postgres-secret -o yaml | grep password:`

**Validation**:
```bash
# Secret exists and base64 encoded
kubectl get secrets | grep postgres
kubectl describe secret postgres-secret
```

### US3: Deployment & Testing

- [ ] T078 [US3] Apply postgres statefulset: `kubectl apply -f k8s/postgres/statefulset.yaml`
- [ ] T079 [US3] Apply postgres service: `kubectl apply -f k8s/postgres/service.yaml`
- [ ] T080 [US3] Verify postgres pod reaches Running state: `kubectl get pods -l app=postgres`
- [ ] T081 [US3] Verify PVC is bound: `kubectl get pvc` shows postgres-storage-postgres-0 as Bound
- [ ] T082 [US3] Verify PVC size: `kubectl describe pvc postgres-storage-postgres-0 | grep Capacity`
- [ ] T083 [US3] Test database connection from backend pod: `kubectl exec -it <backend-pod> -- python -c "from sqlmodel import create_engine; create_engine('postgresql://todouser:securepassword123@postgres-service:5432/tododb').connect()"`
- [ ] T084 [US3] Create test data: Insert task via backend API
- [ ] T085 [US3] Delete postgres pod: `kubectl delete pod postgres-0`
- [ ] T086 [US3] Wait for pod recreation: `kubectl get pods -l app=postgres -w`
- [ ] T087 [US3] Verify test data still exists: Query task via backend API

**Independent Test Criteria**:
```bash
# All acceptance scenarios from spec
✅ PVC created and bound to /var/lib/postgresql/data
✅ Data persists after pod deletion
✅ Backend connects using credentials from secret
✅ Tables (users, tasks, conversations, messages) created on startup
```

---

## Phase 6: User Story 4 - Implement Service Discovery (P1)

**Goal**: Verify Kubernetes service discovery and inter-service communication

**Independent Test**: Frontend can communicate with backend via service DNS

**Dependencies**: User Story 1 (backend deployed), User Story 2 (frontend deployed)

### US4: Service Discovery Validation

- [ ] T088 [US4] Verify backend service endpoints: `kubectl get endpoints backend-service`
- [ ] T089 [US4] Verify frontend service endpoints: `kubectl get endpoints frontend-service`
- [ ] T090 [US4] Test DNS resolution from frontend pod: `kubectl exec -it <frontend-pod> -- nslookup backend-service`
- [ ] T091 [US4] Test connectivity from frontend to backend: `kubectl exec -it <frontend-pod> -- wget -O- http://backend-service:8000/`
- [ ] T092 [US4] Verify NEXT_PUBLIC_API_URL in frontend pod: `kubectl exec -it <frontend-pod> -- env | grep NEXT_PUBLIC_API_URL`
- [ ] T093 [US4] Test API call from browser: Open frontend in browser, open DevTools Network tab, verify requests to backend-service succeed
- [ ] T094 [US4] Test load balancing: Scale backend to 3 replicas, make multiple requests, verify load distribution via logs

**Independent Test Criteria**:
```bash
# All acceptance scenarios from spec
✅ backend-service.default.svc.cluster.local resolves to backend pod IP
✅ Frontend successfully routes API calls to backend
✅ Load is balanced across multiple backend replicas
✅ Backend service is ClusterIP (internal only)
```

---

## Phase 7: User Story 5 - Manage Secrets Securely (P1)

**Goal**: Store sensitive configuration in Kubernetes Secrets

**Independent Test**: Secrets are mounted correctly, not exposed in git

**Dependencies**: Phase 2 complete (foundational for US1, US3)

### US5: Application Secrets

- [ ] T095 [US5] Create app-secrets imperatively with DATABASE_URL: `kubectl create secret generic app-secrets --from-literal=database-url='postgresql://todouser:securepassword123@postgres-service:5432/tododb' --from-literal=jwt-secret='your-secret-key-change-in-production' --from-literal=openai-api-key='sk-your-openai-key-here'`
- [ ] T096 [US5] Verify app-secrets created: `kubectl get secret app-secrets`
- [ ] T097 [US5] Verify secret keys exist: `kubectl describe secret app-secrets | grep -E 'database-url|jwt-secret|openai-api-key'`
- [ ] T098 [US5] Verify secrets are base64 encoded: `kubectl get secret app-secrets -o yaml`
- [ ] T099 [US5] Test secret rotation: Update secret value, restart backend pods: `kubectl rollout restart deployment backend`
- [ ] T100 [US5] Verify new secret loaded: Check backend logs for new DATABASE_URL
- [ ] T101 [US5] Verify k8s/secrets/ is in .gitignore: `git check-ignore k8s/secrets/` returns positive
- [ ] T102 [US5] Document secret creation in README-k8s.md with warning about not committing secrets

**Independent Test Criteria**:
```bash
# All acceptance scenarios from spec
✅ app-secrets created with DATABASE_URL, JWT_SECRET_KEY, OPENAI_API_KEY
✅ Secrets are base64 encoded in Kubernetes
✅ Secrets automatically decoded when mounted as environment variables
✅ Secret updates apply after pod restart
✅ k8s/secrets/ directory is gitignored
```

---

## Phase 8: User Story 6 - Create Helm Charts (P2)

**Goal**: Package Kubernetes manifests as templated Helm charts

**Independent Test**: Helm install succeeds, values can be overridden

**Dependencies**: User Story 1, 2, 3, 5 complete (all manifests exist)

### US6: Backend Helm Chart

- [ ] T103 [P] [US6] Create helm/backend/Chart.yaml with name: backend, version: 1.0.0, appVersion: 1.0.0
- [ ] T104 [P] [US6] Create helm/backend/values.yaml with replicaCount: 3, image.repository: backend, image.tag: latest
- [ ] T105 [P] [US6] Add resource defaults to values.yaml: requests (500m CPU, 512Mi), limits (1000m, 1Gi)
- [ ] T106 [P] [US6] Add health check defaults to values.yaml: liveness/readiness probe configurations
- [ ] T107 [P] [US6] Create helm/backend/templates/deployment.yaml converting k8s/backend/deployment.yaml to Helm template
- [ ] T108 [P] [US6] Replace hardcoded values with {{ .Values.replicaCount }}, {{ .Values.image.repository }}:{{ .Values.image.tag }}
- [ ] T109 [P] [US6] Create helm/backend/templates/service.yaml converting k8s/backend/service.yaml to template
- [ ] T110 [P] [US6] Create helm/backend/templates/secret.yaml for app-secrets (optionally templated)
- [ ] T111 [P] [US6] Create helm/backend/templates/_helpers.tpl with common labels and selectors
- [ ] T112 [P] [US6] Lint backend chart: `helm lint ./helm/backend`
- [ ] T113 [P] [US6] Test template rendering: `helm template backend ./helm/backend`

### US6: Frontend Helm Chart

- [ ] T114 [P] [US6] Create helm/frontend/Chart.yaml with name: frontend, version: 1.0.0, appVersion: 1.0.0
- [ ] T115 [P] [US6] Create helm/frontend/values.yaml with replicaCount: 2, image.repository: frontend, image.tag: latest
- [ ] T116 [P] [US6] Add resource defaults to values.yaml: requests (250m CPU, 256Mi), limits (500m, 512Mi)
- [ ] T117 [P] [US6] Add env.apiUrl to values.yaml: http://backend-service:8000
- [ ] T118 [P] [US6] Create helm/frontend/templates/deployment.yaml converting k8s/frontend/deployment.yaml to template
- [ ] T119 [P] [US6] Replace hardcoded values with {{ .Values.replicaCount }}, {{ .Values.image.repository }}:{{ .Values.image.tag }}
- [ ] T120 [P] [US6] Create helm/frontend/templates/service.yaml with templated nodePort
- [ ] T121 [P] [US6] Create helm/frontend/templates/_helpers.tpl
- [ ] T122 [P] [US6] Lint frontend chart: `helm lint ./helm/frontend`
- [ ] T123 [P] [US6] Test template rendering: `helm template frontend ./helm/frontend`

### US6: PostgreSQL Helm Chart

- [ ] T124 [P] [US6] Create helm/postgres/Chart.yaml with name: postgres, version: 1.0.0
- [ ] T125 [P] [US6] Create helm/postgres/values.yaml with image: postgres:15-alpine, storage: 10Gi
- [ ] T126 [P] [US6] Add postgres credentials to values.yaml: user: todouser, database: tododb
- [ ] T127 [P] [US6] Create helm/postgres/templates/statefulset.yaml converting k8s/postgres/statefulset.yaml
- [ ] T128 [P] [US6] Create helm/postgres/templates/service.yaml
- [ ] T129 [P] [US6] Create helm/postgres/templates/_helpers.tpl
- [ ] T130 [P] [US6] Lint postgres chart: `helm lint ./helm/postgres`

### US6: Helm Deployment

- [ ] T131 [US6] Uninstall kubectl-deployed resources: `kubectl delete -f k8s/`
- [ ] T132 [US6] Install postgres chart: `helm install postgres ./helm/postgres`
- [ ] T133 [US6] Install backend chart: `helm install backend ./helm/backend`
- [ ] T134 [US6] Install frontend chart: `helm install frontend ./helm/frontend`
- [ ] T135 [US6] Verify all pods Running: `kubectl get pods`
- [ ] T136 [US6] Test overriding values: `helm upgrade backend ./helm/backend --set replicaCount=5`
- [ ] T137 [US6] Verify replica count updated: `kubectl get deployment backend -o yaml | grep replicas`
- [ ] T138 [US6] Test multi-environment: Create values-prod.yaml, install with `helm install backend ./helm/backend -f values-prod.yaml`

**Independent Test Criteria**:
```bash
# All acceptance scenarios from spec
✅ helm install backend ./helm/backend succeeds
✅ Pod uses specified image.tag from values.yaml
✅ Different values files produce different configurations
✅ helm dependency update resolves dependencies
```

---

## Phase 9: User Story 7 & 8 - Resource Limits & Health Checks (P2)

**Goal**: Configure resource management and health monitoring

**Independent Test**: Pods respect resource limits, health checks trigger restarts

**Dependencies**: User Story 1, 2, 3 complete

### US7: Resource Limits Validation

- [ ] T139 [P] [US7] Verify backend resource requests set: `kubectl describe pod <backend-pod> | grep -A 2 Requests`
- [ ] T140 [P] [US7] Verify backend resource limits set: `kubectl describe pod <backend-pod> | grep -A 2 Limits`
- [ ] T141 [P] [US7] Verify frontend resource requests/limits: `kubectl describe pod <frontend-pod> | grep -A 4 "Requests\|Limits"`
- [ ] T142 [P] [US7] Verify postgres resource requests/limits: `kubectl describe pod postgres-0 | grep -A 4 "Requests\|Limits"`
- [ ] T143 [P] [US7] Test pod scheduling with resource constraints: Reduce Minikube memory, verify scheduler respects requests
- [ ] T144 [P] [US7] Test OOMKill simulation: Stress test backend to exceed memory limit, verify pod restart

### US8: Health Check Validation

- [ ] T145 [P] [US8] Verify backend liveness probe configured: `kubectl describe pod <backend-pod> | grep Liveness`
- [ ] T146 [P] [US8] Verify backend readiness probe configured: `kubectl describe pod <backend-pod> | grep Readiness`
- [ ] T147 [P] [US8] Verify frontend probes: `kubectl describe pod <frontend-pod> | grep -E "Liveness|Readiness"`
- [ ] T148 [P] [US8] Test readiness probe: Stop backend process in pod, verify pod marked Unready
- [ ] T149 [P] [US8] Test liveness probe: Simulate backend hang, verify pod restarts after failureThreshold
- [ ] T150 [P] [US8] Monitor pod restart count: `kubectl get pods -l app=backend -w`
- [ ] T151 [P] [US8] Verify traffic routing: During readiness failure, verify service stops routing to unhealthy pod

**Independent Test Criteria**:
```bash
# US7 acceptance scenarios
✅ Backend reserves 500m CPU, 512Mi memory
✅ Pod OOMKilled when exceeding 1Gi memory limit
✅ Frontend uses fewer resources than backend
✅ Scheduler places pods based on available capacity

# US8 acceptance scenarios
✅ Backend readiness probe on / marks pod Ready only after success
✅ Liveness probe restarts pod after 3 consecutive failures
✅ Readiness probe marks pod Unready when database connection lost
✅ Frontend startup probe successful after Next.js build completes
```

---

## Phase 10: End-to-End Testing & Documentation

**Goal**: Validate complete application functionality and create comprehensive documentation

**Dependencies**: All user stories complete

### E2E Testing

- [ ] T152 Access frontend via NodePort: `http://$(minikube ip):30000`
- [ ] T153 Test user registration: Create new account via UI
- [ ] T154 Test user login: Authenticate and verify JWT token in localStorage
- [ ] T155 Test task creation: Create multiple tasks via UI
- [ ] T156 Test task update: Edit task title and verify changes persist
- [ ] T157 Test task completion: Mark task as completed, verify status update
- [ ] T158 Test task deletion: Delete task, verify removal from database
- [ ] T159 Test AI chatbot: Send natural language command "Add task: Test deployment"
- [ ] T160 Test data persistence: Delete postgres pod, recreate, verify tasks still exist
- [ ] T161 Test rolling update: Update backend image tag, verify zero-downtime deployment
- [ ] T162 Test pod failure recovery: Delete backend pod, verify automatic replacement

### Documentation

- [ ] T163 [P] Document prerequisites in README-k8s.md (Minikube, kubectl, Helm, Docker)
- [ ] T164 [P] Document image build process in README-k8s.md (eval minikube docker-env, docker build)
- [ ] T165 [P] Document secret creation workflow in README-k8s.md (imperative kubectl create secret)
- [ ] T166 [P] Document deployment steps in README-k8s.md (kubectl apply vs helm install)
- [ ] T167 [P] Document verification steps in README-k8s.md (kubectl get pods, port-forward, curl tests)
- [ ] T168 [P] Document troubleshooting guide in README-k8s.md (ImagePullBackOff, CrashLoopBackOff, connection errors)
- [ ] T169 [P] Create architecture diagram showing container and Kubernetes architecture
- [ ] T170 [P] Document cleanup process: `helm uninstall`, `kubectl delete`, `minikube delete`

### Automation Scripts

- [ ] T171 [P] Create scripts/build-images.sh to automate Docker image builds
- [ ] T172 [P] Create scripts/create-secrets.sh to automate secret creation (with placeholders)
- [ ] T173 [P] Create scripts/deploy-all.sh to automate Helm installations
- [ ] T174 [P] Create scripts/verify-deployment.sh to check pod status, endpoints, health
- [ ] T175 [P] Create scripts/cleanup.sh to remove all resources: `helm uninstall`, `kubectl delete pvc`
- [ ] T176 [P] Make all scripts executable: `chmod +x scripts/*.sh`
- [ ] T177 [P] Test automation scripts end-to-end: Run build-images.sh → deploy-all.sh → verify-deployment.sh

**Validation**:
```bash
# E2E tests pass
✅ User can register, login, and manage tasks
✅ AI chatbot responds to commands
✅ Data persists through pod restarts
✅ Rolling updates complete without errors
✅ Failed pods automatically replaced

# Documentation complete
✅ README-k8s.md covers all deployment steps
✅ Troubleshooting guide addresses common issues
✅ Architecture diagrams illustrate system design
✅ Automation scripts reduce manual steps
```

---

## Dependency Graph

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundational)
    ↓
    ├─→ Phase 5 (US3: Database) ──────────┐
    │                                      ↓
    ├─→ Phase 7 (US5: Secrets) ──────────→ Phase 3 (US1: Backend)
    │                                      ↓
    └─────────────────────────────────────→ Phase 4 (US2: Frontend)
                                           ↓
                                           Phase 6 (US4: Service Discovery)
                                           ↓
                                           Phase 8 (US6: Helm Charts)
                                           ↓
                                           Phase 9 (US7 & US8: Resources & Health)
                                           ↓
                                           Phase 10 (E2E & Documentation)
```

**Critical Path**: Phase 1 → Phase 2 → Phase 5 → Phase 7 → Phase 3 → Phase 4 → Phase 6 → Phase 10

**Parallel Opportunities**:
- Phase 5 (Database) and Phase 7 (Secrets) can run in parallel
- Within Phase 8, all three Helm chart creations (T103-T130) can run in parallel
- Within Phase 9, all validation tasks can run in parallel
- Within Phase 10, all documentation tasks (T163-T170) and script tasks (T171-T177) can run in parallel

---

## MVP Scope Recommendation

**Minimum Viable Product (MVP)**: Phases 1-7
- Phase 1: Setup (required)
- Phase 2: Foundational (required)
- Phase 5: Database Persistence (US3) - Required for backend
- Phase 7: Secrets Management (US5) - Required for security
- Phase 3: Backend Deployment (US1) - Core service
- Phase 4: Frontend Deployment (US2) - User interface
- Phase 6: Service Discovery (US4) - Inter-service communication

**Post-MVP Enhancements**:
- Phase 8: Helm Charts (US6) - Improves deployment experience
- Phase 9: Resource Limits & Health Checks (US7, US8) - Production readiness
- Phase 10: E2E Testing & Documentation - Quality assurance

---

## Parallel Execution Examples

### Phase 2: Foundational Tasks
```bash
# Run in parallel (different files)
Terminal 1: T017 - Create backend/.dockerignore
Terminal 2: T018 - Create frontend/.dockerignore
```

### Phase 8: Helm Chart Creation
```bash
# Run in parallel (independent charts)
Terminal 1: T103-T113 - Backend Helm chart
Terminal 2: T114-T123 - Frontend Helm chart
Terminal 3: T124-T130 - PostgreSQL Helm chart
```

### Phase 9: Validation Tasks
```bash
# Run in parallel (read-only operations)
Terminal 1: T139-T144 - Resource limits validation
Terminal 2: T145-T151 - Health checks validation
```

### Phase 10: Documentation & Scripts
```bash
# Run in parallel (different files)
Terminal 1: T163-T170 - Documentation tasks
Terminal 2: T171-T177 - Automation scripts
```

---

## Implementation Strategy

1. **Start with MVP (Phases 1-7)**: Deliver working Kubernetes deployment
2. **Incremental Delivery**: Each phase produces testable increment
3. **Independent Testing**: Each user story has acceptance criteria
4. **Parallel Execution**: Leverage [P] tasks for faster completion
5. **Continuous Validation**: Test after each phase before moving forward

---

## Task Summary

**Total Tasks**: 177
- Phase 1 (Setup): 12 tasks
- Phase 2 (Foundational): 6 tasks
- Phase 3 (US1 Backend): 23 tasks
- Phase 4 (US2 Frontend): 26 tasks
- Phase 5 (US3 Database): 20 tasks
- Phase 6 (US4 Service Discovery): 7 tasks
- Phase 7 (US5 Secrets): 8 tasks
- Phase 8 (US6 Helm Charts): 36 tasks
- Phase 9 (US7 & US8 Resources/Health): 13 tasks
- Phase 10 (E2E & Documentation): 26 tasks

**Parallelizable Tasks**: 54 tasks marked with [P]
**User Story Tasks**: 159 tasks (excluding setup/foundational)

---

## Next Steps

1. **Review and approve tasks.md**
2. **Begin Phase 1: Setup** (T001-T012)
3. **Execute MVP phases** (1, 2, 5, 7, 3, 4, 6)
4. **Validate each phase** before proceeding
5. **Iterate on feedback** and adjust tasks as needed

---

**Status**: Ready for Implementation
**Approved by**: [Pending]
**Start Date**: [TBD]
