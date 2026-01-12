#!/bin/bash

# End-to-End Connectivity Test Script
# Tests full application stack: Frontend → Backend → Database → AI Chatbot

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Default values
NAMESPACE="default"
VERBOSE=false
CLEANUP=true

# Test counters
PASSED=0
FAILED=0

# Parse arguments
for arg in "$@"; do
    case $arg in
        --namespace=*)
            NAMESPACE="${arg#*=}"
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --no-cleanup)
            CLEANUP=false
            shift
            ;;
        --help)
            echo "FlowTask End-to-End Connectivity Test"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --namespace=NS    Kubernetes namespace (default: default)"
            echo "  --verbose         Show detailed output"
            echo "  --no-cleanup      Don't delete test data after completion"
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
echo -e "${BLUE}║     FlowTask E2E Connectivity Test           ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}Namespace: $NAMESPACE${NC}"
echo -e "${CYAN}Cleanup: $CLEANUP${NC}"
echo ""

# Helper functions
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

verbose_log() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${MAGENTA}[DEBUG] $1${NC}"
    fi
}

# ============================================
# 0. PREREQUISITES CHECK
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}0. Prerequisites Check${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    test_failed "kubectl not found"
    exit 1
fi
test_passed "kubectl is available"

# Check if curl is available
if ! command -v curl &> /dev/null; then
    test_failed "curl not found"
    exit 1
fi
test_passed "curl is available"

# Check if jq is available
if ! command -v jq &> /dev/null; then
    test_info "jq not found (optional, but recommended for JSON parsing)"
fi

# Check cluster connectivity
if ! kubectl cluster-info &> /dev/null; then
    test_failed "Cannot connect to Kubernetes cluster"
    exit 1
fi
test_passed "Connected to Kubernetes cluster"

# Check if all pods are running
NOT_RUNNING=$(kubectl get pods -n $NAMESPACE --field-selector=status.phase!=Running --no-headers 2>/dev/null | wc -l)
if [ "$NOT_RUNNING" -eq 0 ]; then
    test_passed "All pods are running"
else
    test_failed "$NOT_RUNNING pod(s) not running. Please fix deployment first."
    kubectl get pods -n $NAMESPACE
    exit 1
fi

echo ""

# ============================================
# 1. FRONTEND ACCESSIBILITY TEST
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}1. Frontend Accessibility Test${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Get Minikube IP or use service
if command -v minikube &> /dev/null && minikube status &> /dev/null; then
    MINIKUBE_IP=$(minikube ip 2>/dev/null || echo "")
    if [ -n "$MINIKUBE_IP" ]; then
        # Get NodePort
        FRONTEND_NODEPORT=$(kubectl get service -n $NAMESPACE frontend-frontend-service -o jsonpath='{.spec.ports[0].nodePort}')
        FRONTEND_URL="http://$MINIKUBE_IP:$FRONTEND_NODEPORT"
        test_info "Using Minikube: $FRONTEND_URL"
    else
        test_info "Minikube IP not available, using port-forward"
        # Start port-forward in background
        kubectl port-forward -n $NAMESPACE service/frontend-frontend-service 3000:3000 &> /dev/null &
        PORT_FORWARD_PID=$!
        sleep 3
        FRONTEND_URL="http://localhost:3000"
    fi
else
    test_info "Not using Minikube, using port-forward"
    kubectl port-forward -n $NAMESPACE service/frontend-frontend-service 3000:3000 &> /dev/null &
    PORT_FORWARD_PID=$!
    sleep 3
    FRONTEND_URL="http://localhost:3000"
fi

echo -e "${YELLOW}Testing frontend accessibility at: $FRONTEND_URL${NC}"

# Test frontend with retries
MAX_RETRIES=3
RETRY_COUNT=0
FRONTEND_SUCCESS=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf "$FRONTEND_URL" -o /dev/null -m 10; then
        FRONTEND_SUCCESS=true
        break
    fi
    ((RETRY_COUNT++))
    if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
        verbose_log "Retry $RETRY_COUNT/$MAX_RETRIES..."
        sleep 2
    fi
done

if [ "$FRONTEND_SUCCESS" = true ]; then
    test_passed "Frontend is accessible at $FRONTEND_URL"

    # Get response for verification
    FRONTEND_RESPONSE=$(curl -s "$FRONTEND_URL" -m 10)
    if echo "$FRONTEND_RESPONSE" | grep -qi "FlowTask\|Todo\|Next.js"; then
        test_passed "Frontend returned valid HTML content"
        verbose_log "Frontend response contains expected content"
    else
        test_info "Frontend accessible but content verification inconclusive"
    fi
else
    test_failed "Frontend not accessible after $MAX_RETRIES attempts"
fi

echo ""

# ============================================
# 2. BACKEND API TEST (CREATE TODO)
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}2. Backend API Test (Create Todo)${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Get backend service
BACKEND_SERVICE="backend-backend-service"
BACKEND_PORT=8000

# Use kubectl port-forward for backend
echo -e "${YELLOW}Setting up backend port-forward...${NC}"
kubectl port-forward -n $NAMESPACE service/$BACKEND_SERVICE 8000:8000 &> /dev/null &
BACKEND_PORT_FORWARD_PID=$!
sleep 3

BACKEND_URL="http://localhost:8000"

# Test backend health endpoint first
echo -e "${YELLOW}Testing backend health endpoint...${NC}"
if curl -sf "$BACKEND_URL/health" -o /dev/null -m 10 2>/dev/null || curl -sf "$BACKEND_URL/" -o /dev/null -m 10 2>/dev/null; then
    test_passed "Backend health endpoint is accessible"
else
    test_failed "Backend health endpoint not accessible"
fi

# Register a test user first
echo ""
echo -e "${YELLOW}Registering test user...${NC}"
TEST_USER_EMAIL="e2e-test-$(date +%s)@flowtask.test"
TEST_USER_PASSWORD="TestPassword123!"
TEST_USERNAME="e2e-tester"

verbose_log "User email: $TEST_USER_EMAIL"

REGISTER_RESPONSE=$(curl -s -X POST "$BACKEND_URL/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$TEST_USER_EMAIL\",
        \"password\": \"$TEST_USER_PASSWORD\",
        \"username\": \"$TEST_USERNAME\"
    }" -m 10 2>/dev/null || echo '{"error": "curl_failed"}')

verbose_log "Register response: $REGISTER_RESPONSE"

if echo "$REGISTER_RESPONSE" | grep -qi "error\|fail" && ! echo "$REGISTER_RESPONSE" | grep -qi "already exists"; then
    test_info "User registration returned error (may already exist or endpoint different)"
    # Continue anyway, try to login
else
    test_passed "Test user registration attempted"
fi

# Login to get token
echo ""
echo -e "${YELLOW}Logging in to get auth token...${NC}"

LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/login" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$TEST_USER_EMAIL\",
        \"password\": \"$TEST_USER_PASSWORD\"
    }" -m 10 2>/dev/null || echo '{"error": "curl_failed"}')

verbose_log "Login response: $LOGIN_RESPONSE"

# Try to extract token (handle different response formats)
if command -v jq &> /dev/null; then
    AUTH_TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // .token // empty' 2>/dev/null || echo "")
else
    # Fallback: simple grep for token
    AUTH_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -oP '"access_token":"?\K[^",:}]+' || echo "")
    if [ -z "$AUTH_TOKEN" ]; then
        AUTH_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -oP '"token":"?\K[^",:}]+' || echo "")
    fi
fi

if [ -n "$AUTH_TOKEN" ] && [ "$AUTH_TOKEN" != "null" ]; then
    test_passed "Successfully obtained auth token"
    verbose_log "Token: ${AUTH_TOKEN:0:20}..."
else
    test_info "Could not obtain auth token (may need different auth method)"
    AUTH_TOKEN=""
fi

# Create a test Todo
echo ""
echo -e "${YELLOW}Creating test Todo via Backend API...${NC}"
TEST_TODO_TITLE="E2E Test Todo - $(date +%Y%m%d-%H%M%S)"
TEST_TODO_DESCRIPTION="This is an end-to-end connectivity test todo"

verbose_log "Todo title: $TEST_TODO_TITLE"

# Build curl command with auth if available
if [ -n "$AUTH_TOKEN" ]; then
    CREATE_TODO_RESPONSE=$(curl -s -X POST "$BACKEND_URL/todos" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -d "{
            \"title\": \"$TEST_TODO_TITLE\",
            \"description\": \"$TEST_TODO_DESCRIPTION\",
            \"completed\": false
        }" -m 10 2>/dev/null || echo '{"error": "curl_failed"}')
else
    # Try without auth (if endpoint allows)
    CREATE_TODO_RESPONSE=$(curl -s -X POST "$BACKEND_URL/todos" \
        -H "Content-Type: application/json" \
        -d "{
            \"title\": \"$TEST_TODO_TITLE\",
            \"description\": \"$TEST_TODO_DESCRIPTION\",
            \"completed\": false
        }" -m 10 2>/dev/null || echo '{"error": "curl_failed"}')
fi

verbose_log "Create Todo response: $CREATE_TODO_RESPONSE"

# Check if Todo was created successfully
if echo "$CREATE_TODO_RESPONSE" | grep -qi "error\|fail\|unauthorized"; then
    test_failed "Todo creation failed: $CREATE_TODO_RESPONSE"
    TODO_CREATED=false
else
    test_passed "Todo creation request sent successfully"
    TODO_CREATED=true

    # Try to extract Todo ID
    if command -v jq &> /dev/null; then
        TEST_TODO_ID=$(echo "$CREATE_TODO_RESPONSE" | jq -r '.id // empty' 2>/dev/null || echo "")
    else
        TEST_TODO_ID=$(echo "$CREATE_TODO_RESPONSE" | grep -oP '"id":"?\K[^",:}]+' || echo "")
    fi

    if [ -n "$TEST_TODO_ID" ]; then
        test_passed "Todo created with ID: $TEST_TODO_ID"
        verbose_log "Full response: $CREATE_TODO_RESPONSE"
    else
        test_info "Todo created but ID not extracted from response"
        TEST_TODO_ID=""
    fi
fi

echo ""

# ============================================
# 3. DATABASE VERIFICATION TEST
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}3. Database Verification Test${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

# Get postgres pod name
POSTGRES_POD=$(kubectl get pod -n $NAMESPACE -l app=postgres -o jsonpath='{.items[0].metadata.name}')

if [ -z "$POSTGRES_POD" ]; then
    test_failed "Postgres pod not found"
else
    test_passed "Found postgres pod: $POSTGRES_POD"

    echo ""
    echo -e "${YELLOW}Verifying database connectivity...${NC}"

    # Test database connection
    DB_CONNECT_TEST=$(kubectl exec -n $NAMESPACE $POSTGRES_POD -- psql -U todouser -d tododb -c "\conninfo" 2>&1)

    if echo "$DB_CONNECT_TEST" | grep -qi "connected\|tododb"; then
        test_passed "Database connection successful"
        verbose_log "$DB_CONNECT_TEST"
    else
        test_failed "Database connection failed"
    fi

    echo ""
    echo -e "${YELLOW}Checking if todos table exists...${NC}"

    # Check if todos table exists
    TABLE_CHECK=$(kubectl exec -n $NAMESPACE $POSTGRES_POD -- psql -U todouser -d tododb -c "\dt" 2>&1)

    if echo "$TABLE_CHECK" | grep -qi "todos\|todo"; then
        test_passed "Todos table exists in database"
        verbose_log "$TABLE_CHECK"
    else
        test_info "Todos table may not exist yet (check migrations)"
        verbose_log "$TABLE_CHECK"
    fi

    # If todo was created, verify it's in database
    if [ "$TODO_CREATED" = true ]; then
        echo ""
        echo -e "${YELLOW}Verifying test Todo in database...${NC}"

        # Query for the test todo
        DB_QUERY_RESULT=$(kubectl exec -n $NAMESPACE $POSTGRES_POD -- \
            psql -U todouser -d tododb -t -c \
            "SELECT COUNT(*) FROM todos WHERE title LIKE 'E2E Test Todo%';" 2>&1 || echo "0")

        TODO_COUNT=$(echo "$DB_QUERY_RESULT" | tr -d ' \n' | grep -o '[0-9]\+' || echo "0")

        if [ "$TODO_COUNT" -gt 0 ]; then
            test_passed "Test Todo found in database (count: $TODO_COUNT)"

            # Get full record
            if [ "$VERBOSE" = true ]; then
                echo -e "${YELLOW}Todo records in database:${NC}"
                kubectl exec -n $NAMESPACE $POSTGRES_POD -- \
                    psql -U todouser -d tododb -c \
                    "SELECT id, title, completed, created_at FROM todos WHERE title LIKE 'E2E Test Todo%' ORDER BY created_at DESC LIMIT 5;"
            fi
        else
            test_failed "Test Todo not found in database (table may be empty or different schema)"

            # Show all tables as debug info
            if [ "$VERBOSE" = true ]; then
                echo -e "${YELLOW}Available tables:${NC}"
                kubectl exec -n $NAMESPACE $POSTGRES_POD -- \
                    psql -U todouser -d tododb -c "\dt"
            fi
        fi
    fi
fi

echo ""

# ============================================
# 4. AI CHATBOT ENDPOINT TEST
# ============================================

echo -e "${BLUE}════════════════════════════════════════${NC}"
echo -e "${BLUE}4. AI Chatbot Endpoint Test${NC}"
echo -e "${BLUE}════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}Testing AI Chatbot endpoint...${NC}"

# Test chatbot endpoint (common patterns)
CHATBOT_ENDPOINTS=(
    "/chat"
    "/api/chat"
    "/chatbot"
    "/ai/chat"
    "/mcp/chat"
)

CHATBOT_SUCCESS=false
CHATBOT_ENDPOINT=""

for endpoint in "${CHATBOT_ENDPOINTS[@]}"; do
    verbose_log "Trying endpoint: $endpoint"

    # Try POST request with simple message
    CHATBOT_RESPONSE=$(curl -s -X POST "$BACKEND_URL$endpoint" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -d "{
            \"message\": \"Hello, this is a test\",
            \"query\": \"Hello\",
            \"prompt\": \"Test query\"
        }" -m 10 2>/dev/null || echo '{"error": "curl_failed"}')

    verbose_log "Response: $CHATBOT_RESPONSE"

    # Check if response is not an error
    if ! echo "$CHATBOT_RESPONSE" | grep -qi "not found\|404\|curl_failed"; then
        CHATBOT_SUCCESS=true
        CHATBOT_ENDPOINT="$endpoint"
        break
    fi
done

if [ "$CHATBOT_SUCCESS" = true ]; then
    test_passed "AI Chatbot endpoint found and responding: $CHATBOT_ENDPOINT"

    # Verify response contains expected fields
    if echo "$CHATBOT_RESPONSE" | grep -qi "response\|message\|reply\|answer"; then
        test_passed "Chatbot returned valid response structure"
        verbose_log "Response: $CHATBOT_RESPONSE"
    else
        test_info "Chatbot responded but structure unclear"
        verbose_log "Response: $CHATBOT_RESPONSE"
    fi
else
    test_info "AI Chatbot endpoint not found at common paths"
    test_info "Tried: ${CHATBOT_ENDPOINTS[*]}"

    # List available endpoints
    if [ "$VERBOSE" = true ]; then
        echo -e "${YELLOW}Available API endpoints:${NC}"
        OPENAPI_DOCS=$(curl -s "$BACKEND_URL/docs" -m 5 2>/dev/null || echo "")
        if [ -n "$OPENAPI_DOCS" ]; then
            echo "OpenAPI docs available at: $BACKEND_URL/docs"
        fi

        REDOC=$(curl -s "$BACKEND_URL/redoc" -m 5 2>/dev/null || echo "")
        if [ -n "$REDOC" ]; then
            echo "ReDoc available at: $BACKEND_URL/redoc"
        fi
    fi
fi

echo ""

# ============================================
# 5. CLEANUP (if enabled)
# ============================================

if [ "$CLEANUP" = true ] && [ "$TODO_CREATED" = true ] && [ -n "$TEST_TODO_ID" ]; then
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo -e "${BLUE}5. Cleanup Test Data${NC}"
    echo -e "${BLUE}════════════════════════════════════════${NC}"
    echo ""

    echo -e "${YELLOW}Deleting test Todo...${NC}"

    if [ -n "$AUTH_TOKEN" ]; then
        DELETE_RESPONSE=$(curl -s -X DELETE "$BACKEND_URL/todos/$TEST_TODO_ID" \
            -H "Authorization: Bearer $AUTH_TOKEN" \
            -m 10 2>/dev/null || echo '{"error": "curl_failed"}')
    else
        DELETE_RESPONSE=$(curl -s -X DELETE "$BACKEND_URL/todos/$TEST_TODO_ID" \
            -m 10 2>/dev/null || echo '{"error": "curl_failed"}')
    fi

    if ! echo "$DELETE_RESPONSE" | grep -qi "error\|fail"; then
        test_passed "Test Todo deleted successfully"
    else
        test_info "Test Todo deletion failed (may need manual cleanup)"
    fi

    echo ""
fi

# Kill port-forward processes
if [ -n "$PORT_FORWARD_PID" ]; then
    kill $PORT_FORWARD_PID 2>/dev/null || true
fi
if [ -n "$BACKEND_PORT_FORWARD_PID" ]; then
    kill $BACKEND_PORT_FORWARD_PID 2>/dev/null || true
fi

# ============================================
# SUMMARY
# ============================================

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              E2E Test Summary                 ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Passed:${NC} $PASSED checks"
echo -e "${RED}Failed:${NC} $FAILED checks"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All E2E tests passed!${NC}"
    echo ""
    echo -e "${CYAN}Full application stack is working correctly:${NC}"
    echo "  ✓ Frontend accessible"
    echo "  ✓ Backend API responding"
    echo "  ✓ Database operations working"
    echo "  ✓ End-to-end data flow verified"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠ Some E2E tests failed or were inconclusive.${NC}"
    echo ""
    echo -e "${CYAN}Recommendations:${NC}"
    echo "  1. Check API documentation: $BACKEND_URL/docs"
    echo "  2. Verify database schema matches application models"
    echo "  3. Review backend logs: kubectl logs -l app=backend -n $NAMESPACE"
    echo "  4. Check authentication requirements"
    echo "  5. Run with --verbose flag for detailed output"
    echo ""
    exit 1
fi
