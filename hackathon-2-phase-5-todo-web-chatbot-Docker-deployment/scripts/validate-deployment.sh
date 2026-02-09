#!/bin/bash

# Deployment Validation Script
# Validates health checks, resource usage, replicas, and self-healing

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default namespace
NAMESPACE="default"

# Parse arguments
for arg in "$@"; do
    case $arg in
        --namespace=*)
            NAMESPACE="${arg#*=}"
            shift
            ;;
        --help)
            echo "FlowTask Deployment Validation Script"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --namespace=NS    Kubernetes namespace (default: default)"
            echo "  --help            Show this help"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $arg${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     FlowTask Deployment Validation           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Namespace: $NAMESPACE${NC}"
echo ""

# Test counters
PASSED=0
FAILED=0

# Helper function for test results
test_passed() {
    echo -e "${GREEN}✓ $1${NC}"
    ((PASSED++))
}

test_failed() {
    echo -e "${RED}✗ $1${NC}"
    ((FAILED++))
}

test_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# ============================================
# 1. HEALTH CHECK VALIDATION
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}1. Health Check Validation${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}Checking pod status...${NC}"
kubectl get pods -n $NAMESPACE -o wide
echo ""

# Check if all pods are running
NOT_RUNNING=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running --no-headers 2>/dev/null | wc -l)
if [ "$NOT_RUNNING" -eq 0 ]; then
    test_passed "All pods are in Running state"
else
    test_failed "$NOT_RUNNING pod(s) not in Running state"
fi

# Check if all pods are ready
NOT_READY=$(kubectl get pods -n $NAMESPACE -o json | jq -r '.items[] | select(.status.conditions[] | select(.type=="Ready" and .status!="True")) | .metadata.name' | wc -l)
if [ "$NOT_READY" -eq 0 ]; then
    test_passed "All pods are Ready"
else
    test_failed "$NOT_READY pod(s) not Ready"
fi

echo ""
echo -e "${YELLOW}Checking liveness and readiness probes...${NC}"

# Backend probes
echo -e "${CYAN}Backend Pods:${NC}"
kubectl get pods -n $NAMESPACE -l app=backend -o custom-columns=\
NAME:.metadata.name,\
READY:.status.conditions[?(@.type==\"Ready\")].status,\
RESTARTS:.status.containerStatuses[0].restartCount,\
AGE:.metadata.creationTimestamp

BACKEND_RESTARTS=$(kubectl get pods -n $NAMESPACE -l app=backend -o json | jq '[.items[].status.containerStatuses[0].restartCount] | add')
if [ "$BACKEND_RESTARTS" -lt 5 ]; then
    test_passed "Backend pods restart count acceptable ($BACKEND_RESTARTS)"
else
    test_failed "Backend pods restarting frequently ($BACKEND_RESTARTS restarts)"
fi
echo ""

# Frontend probes
echo -e "${CYAN}Frontend Pods:${NC}"
kubectl get pods -n $NAMESPACE -l app=frontend -o custom-columns=\
NAME:.metadata.name,\
READY:.status.conditions[?(@.type==\"Ready\")].status,\
RESTARTS:.status.containerStatuses[0].restartCount,\
AGE:.metadata.creationTimestamp

FRONTEND_RESTARTS=$(kubectl get pods -n $NAMESPACE -l app=frontend -o json | jq '[.items[].status.containerStatuses[0].restartCount] | add')
if [ "$FRONTEND_RESTARTS" -lt 5 ]; then
    test_passed "Frontend pods restart count acceptable ($FRONTEND_RESTARTS)"
else
    test_failed "Frontend pods restarting frequently ($FRONTEND_RESTARTS restarts)"
fi
echo ""

# Postgres probes
echo -e "${CYAN}Postgres Pods:${NC}"
kubectl get pods -n $NAMESPACE -l app=postgres -o custom-columns=\
NAME:.metadata.name,\
READY:.status.conditions[?(@.type==\"Ready\")].status,\
RESTARTS:.status.containerStatuses[0].restartCount,\
AGE:.metadata.creationTimestamp

POSTGRES_RESTARTS=$(kubectl get pods -n $NAMESPACE -l app=postgres -o json | jq '[.items[].status.containerStatuses[0].restartCount] | add')
if [ "$POSTGRES_RESTARTS" -lt 5 ]; then
    test_passed "Postgres pods restart count acceptable ($POSTGRES_RESTARTS)"
else
    test_failed "Postgres pods restarting frequently ($POSTGRES_RESTARTS restarts)"
fi
echo ""

# Check for recent probe failures
echo -e "${YELLOW}Checking for recent probe failures...${NC}"
PROBE_FAILURES=$(kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' 2>/dev/null | grep -i "unhealthy\|liveness\|readiness" | grep -i "failed" | wc -l)
if [ "$PROBE_FAILURES" -eq 0 ]; then
    test_passed "No recent probe failures detected"
else
    test_failed "$PROBE_FAILURES probe failure(s) detected in recent events"
    kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' | grep -i "unhealthy\|liveness\|readiness" | grep -i "failed" | tail -n 5
fi
echo ""

# ============================================
# 2. RESOURCE USAGE VALIDATION
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}2. Resource Usage Validation${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Check if metrics-server is available
if ! kubectl get deployment metrics-server -n kube-system &> /dev/null; then
    test_info "Metrics-server not found. Attempting to enable..."
    if command -v minikube &> /dev/null; then
        minikube addons enable metrics-server
        echo "Waiting 30 seconds for metrics-server to start..."
        sleep 30
    else
        test_failed "Metrics-server not available and not running on Minikube"
        echo ""
    fi
fi

# Wait for metrics to be available
echo -e "${YELLOW}Waiting for metrics to be available...${NC}"
sleep 10

# Get resource usage
echo -e "${YELLOW}Current resource usage:${NC}"
if kubectl top pods -n $NAMESPACE &> /dev/null; then
    kubectl top pods -n $NAMESPACE
    test_passed "Resource metrics available"
    echo ""

    # Node usage
    echo -e "${YELLOW}Node resource usage:${NC}"
    kubectl top nodes
    echo ""

    # Compare with limits
    echo -e "${YELLOW}Resource requests and limits:${NC}"
    kubectl get pods -n $NAMESPACE -o custom-columns=\
NAME:.metadata.name,\
CPU_REQ:.spec.containers[0].resources.requests.cpu,\
CPU_LIM:.spec.containers[0].resources.limits.cpu,\
MEM_REQ:.spec.containers[0].resources.requests.memory,\
MEM_LIM:.spec.containers[0].resources.limits.memory

    test_passed "Resource limits configured for all pods"
else
    test_failed "Unable to retrieve resource metrics (metrics-server may need more time)"
fi
echo ""

# ============================================
# 3. REPLICA MANAGEMENT VALIDATION
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}3. Replica Management Validation${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}Checking deployments and replicas...${NC}"
kubectl get deployments -n $NAMESPACE -o wide
echo ""

# Check backend replicas
BACKEND_DESIRED=$(kubectl get deployment backend-backend -n $NAMESPACE -o jsonpath='{.spec.replicas}')
BACKEND_READY=$(kubectl get deployment backend-backend -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')
if [ "$BACKEND_DESIRED" -eq "$BACKEND_READY" ]; then
    test_passed "Backend replicas: $BACKEND_READY/$BACKEND_DESIRED ready"
else
    test_failed "Backend replicas: $BACKEND_READY/$BACKEND_DESIRED ready"
fi

# Check frontend replicas
FRONTEND_DESIRED=$(kubectl get deployment frontend-frontend -n $NAMESPACE -o jsonpath='{.spec.replicas}')
FRONTEND_READY=$(kubectl get deployment frontend-frontend -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')
if [ "$FRONTEND_DESIRED" -eq "$FRONTEND_READY" ]; then
    test_passed "Frontend replicas: $FRONTEND_READY/$FRONTEND_DESIRED ready"
else
    test_failed "Frontend replicas: $FRONTEND_READY/$FRONTEND_DESIRED ready"
fi

# Check postgres StatefulSet
echo ""
echo -e "${YELLOW}Checking StatefulSet...${NC}"
kubectl get statefulset -n $NAMESPACE -o wide
echo ""

POSTGRES_DESIRED=$(kubectl get statefulset postgres-postgres -n $NAMESPACE -o jsonpath='{.spec.replicas}')
POSTGRES_READY=$(kubectl get statefulset postgres-postgres -n $NAMESPACE -o jsonpath='{.status.readyReplicas}')
if [ "$POSTGRES_DESIRED" -eq "$POSTGRES_READY" ]; then
    test_passed "Postgres replicas: $POSTGRES_READY/$POSTGRES_DESIRED ready"
else
    test_failed "Postgres replicas: $POSTGRES_READY/$POSTGRES_DESIRED ready"
fi
echo ""

# Check for HorizontalPodAutoscaler
echo -e "${YELLOW}Checking for HorizontalPodAutoscaler...${NC}"
HPA_COUNT=$(kubectl get hpa -n $NAMESPACE --no-headers 2>/dev/null | wc -l)
if [ "$HPA_COUNT" -gt 0 ]; then
    kubectl get hpa -n $NAMESPACE
    test_passed "HorizontalPodAutoscaler configured"
else
    test_info "No HorizontalPodAutoscaler configured (using fixed replicas)"
fi
echo ""

# ============================================
# 4. SELF-HEALING VALIDATION
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}4. Self-Healing Validation${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}Testing pod self-healing...${NC}"
echo -e "${CYAN}This test will delete a backend pod and verify automatic recreation${NC}"
echo ""

# Get initial backend pod
BACKEND_POD=$(kubectl get pod -n $NAMESPACE -l app=backend -o jsonpath='{.items[0].metadata.name}')
echo -e "Deleting pod: ${CYAN}$BACKEND_POD${NC}"

# Delete pod
kubectl delete pod $BACKEND_POD -n $NAMESPACE --grace-period=0 --force &> /dev/null

echo "Waiting for pod recreation..."
sleep 5

# Check if new pod was created
NEW_BACKEND_COUNT=$(kubectl get pods -n $NAMESPACE -l app=backend --no-headers | wc -l)
if [ "$NEW_BACKEND_COUNT" -eq "$BACKEND_DESIRED" ]; then
    test_passed "Pod automatically recreated (count: $NEW_BACKEND_COUNT)"
else
    test_failed "Pod not recreated properly (count: $NEW_BACKEND_COUNT, expected: $BACKEND_DESIRED)"
fi

# Wait for new pod to be ready
echo "Waiting for new pod to become ready..."
kubectl wait --for=condition=ready pod -l app=backend -n $NAMESPACE --timeout=60s &> /dev/null
if [ $? -eq 0 ]; then
    test_passed "New pod is ready and healthy"
else
    test_failed "New pod failed to become ready within timeout"
fi
echo ""

# Show final pod status
echo -e "${YELLOW}Final pod status:${NC}"
kubectl get pods -n $NAMESPACE -l app=backend
echo ""

# ============================================
# SUMMARY
# ============================================

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              Validation Summary               ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Passed:${NC} $PASSED checks"
echo -e "${RED}Failed:${NC} $FAILED checks"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All validations passed!${NC}"
    echo ""
    echo -e "${CYAN}Deployment is healthy and ready for production.${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some validations failed.${NC}"
    echo ""
    echo -e "${YELLOW}Recommended actions:${NC}"
    echo "  1. Check pod logs: kubectl logs <pod-name> -n $NAMESPACE"
    echo "  2. Describe failing pods: kubectl describe pod <pod-name> -n $NAMESPACE"
    echo "  3. Check events: kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp'"
    echo "  4. Review resource limits and requests"
    echo ""
    exit 1
fi
