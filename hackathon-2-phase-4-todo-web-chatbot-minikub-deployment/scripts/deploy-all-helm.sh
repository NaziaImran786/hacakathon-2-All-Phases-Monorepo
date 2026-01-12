#!/bin/bash

# Deploy All Components with Helm
# Automated deployment script for FlowTask application

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
NAMESPACE="default"
DB_PASSWORD=""
JWT_SECRET=""
OPENAI_KEY=""
SKIP_BUILD=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --namespace=*)
            NAMESPACE="${arg#*=}"
            shift
            ;;
        --db-password=*)
            DB_PASSWORD="${arg#*=}"
            shift
            ;;
        --jwt-secret=*)
            JWT_SECRET="${arg#*=}"
            shift
            ;;
        --openai-key=*)
            OPENAI_KEY="${arg#*=}"
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --help)
            echo "Deploy FlowTask Application with Helm"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --namespace=NS         Deploy to namespace (default: default)"
            echo "  --db-password=PASS     PostgreSQL password"
            echo "  --jwt-secret=SECRET    JWT secret key"
            echo "  --openai-key=KEY       OpenAI API key"
            echo "  --skip-build           Skip Docker image builds"
            echo "  --help                 Show this help"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     FlowTask Helm Deployment Script          ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v helm &> /dev/null; then
    echo -e "${RED}✗ Helm not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Helm found${NC}"

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}✗ kubectl not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ kubectl found${NC}"

if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}✗ Cannot connect to Kubernetes cluster${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Connected to Kubernetes cluster${NC}"

echo ""

# Build Docker images
if [ "$SKIP_BUILD" = false ]; then
    echo -e "${YELLOW}Building Docker images...${NC}"

    # Check if using Minikube
    if kubectl config current-context | grep -q minikube; then
        echo -e "${BLUE}ℹ Using Minikube Docker daemon${NC}"
        eval $(minikube docker-env)
    fi

    docker build -t backend:latest ./backend
    docker build -t frontend:latest ./frontend

    echo -e "${GREEN}✓ Images built${NC}"
    echo ""
else
    echo -e "${BLUE}ℹ Skipping image builds${NC}"
    echo ""
fi

# Prompt for secrets if not provided
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}Enter PostgreSQL password:${NC}"
    read -s DB_PASSWORD
    echo ""
fi

if [ -z "$JWT_SECRET" ]; then
    echo -e "${YELLOW}Enter JWT secret (or press Enter to generate):${NC}"
    read -s JWT_SECRET
    echo ""
    if [ -z "$JWT_SECRET" ]; then
        JWT_SECRET=$(openssl rand -hex 32)
        echo -e "${GREEN}✓ Generated JWT secret${NC}"
    fi
fi

if [ -z "$OPENAI_KEY" ]; then
    echo -e "${YELLOW}Enter OpenAI API key:${NC}"
    read -s OPENAI_KEY
    echo ""
fi

# Deploy PostgreSQL
echo -e "${YELLOW}Deploying PostgreSQL...${NC}"
helm install postgres ./helm/postgres \
    --namespace $NAMESPACE \
    --set postgresql.password="$DB_PASSWORD" \
    --wait \
    --timeout 120s

echo -e "${GREEN}✓ PostgreSQL deployed${NC}"
echo ""

# Get postgres service name
POSTGRES_SERVICE=$(kubectl get service -n $NAMESPACE -l app.kubernetes.io/name=postgres -o jsonpath='{.items[0].metadata.name}')
echo -e "${BLUE}ℹ PostgreSQL service: $POSTGRES_SERVICE${NC}"
echo ""

# Deploy Backend
echo -e "${YELLOW}Deploying Backend...${NC}"
helm install backend ./helm/backend \
    --namespace $NAMESPACE \
    --set env.DATABASE_URL="postgresql://todouser:$DB_PASSWORD@$POSTGRES_SERVICE:5432/tododb" \
    --set env.JWT_SECRET_KEY="$JWT_SECRET" \
    --set env.OPENAI_API_KEY="$OPENAI_KEY" \
    --set image.pullPolicy=IfNotPresent \
    --wait \
    --timeout 120s

echo -e "${GREEN}✓ Backend deployed${NC}"
echo ""

# Get backend service name
BACKEND_SERVICE=$(kubectl get service -n $NAMESPACE -l app.kubernetes.io/name=backend -o jsonpath='{.items[0].metadata.name}')
echo -e "${BLUE}ℹ Backend service: $BACKEND_SERVICE${NC}"
echo ""

# Deploy Frontend
echo -e "${YELLOW}Deploying Frontend...${NC}"
helm install frontend ./helm/frontend \
    --namespace $NAMESPACE \
    --set env.NEXT_PUBLIC_API_URL="http://$BACKEND_SERVICE:8000" \
    --set image.pullPolicy=IfNotPresent \
    --wait \
    --timeout 120s

echo -e "${GREEN}✓ Frontend deployed${NC}"
echo ""

# Show deployment status
echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║           Deployment Successful!              ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
echo ""

echo "Deployment Summary:"
helm list -n $NAMESPACE
echo ""

echo "Pod Status:"
kubectl get pods -n $NAMESPACE
echo ""

echo "Services:"
kubectl get services -n $NAMESPACE
echo ""

# Access information
echo -e "${BLUE}Access Information:${NC}"
if kubectl config current-context | grep -q minikube; then
    MINIKUBE_IP=$(minikube ip)
    echo "  Frontend: http://$MINIKUBE_IP:30000"
    echo ""
    echo "Or use port-forward:"
fi
echo "  kubectl port-forward service/frontend-frontend-service 3000:3000 -n $NAMESPACE"
echo "  Then visit: http://localhost:3000"
echo ""

echo -e "${BLUE}Useful Commands:${NC}"
echo "  # View logs"
echo "  kubectl logs -l app=backend -n $NAMESPACE"
echo "  kubectl logs -l app=frontend -n $NAMESPACE"
echo ""
echo "  # Check status"
echo "  helm status backend -n $NAMESPACE"
echo "  helm status frontend -n $NAMESPACE"
echo "  helm status postgres -n $NAMESPACE"
echo ""
echo "  # Uninstall"
echo "  helm uninstall frontend backend postgres -n $NAMESPACE"
echo ""

echo -e "${GREEN}Done!${NC}"
