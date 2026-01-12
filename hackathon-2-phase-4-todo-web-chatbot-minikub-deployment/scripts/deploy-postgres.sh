#!/bin/bash

# PostgreSQL Deployment Script for Kubernetes
# Deploys PostgreSQL StatefulSet with persistent storage
#
# Usage:
#   ./scripts/deploy-postgres.sh [OPTIONS]
#
# Options:
#   --password=PASSWORD   Set database password (default: prompts for input)
#   --skip-secret        Skip secret creation (assumes already exists)
#   --namespace=NS       Deploy to specific namespace (default: default)
#   --dry-run            Show what would be deployed without applying
#   --help               Show this help message

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
NAMESPACE="default"
SKIP_SECRET=false
DRY_RUN=false
DB_PASSWORD=""

# Parse arguments
for arg in "$@"; do
    case $arg in
        --password=*)
            DB_PASSWORD="${arg#*=}"
            shift
            ;;
        --skip-secret)
            SKIP_SECRET=true
            shift
            ;;
        --namespace=*)
            NAMESPACE="${arg#*=}"
            shift
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help)
            echo "PostgreSQL Deployment Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --password=PASSWORD   Set database password"
            echo "  --skip-secret        Skip secret creation"
            echo "  --namespace=NS       Deploy to namespace (default: default)"
            echo "  --dry-run            Show what would be deployed"
            echo "  --help               Show this help"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  PostgreSQL Kubernetes Deployment Script     ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}✗ kubectl not found${NC}"
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi
echo -e "${GREEN}✓ kubectl found${NC}"

if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}✗ Cannot connect to Kubernetes cluster${NC}"
    echo "Please ensure cluster is running (minikube start)"
    exit 1
fi
echo -e "${GREEN}✓ Connected to Kubernetes cluster${NC}"

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo -e "${YELLOW}⚠ Namespace '$NAMESPACE' does not exist${NC}"
    read -p "Create namespace? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kubectl create namespace "$NAMESPACE"
        echo -e "${GREEN}✓ Namespace created${NC}"
    else
        echo -e "${RED}✗ Aborting${NC}"
        exit 1
    fi
fi

echo ""

# Create secret
if [ "$SKIP_SECRET" = false ]; then
    echo -e "${YELLOW}Creating PostgreSQL secret...${NC}"

    # Check if secret already exists
    if kubectl get secret postgres-secret -n "$NAMESPACE" &> /dev/null; then
        echo -e "${YELLOW}⚠ Secret 'postgres-secret' already exists${NC}"
        read -p "Delete and recreate? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kubectl delete secret postgres-secret -n "$NAMESPACE"
            echo -e "${GREEN}✓ Existing secret deleted${NC}"
        else
            echo -e "${BLUE}ℹ Using existing secret${NC}"
            SKIP_SECRET=true
        fi
    fi

    if [ "$SKIP_SECRET" = false ]; then
        # Prompt for password if not provided
        if [ -z "$DB_PASSWORD" ]; then
            echo ""
            echo "Enter PostgreSQL password (minimum 8 characters):"
            read -s DB_PASSWORD
            echo ""

            if [ ${#DB_PASSWORD} -lt 8 ]; then
                echo -e "${RED}✗ Password must be at least 8 characters${NC}"
                exit 1
            fi
        fi

        # Create secret
        if [ "$DRY_RUN" = true ]; then
            echo -e "${BLUE}[DRY RUN] Would create secret: postgres-secret${NC}"
        else
            kubectl create secret generic postgres-secret \
                --from-literal=password="$DB_PASSWORD" \
                -n "$NAMESPACE"
            echo -e "${GREEN}✓ Secret created: postgres-secret${NC}"
        fi
    fi
else
    echo -e "${BLUE}ℹ Skipping secret creation (--skip-secret)${NC}"

    # Verify secret exists
    if ! kubectl get secret postgres-secret -n "$NAMESPACE" &> /dev/null; then
        echo -e "${RED}✗ Secret 'postgres-secret' not found${NC}"
        echo "Please create secret first or remove --skip-secret flag"
        exit 1
    fi
    echo -e "${GREEN}✓ Secret exists: postgres-secret${NC}"
fi

echo ""

# Check storage class
echo -e "${YELLOW}Checking storage class...${NC}"
if ! kubectl get storageclass standard &> /dev/null; then
    echo -e "${RED}✗ Storage class 'standard' not found${NC}"
    echo "Available storage classes:"
    kubectl get storageclass
    echo ""
    echo "For Minikube, ensure it's started with:"
    echo "  minikube start --driver=docker"
    exit 1
fi
echo -e "${GREEN}✓ Storage class 'standard' available${NC}"

echo ""

# Deploy StatefulSet
echo -e "${YELLOW}Deploying PostgreSQL StatefulSet...${NC}"

if [ "$DRY_RUN" = true ]; then
    echo -e "${BLUE}[DRY RUN] Would apply StatefulSet${NC}"
    kubectl apply -f k8s/postgres/statefulset.yaml -n "$NAMESPACE" --dry-run=client
else
    kubectl apply -f k8s/postgres/statefulset.yaml -n "$NAMESPACE"
    echo -e "${GREEN}✓ StatefulSet deployed${NC}"
fi

echo ""

# Deploy Service
echo -e "${YELLOW}Deploying PostgreSQL Service...${NC}"

if [ "$DRY_RUN" = true ]; then
    echo -e "${BLUE}[DRY RUN] Would apply Service${NC}"
    kubectl apply -f k8s/postgres/service.yaml -n "$NAMESPACE" --dry-run=client
else
    kubectl apply -f k8s/postgres/service.yaml -n "$NAMESPACE"
    echo -e "${GREEN}✓ Service deployed${NC}"
fi

echo ""

# Wait for pod to be ready
if [ "$DRY_RUN" = false ]; then
    echo -e "${YELLOW}Waiting for PostgreSQL pod to be ready...${NC}"
    echo "This may take 30-60 seconds..."

    if kubectl wait --for=condition=ready pod/postgres-0 -n "$NAMESPACE" --timeout=120s 2>/dev/null; then
        echo -e "${GREEN}✓ PostgreSQL pod is ready${NC}"
    else
        echo -e "${RED}✗ Pod not ready after 120s${NC}"
        echo ""
        echo "Check pod status:"
        echo "  kubectl get pods -l app=postgres -n $NAMESPACE"
        echo ""
        echo "Check logs:"
        echo "  kubectl logs postgres-0 -n $NAMESPACE"
        exit 1
    fi

    echo ""

    # Show deployment status
    echo -e "${GREEN}╔═══════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          Deployment Successful!               ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════╝${NC}"
    echo ""

    echo "Deployment Summary:"
    echo "  Namespace:  $NAMESPACE"
    echo "  StatefulSet: postgres"
    echo "  Service:    postgres-service"
    echo "  PVC:        postgres-storage-postgres-0"
    echo "  Database:   tododb"
    echo "  User:       todouser"
    echo ""

    # Show resources
    echo "Resources:"
    kubectl get statefulset postgres -n "$NAMESPACE"
    echo ""
    kubectl get pods -l app=postgres -n "$NAMESPACE"
    echo ""
    kubectl get pvc -n "$NAMESPACE" | grep postgres
    echo ""
    kubectl get service postgres-service -n "$NAMESPACE"
    echo ""

    # Connection info
    echo -e "${BLUE}Connection Information:${NC}"
    echo "  Host: postgres-service"
    echo "  Port: 5432"
    echo "  Database: tododb"
    echo "  User: todouser"
    echo "  Connection String:"
    echo "    postgresql://todouser:PASSWORD@postgres-service:5432/tododb"
    echo ""

    # Next steps
    echo -e "${BLUE}Next Steps:${NC}"
    echo "  1. Test connection:"
    echo "     kubectl exec -it postgres-0 -n $NAMESPACE -- psql -U todouser -d tododb"
    echo ""
    echo "  2. Check logs:"
    echo "     kubectl logs postgres-0 -n $NAMESPACE"
    echo ""
    echo "  3. View PVC:"
    echo "     kubectl get pvc postgres-storage-postgres-0 -n $NAMESPACE"
    echo ""
    echo "  4. Deploy backend with connection string:"
    echo "     DATABASE_URL=postgresql://todouser:PASSWORD@postgres-service:5432/tododb"
    echo ""
else
    echo -e "${BLUE}[DRY RUN] Deployment simulation complete${NC}"
    echo ""
    echo "To actually deploy, run without --dry-run flag"
fi

echo -e "${GREEN}Done!${NC}"
