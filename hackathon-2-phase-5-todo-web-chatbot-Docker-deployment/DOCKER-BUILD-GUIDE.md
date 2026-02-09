# Docker Build Guide for FlowTask

This guide provides instructions for building and testing the Docker images for the FlowTask application.

## Prerequisites

- Docker Desktop installed and running
- Docker version 24+
- At least 8GB RAM allocated to Docker
- At least 20GB free disk space

## Dockerfiles Overview

### Backend Dockerfile (backend/Dockerfile)

**Multi-stage build strategy:**
- **Stage 1 (builder)**: Installs build dependencies and Python packages
- **Stage 2 (runtime)**: Minimal image with only runtime dependencies

**Key features:**
- Base image: `python:3.11-slim` (compatible with psycopg2-binary)
- Non-root user: `appuser` (UID 1000)
- Port: 8000
- Health check: HTTP GET on `/`
- Includes all dependencies: FastAPI, SQLModel, MCP, OpenAI Agents SDK

**Environment variables required:**
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `OPENAI_API_KEY`: OpenAI API key for AI features

**Target size:** < 500MB

---

### Frontend Dockerfile (frontend/Dockerfile)

**Multi-stage build strategy:**
- **Stage 1 (deps)**: Installs production dependencies
- **Stage 2 (builder)**: Installs all dependencies and builds Next.js app
- **Stage 3 (runtime)**: Minimal image with production build artifacts

**Key features:**
- Base image: `node:20-alpine` (minimal size)
- Non-root user: `appuser` (UID 1000)
- Port: 3000
- Health check: HTTP GET on `/`
- Optimized production build with static assets

**Environment variables required:**
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://backend-service:8000)

**Target size:** < 300MB

---

## Build Instructions

### 1. Build Backend Image

```bash
# Navigate to backend directory
cd backend

# Build the image
docker build -t backend:latest .

# Verify image was created
docker images | grep backend

# Check image size (should be < 500MB)
docker images backend:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

**Expected output:**
```
REPOSITORY   TAG      SIZE
backend      latest   ~450MB
```

---

### 2. Build Frontend Image

```bash
# Navigate to frontend directory
cd frontend

# Build the image
docker build -t frontend:latest .

# Verify image was created
docker images | grep frontend

# Check image size (should be < 300MB)
docker images frontend:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

**Expected output:**
```
REPOSITORY   TAG      SIZE
frontend     latest   ~250MB
```

---

## Testing Images Locally

### Test Backend Image

```bash
# Run backend container with test environment variables
docker run -d \
  --name test-backend \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e JWT_SECRET_KEY="test-secret-key" \
  -e OPENAI_API_KEY="sk-test-key" \
  backend:latest

# Check if container is running
docker ps | grep test-backend

# Test health endpoint
curl http://localhost:8000/

# Check logs
docker logs test-backend

# Verify environment variables are set
docker exec test-backend env | grep -E 'DATABASE_URL|JWT_SECRET_KEY|OPENAI_API_KEY'

# Verify non-root user
docker exec test-backend whoami
# Expected output: appuser

# Stop and remove container
docker stop test-backend
docker rm test-backend
```

**Expected responses:**
- `curl http://localhost:8000/` should return: `{"status":"Backend is running successfully!"}`
- Container should start without errors
- Environment variables should be present

---

### Test Frontend Image

```bash
# Run frontend container
docker run -d \
  --name test-frontend \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL="http://localhost:8000" \
  frontend:latest

# Check if container is running
docker ps | grep test-frontend

# Test health endpoint
curl http://localhost:3000/

# Open in browser
# Navigate to: http://localhost:3000

# Check logs
docker logs test-frontend

# Verify environment variable
docker exec test-frontend env | grep NEXT_PUBLIC_API_URL

# Verify non-root user
docker exec test-frontend whoami
# Expected output: appuser

# Stop and remove container
docker stop test-frontend
docker rm test-frontend
```

**Expected responses:**
- Browser should show the login page
- `curl http://localhost:3000/` should return HTML
- No errors in logs

---

## Testing Full Stack Locally

To test both frontend and backend together:

```bash
# Create a Docker network
docker network create flowtask-network

# Start backend
docker run -d \
  --name backend \
  --network flowtask-network \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
  -e JWT_SECRET_KEY="test-secret" \
  -e OPENAI_API_KEY="sk-test" \
  backend:latest

# Start frontend
docker run -d \
  --name frontend \
  --network flowtask-network \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL="http://backend:8000" \
  frontend:latest

# Test connectivity
docker exec frontend wget -O- http://backend:8000/

# Open application in browser
# Navigate to: http://localhost:3000

# Cleanup
docker stop frontend backend
docker rm frontend backend
docker network rm flowtask-network
```

---

## Build Optimization Tips

### Reduce Build Time

1. **Use BuildKit** (faster builds with better caching):
   ```bash
   export DOCKER_BUILDKIT=1
   docker build -t backend:latest ./backend
   ```

2. **Use Docker layer caching**:
   - Dependencies are copied first (requirements.txt, package.json)
   - Source code is copied last
   - Rebuilds are faster if only source code changes

3. **Parallel builds**:
   ```bash
   # Build both images simultaneously
   docker build -t backend:latest ./backend &
   docker build -t frontend:latest ./frontend &
   wait
   ```

---

### Reduce Image Size

1. **Multi-stage builds** (already implemented):
   - Build dependencies are not included in final image
   - Only runtime files are copied

2. **Alpine base images** (frontend uses this):
   - Smaller base image (~5MB vs ~100MB)

3. **Clean up after installs**:
   - `apt-get clean` and `rm -rf /var/lib/apt/lists/*` (backend)
   - `npm ci` instead of `npm install` (frontend)

4. **Use .dockerignore**:
   - Excludes unnecessary files from build context
   - Faster builds and smaller images

---

## Troubleshooting

### Build Failures

**Error: "docker: command not found"**
- Solution: Install Docker Desktop and ensure it's running

**Error: "Cannot connect to Docker daemon"**
- Solution: Start Docker Desktop
- Verify: `docker ps` should run without errors

**Error: "psycopg2-binary installation failed" (backend)**
- Cause: Missing build dependencies
- Solution: Already handled in Dockerfile with `gcc` and `libpq-dev`

**Error: "npm ERR! network" (frontend)**
- Cause: Network issues or npm registry down
- Solution: Retry build or use `npm ci --legacy-peer-deps`

---

### Image Size Issues

**Backend image > 500MB:**
- Check installed packages: `docker history backend:latest`
- Ensure multi-stage build is working correctly
- Verify .dockerignore is excluding .venv/

**Frontend image > 300MB:**
- Verify node_modules are only from production dependencies
- Check if .next/ folder is optimized
- Ensure devDependencies are not in final stage

---

### Runtime Issues

**Container exits immediately:**
- Check logs: `docker logs <container-name>`
- Verify environment variables are set correctly
- Ensure application dependencies are installed

**Health check failing:**
- Check if application is listening on correct port (8000 for backend, 3000 for frontend)
- Verify application starts successfully
- Check logs for startup errors

**Permission denied errors:**
- Verify files are owned by appuser (UID 1000)
- Check Dockerfile COPY commands use `--chown=appuser:appuser`

---

## Kubernetes-Specific Considerations

When building for Kubernetes deployment:

### Option 1: Build with Minikube Docker Daemon

```bash
# Configure Docker to use Minikube's daemon
eval $(minikube docker-env)

# Build images (they'll be stored in Minikube)
docker build -t backend:latest ./backend
docker build -t frontend:latest ./frontend

# Verify images are in Minikube
docker images | grep -E 'backend|frontend'

# Set imagePullPolicy to Never in Kubernetes manifests
# imagePullPolicy: Never
```

**Advantages:**
- No need for external registry
- Faster builds (no push/pull)
- Ideal for local development

**Disadvantages:**
- Images lost if Minikube is deleted
- Not suitable for production

---

### Option 2: Push to Container Registry

```bash
# Tag images for registry
docker tag backend:latest <your-registry>/backend:latest
docker tag frontend:latest <your-registry>/frontend:latest

# Push to registry
docker push <your-registry>/backend:latest
docker push <your-registry>/frontend:latest

# Update Kubernetes manifests to reference registry images
# image: <your-registry>/backend:latest
```

**Registries:**
- Docker Hub: `docker.io/username/backend:latest`
- GitHub Container Registry: `ghcr.io/username/backend:latest`
- Google Container Registry: `gcr.io/project-id/backend:latest`

---

## Validation Checklist

Before deploying to Kubernetes, verify:

- [ ] Backend image builds successfully
- [ ] Backend image size < 500MB
- [ ] Backend container runs without errors
- [ ] Backend health endpoint returns 200 OK
- [ ] Backend runs as non-root user (appuser)
- [ ] Frontend image builds successfully
- [ ] Frontend image size < 300MB
- [ ] Frontend container runs without errors
- [ ] Frontend serves pages correctly
- [ ] Frontend runs as non-root user (appuser)
- [ ] Both images are tagged correctly (latest or version)
- [ ] .dockerignore files exclude unnecessary files

---

## Next Steps

Once Docker images are built and tested:

1. **Start Minikube**: `minikube start --driver=docker --cpus=4 --memory=8192`
2. **Configure Docker**: `eval $(minikube docker-env)`
3. **Rebuild images in Minikube context**
4. **Create Kubernetes manifests** (Deployments, Services, Secrets)
5. **Deploy to Kubernetes**: `kubectl apply -f k8s/`

See `README-k8s.md` for full Kubernetes deployment instructions.

---

## References

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Next.js Docker Deployment](https://nextjs.org/docs/deployment#docker-image)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)
