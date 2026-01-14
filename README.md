# FlowTask - AI-Powered Productivity Dashboard

A modern, stateless Todo application featuring an integrated AI Assistant powered by OpenAI and MCP (Model Context Protocol). FlowTask combines intuitive task management with intelligent AI assistance, allowing users to create, organize, and complete tasks using natural language commands.

![Version](https://img.shields.io/badge/version-3.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Overview

FlowTask is a Phase III Todo Web Chatbot that provides:
- **Stateless AI Chat**: AI assistant with full conversational memory, no session state required
- **Unified Data Sync**: AI-created tasks and manual tasks are stored in the same database for seamless synchronization
- **Modern UI**: Floating AI widget, side-drawer chat interface, and dark-themed glassmorphism dashboard
- **Secure Auth**: JWT-based authentication with signup-to-login redirect flow

## Tech Stack

### Frontend
- **Framework**: Next.js 14.1.0 (App Router)
- **Styling**: Tailwind CSS with custom glassmorphism theme
- **Animations**: Framer Motion for smooth UI transitions
- **Icons**: Lucide React
- **TypeScript**: Full type safety

### Backend
- **Framework**: FastAPI (Python)
- **Database**: Neon PostgreSQL with SQLModel ORM
- **Authentication**: JWT (python-jose) with Bcrypt password hashing
- **CORS**: Configured for frontend-backend communication

### AI & MCP
- **OpenAI Agents SDK**: Agent orchestration and structured outputs
- **Model**: GPT-4o
- **MCP (Model Context Protocol)**: Official MCP SDK (FastMCP v1.25.0) for tool integrations
- **MCP Tools**: Task CRUD operations (add, list, complete, update, delete)

## Key Features & Architecture

### Stateless AI Chat

FlowTask implements a **stateless request cycle** where the AI assistant fetches entire conversation history from the database on every request:

```
Request Flow:
1. User sends message → Frontend
2. Frontend includes JWT in Authorization header
3. Backend validates JWT and extracts user_id
4. ChatService fetches all messages from Neon DB for this conversation
5. Agent processes message history + new user message
6. Agent response is saved to database
7. Response returned to frontend
```

**Why Stateless?**
- No memory leaks or session state issues
- Easy horizontal scaling (any server can handle any request)
- All conversation history persisted to Neon PostgreSQL
- User can refresh page and continue seamlessly

**Database Schema for Chat:**
- `conversations` table: Stores chat sessions with user isolation
- `messages` table: Stores all user/assistant messages with tool context

### Unified Data Sync

All tasks are stored in a single Neon PostgreSQL database table, whether created:
- Manually via UI (frontend → REST API)
- Via AI assistant (user → AI → MCP tools → same database)

**Task Table Schema:**
```python
class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = None
    status: str = "pending"  # pending, completed, cancelled
    user_id: str = Field(foreign_key="user.id")
    due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
```

**Real-time Sync:**
- Frontend uses `fetchTasks()` after AI interactions to update UI
- Custom event `taskUpdated` dispatched for cross-component synchronization
- Both manual and AI-created tasks appear in the same dashboard

### Modern UI

**Dashboard Features:**
- Dark theme with glassmorphism (semi-transparent cards, backdrop blur)
- Centered task list with responsive layout
- Floating Action Button (FAB) for AI chat access
- Side-drawer chat window (450px width, full height)
- Smooth animations via Framer Motion

**Chat Interface:**
- Full-height drawer from right side
- Quick action buttons (Add Task, List Tasks, Complete, etc.)
- Message bubbles with timestamps
- Typing indicators during AI processing

### Secure Authentication

**Signup Flow:**
1. User registers with username/password
2. Backend creates user account in database
3. Returns success message only: `{"message": "User created successfully"}`
4. Frontend redirects to `/login` with toast message
5. User must explicitly log in with credentials

**Login Flow:**
1. User submits credentials to `/token` endpoint
2. Backend validates and returns JWT (30-minute expiry)
3. Frontend stores JWT in `localStorage`
4. All subsequent requests include `Authorization: Bearer {token}` header

**Security Features:**
- Passwords hashed with Bcrypt before storage
- JWT tokens signed with secret key (HS256)
- User isolation enforced via `user_id` in all database queries
- CORS configured for frontend origin only

## Project Structure

```
flowtask/
├── backend/                  # FastAPI backend
│   ├── main.py              # Main API app, auth endpoints, task CRUD
│   ├── auth.py              # JWT token generation/validation
│   ├── models.py            # Legacy SQLModel definitions (Task, User)
│   ├── src/
│   │   ├── api/
│   │   │   ├── chat.py     # POST /api/chat endpoint
│   │   │   ├── schemas.py  # Pydantic models for API
│   │   │   └── deps.py    # Dependency injection (JWT extraction)
│   │   ├── services/
│   │   │   ├── agent.py     # OpenAI Agents SDK orchestration
│   │   │   ├── chat.py     # Conversation history management
│   │   │   └── db.py      # Database connection and queries
│   │   ├── mcp/
│   │   │   ├── server.py    # MCP server wrapper (FastMCP)
│   │   │   └── tools/
│   │   │       ├── add_task.py
│   │   │       ├── list_tasks.py
│   │   │       ├── complete_task.py
│   │   │       ├── update_task.py
│   │   │       └── delete_task.py
│   │   └── models/
│   │       ├── conversation.py
│   │       ├── message.py
│   │       └── task.py
│   └── requirements.txt
│
├── frontend/                 # Next.js 14 frontend
│   ├── app/
│   │   ├── layout.tsx       # Root layout with metadata
│   │   ├── page.tsx         # Landing page
│   │   ├── login/
│   │   │   └── page.tsx     # Login form with JWT storage
│   │   ├── signup/
│   │   │   └── page.tsx     # Signup form (no token returned)
│   │   └── tasks/
│   │       └── page.tsx     # Main dashboard + AI chat
│   ├── src/
│   │   └── lib/
│   │       └── api.ts         # API client with JWT auth
│   ├── package.json
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── .env                     # Environment variables (create from example)
├── CLAUDE.md               # Project guidelines
└── README.md               # This file
```

## Installation

Choose your deployment method:
- **[Local Development](#local-development)**: Run directly on your machine (Python + Node.js)
- **[Phase IV: Kubernetes](#phase-iv-kubernetes-deployment)**: Deploy to Minikube/Kubernetes with Helm charts

---

## Local Development

### Prerequisites
- Python 3.9+
- Node.js 18+
- Neon PostgreSQL account (free tier available)
- OpenAI API key

### Backend Setup

1. **Create virtual environment:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
Create `.env` file in `backend/`:
```env
DATABASE_URL=postgresql://user:password@ep-cool.us-east-2.aws.neon.tech/neondb?sslmode=require
OPENAI_API_KEY=sk-proj-...
BETTER_AUTH_SECRET=your-secret-key-here
```

4. **Run backend:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Configure environment:**
Create `.env.local` file in `frontend/`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. **Run frontend:**
```bash
npm run dev
```

4. **Open browser:**
Navigate to `http://localhost:3000`

## Usage

### Creating a Task

**Manual:**
1. Login to your account
2. Click "Add Task" button
3. Enter task details
4. Click "Create Task"

**Via AI Assistant:**
1. Click floating chat button (bottom-right)
2. Type: "Add a task called 'Buy groceries'"
3. AI will confirm and create task
4. Task appears in dashboard automatically

### Managing Tasks

- **Complete**: Click "Complete" button on any task
- **Edit**: Click edit icon to modify title/description
- **Delete**: Click "Delete" button to remove task

### AI Chat Commands

The AI assistant understands natural language:
- "Show me all my tasks"
- "Add a task to call mom tomorrow"
- "Mark task #3 as complete"
- "Delete the task about groceries"
- "Update task #2 to say 'Buy milk instead of groceries'"

## API Endpoints

### Authentication
- `POST /signup` - Create user account (returns success message, no token)
- `POST /token` - Login and receive JWT token
- `GET /api/me` - Get current user info (JWT required)

### Tasks
- `POST /api/{user_id}/tasks/` - Create task (JWT required)
- `GET /api/{user_id}/tasks/` - List user's tasks (JWT required)
- `PUT /api/{user_id}/tasks/{task_id}` - Update task (JWT required)
- `DELETE /api/{user_id}/tasks/{task_id}` - Delete task (JWT required)
- `PATCH /api/{user_id}/tasks/{task_id}/complete` - Toggle completion (JWT required)

### AI Chat
- `POST /api/chat` - Send message to AI assistant (JWT required)
  - Request: `{ "message": "string", "conversation_id": number }`
  - Response: `{ "success": true, "response": { "content": "...", "tasks": [...] }, "conversation_id": 123, "message_id": 456 }`
- `GET /api/health` - Health check

## MCP Tools

The AI assistant has access to these MCP tools:

| Tool | Description | Parameters |
|------|-------------|-------------|
| `add_task` | Create a new task | `title`, `description?`, `due_date?` |
| `list_tasks` | List user's tasks | `status?` (all/pending/completed), `limit?`, `offset?` |
| `complete_task` | Mark task as completed | `task_id` |
| `update_task` | Update task details | `task_id`, `title?`, `description?`, `due_date?` |
| `delete_task` | Remove a task | `task_id` |

All tools are scoped to the authenticated user via `user_id`.

## Database Schema

### Legacy Tables (Phase I/II)
- `users`: username, hashed_password
- `tasks`: id, title, description, completed, owner_id

### Phase III Tables
- `conversations`: id, user_id, title, created_at, updated_at
- `messages`: id, conversation_id, role, content, tool_calls, tool_results, created_at
- `tasks` (extended): status, due_date, created_at, updated_at

## Development

### Running Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Building for Production
```bash
# Frontend
cd frontend
npm run build
npm start

# Backend (with gunicorn)
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## Phase IV: Kubernetes Deployment

Deploy FlowTask to a local Kubernetes cluster with production-ready configurations including persistent storage, health checks, and horizontal scaling.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│                                                              │
│  ┌──────────────┐      ┌──────────────┐     ┌────────────┐ │
│  │   Frontend   │─────▶│   Backend    │────▶│ PostgreSQL │ │
│  │  (Next.js)   │      │  (FastAPI)   │     │   (Neon)   │ │
│  │              │      │              │     │            │ │
│  │  NodePort    │      │  ClusterIP   │     │ StatefulSet│ │
│  │  Port: 30000 │      │  Port: 8000  │     │ + PVC 10Gi │ │
│  │              │      │              │     │            │ │
│  │  Replicas: 2 │      │  Replicas: 3 │     │ Replicas: 1│ │
│  └──────────────┘      └──────────────┘     └────────────┘ │
│         │                      │                    │        │
│         │                      ▼                    │        │
│         │              ┌──────────────┐             │        │
│         │              │  AI Chatbot  │             │        │
│         │              │   (OpenAI)   │             │        │
│         │              │              │             │        │
│         │              │  MCP Tools   │             │        │
│         │              └──────────────┘             │        │
│         │                                           │        │
│         └───────────────────────────────────────────┘        │
│                   Service Discovery (DNS)                    │
└─────────────────────────────────────────────────────────────┘

External Access:
  - Frontend: http://<minikube-ip>:30000 (NodePort)
  - Backend API: http://backend-backend-service:8000 (ClusterIP)
  - Database: postgres-postgres-service:5432 (ClusterIP)
```

**Components:**
- **Frontend**: Next.js app with glassmorphism UI, exposed via NodePort for external access
- **Backend**: FastAPI with JWT auth, OpenAI Agents SDK, and MCP tools
- **Database**: PostgreSQL 15 with 10Gi persistent volume for data durability
- **Service Discovery**: Kubernetes DNS automatically resolves service names
- **Health Checks**: Liveness/readiness probes ensure zero-downtime deployments
- **Secrets**: Kubernetes Secrets for DB credentials, JWT keys, and OpenAI API key

### Prerequisites

#### Required Tools

**1. Docker Desktop**
- Download: https://www.docker.com/products/docker-desktop/
- Used for building container images
- Start Docker Desktop before proceeding

**2. Minikube**
```bash
# macOS
brew install minikube

# Windows (using Chocolatey)
choco install minikube

# Linux
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**3. kubectl** (Kubernetes CLI)
```bash
# macOS
brew install kubectl

# Windows (using Chocolatey)
choco install kubernetes-cli

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install kubectl /usr/local/bin/kubectl
```

**4. Helm** (Kubernetes package manager)
```bash
# macOS
brew install helm

# Windows (using Chocolatey)
choco install kubernetes-helm

# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

#### Verify Installation
```bash
docker --version          # Docker version 20.10+
minikube version         # minikube version: v1.30+
kubectl version --client # Client Version: v1.28+
helm version             # Version: v3.12+
```

### Quick Start (One-Command Deployment)

#### 1. Start Minikube
```bash
# Start with sufficient resources
minikube start --driver=docker --cpus=4 --memory=8192

# Verify cluster is running
minikube status
kubectl cluster-info
```

#### 2. Configure Docker for Minikube
```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Verify
docker ps  # Should show Kubernetes containers
```

#### 3. Build Docker Images
```bash
# Build backend image
docker build -t backend:latest ./backend

# Build frontend image
docker build -t frontend:latest ./frontend

# Verify images
docker images | grep -E "backend|frontend"
```

#### 4. Deploy with Helm (One Command)
```bash
# Deploy all components (Postgres, Backend, Frontend)
./scripts/deploy-all-helm.sh \
  --db-password "your-secure-password" \
  --jwt-secret "your-jwt-secret-key" \
  --openai-key "sk-your-openai-api-key"

# Or run interactively (script will prompt for secrets)
./scripts/deploy-all-helm.sh
```

**What this does:**
- ✅ Validates prerequisites (helm, kubectl, cluster)
- ✅ Builds Docker images (if not using `--skip-build`)
- ✅ Deploys PostgreSQL StatefulSet with 10Gi persistent volume
- ✅ Deploys Backend (3 replicas) with environment variables and secrets
- ✅ Deploys Frontend (2 replicas) with API URL configuration
- ✅ Waits for all pods to be ready
- ✅ Displays access information and useful commands

**Deployment time:** ~3-5 minutes (depending on image pulls)

#### 5. Verify Deployment
```bash
# Check all components are running
kubectl get pods
kubectl get services
kubectl get pvc

# View Helm releases
helm list

# Check pod logs
kubectl logs -l app=backend --tail=50
kubectl logs -l app=frontend --tail=50
```

### Accessing the Application

#### Method 1: NodePort (Minikube)
```bash
# Get Minikube IP
minikube ip
# Example output: 192.168.49.2

# Access frontend
# Navigate to: http://192.168.49.2:30000
```

#### Method 2: Port Forward
```bash
# Forward frontend port
kubectl port-forward service/frontend-frontend-service 3000:3000

# Open browser
# Navigate to: http://localhost:3000
```

#### Method 3: Minikube Service (Auto-open)
```bash
# Automatically open in browser
minikube service frontend-frontend-service
```

### Validation & Testing

#### 1. Validate Deployment Health
```bash
# Run comprehensive validation
./scripts/validate-deployment.sh

# Expected output:
# ✓ All pods are in Running state
# ✓ All pods are Ready
# ✓ Backend replicas: 3/3 ready
# ✓ Frontend replicas: 2/2 ready
# ✓ Postgres replicas: 1/1 ready
# ✓ Resource metrics available
# ✓ Self-healing test passed
```

**What it validates:**
- ✅ Liveness and readiness probe status
- ✅ Pod restart counts (should be <5)
- ✅ Resource usage (CPU/Memory via metrics-server)
- ✅ Replica counts match desired state
- ✅ Self-healing: Deletes a pod and verifies auto-recreation

#### 2. Run End-to-End Tests
```bash
# Run full E2E connectivity test
./scripts/test-e2e-connectivity.sh

# Run with verbose output
./scripts/test-e2e-connectivity.sh --verbose

# Keep test data (don't cleanup)
./scripts/test-e2e-connectivity.sh --no-cleanup
```

**What it tests:**
- ✅ Frontend accessibility (HTTP 200 response)
- ✅ Backend API health endpoint
- ✅ User registration and login (JWT token)
- ✅ Todo creation via POST `/todos`
- ✅ Database verification (SQL query confirms data)
- ✅ AI chatbot endpoint response
- ✅ End-to-end data flow (Frontend → Backend → Database)

**Expected output:**
```
╔═══════════════════════════════════════════════╗
║     FlowTask E2E Connectivity Test           ║
╚═══════════════════════════════════════════════╝

✓ Frontend is accessible
✓ Backend health endpoint responding
✓ Test user registered and logged in
✓ Todo created via API (ID: 42)
✓ Test Todo found in database (count: 1)
✓ AI Chatbot endpoint responding

Passed: 18 checks
Failed: 0 checks

✓ All E2E tests passed!
```

#### 3. Manual Testing

**Test Frontend:**
```bash
# Get frontend URL
minikube service frontend-frontend-service --url
# Visit URL in browser and verify UI loads
```

**Test Backend API:**
```bash
# Port-forward backend
kubectl port-forward service/backend-backend-service 8000:8000

# Test health endpoint
curl http://localhost:8000/health

# View OpenAPI docs
# Navigate to: http://localhost:8000/docs
```

**Test Database:**
```bash
# Connect to postgres pod
kubectl exec -it postgres-postgres-0 -- psql -U todouser -d tododb

# Run SQL queries
\dt                    # List tables
SELECT * FROM tasks;   # View tasks
SELECT * FROM users;   # View users
\q                     # Exit
```

### Helm Chart Management

#### View Status
```bash
# List all Helm releases
helm list

# Get detailed status
helm status postgres
helm status backend
helm status frontend
```

#### Upgrade Deployment
```bash
# Scale backend to 5 replicas
helm upgrade backend ./helm/backend --set replicaCount=5

# Update environment variable
helm upgrade backend ./helm/backend \
  --set env.OPENAI_API_KEY="sk-new-key"

# Use custom values file
helm upgrade backend ./helm/backend -f production-values.yaml
```

#### Rollback
```bash
# View revision history
helm history backend

# Rollback to previous version
helm rollback backend

# Rollback to specific revision
helm rollback backend 2
```

#### Uninstall
```bash
# Uninstall all components
helm uninstall frontend backend postgres

# Delete persistent volume claims (PVCs)
kubectl delete pvc postgres-storage-postgres-postgres-0

# Verify cleanup
kubectl get pods
kubectl get pvc
```

### Troubleshooting

#### Pods Not Starting
```bash
# Check pod status
kubectl get pods

# Describe pod for events
kubectl describe pod <pod-name>

# View logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # Previous crash logs
```

#### Image Pull Errors
```bash
# Verify Docker images exist in Minikube
eval $(minikube docker-env)
docker images | grep -E "backend|frontend"

# Rebuild if missing
docker build -t backend:latest ./backend
docker build -t frontend:latest ./frontend
```

#### Service Not Accessible
```bash
# Check service endpoints
kubectl get endpoints

# Verify service selector matches pod labels
kubectl get pods --show-labels
kubectl describe service <service-name>

# Test service connectivity from within cluster
kubectl run curl-test --image=curlimages/curl -it --rm -- sh
# Inside pod:
curl http://backend-backend-service:8000/health
```

#### Database Connection Issues
```bash
# Check postgres pod logs
kubectl logs postgres-postgres-0

# Verify secret exists
kubectl get secret postgres-secret -o yaml

# Test connection
kubectl exec -it postgres-postgres-0 -- \
  psql -U todouser -d tododb -c "SELECT 1;"
```

#### Helm Chart Validation
```bash
# Lint charts
helm lint ./helm/backend
helm lint ./helm/frontend
helm lint ./helm/postgres

# Dry-run install
helm install backend ./helm/backend --dry-run --debug

# Render templates
helm template backend ./helm/backend
```

### Production Considerations

#### Security
- ⚠️ **Change default passwords**: Never use `changeme` in production
- 🔐 **Use Secrets Manager**: Consider Sealed Secrets or External Secrets Operator
- 🔒 **Enable RBAC**: Configure role-based access control
- 🌐 **Network Policies**: Restrict pod-to-pod communication

#### High Availability
- 📈 **Increase replicas**: Set `replicaCount: 5` for backend/frontend
- ⚖️ **Enable autoscaling**: Configure HorizontalPodAutoscaler
- 🔄 **Pod Disruption Budgets**: Ensure minimum availability during updates
- 💾 **Database backups**: Regular backups of PostgreSQL data

#### Monitoring
- 📊 **Prometheus + Grafana**: Deploy for metrics visualization
- 📝 **ELK Stack**: Centralized logging
- 🔔 **Alerting**: Configure alerts for pod failures, high CPU, etc.

#### Resource Management
```yaml
# Example production values (backend)
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
  targetCPUUtilizationPercentage: 80
```

### Additional Resources

- **Helm Charts Documentation**: [helm/README.md](helm/README.md)
- **Docker Build Guide**: [DOCKER-BUILD-GUIDE.md](DOCKER-BUILD-GUIDE.md)
- **Kubernetes Specification**: [specs/features/kubernetes-deployment.md](specs/features/kubernetes-deployment.md)
- **Validation Script**: [scripts/validate-deployment.sh](scripts/validate-deployment.sh)
- **E2E Test Script**: [scripts/test-e2e-connectivity.sh](scripts/test-e2e-connectivity.sh)

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: [repository-url]/issues
- Documentation: [docs-url]

---

**Built with ❤️ using Next.js, FastAPI, and OpenAI Agents SDK**

