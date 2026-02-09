#!/bin/bash

# Dockerfile Validation Script
# Validates that Dockerfiles are correctly configured before building

set -e  # Exit on any error

echo "🔍 Validating Dockerfiles for FlowTask..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Function to print success
success() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASSED++))
}

# Function to print failure
failure() {
    echo -e "${RED}✗${NC} $1"
    ((FAILED++))
}

# Function to print warning
warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "=== Backend Dockerfile Validation ==="
echo ""

# Check if backend Dockerfile exists
if [ -f "backend/Dockerfile" ]; then
    success "backend/Dockerfile exists"
else
    failure "backend/Dockerfile not found"
    exit 1
fi

# Check if backend .dockerignore exists
if [ -f "backend/.dockerignore" ]; then
    success "backend/.dockerignore exists"
else
    failure "backend/.dockerignore not found"
fi

# Validate backend Dockerfile contents
if grep -q "FROM python:3.11-slim" backend/Dockerfile; then
    success "Backend uses python:3.11-slim base image"
else
    failure "Backend does not use python:3.11-slim base image"
fi

if grep -q "multi-stage" backend/Dockerfile || grep -q "as builder" backend/Dockerfile; then
    success "Backend uses multi-stage build"
else
    failure "Backend does not use multi-stage build"
fi

if grep -q "useradd.*appuser" backend/Dockerfile; then
    success "Backend creates non-root user (appuser)"
else
    failure "Backend does not create non-root user"
fi

if grep -q "USER appuser" backend/Dockerfile; then
    success "Backend switches to non-root user"
else
    failure "Backend does not switch to non-root user"
fi

if grep -q "EXPOSE 8000" backend/Dockerfile; then
    success "Backend exposes port 8000"
else
    failure "Backend does not expose port 8000"
fi

if grep -q "uvicorn" backend/Dockerfile && grep -q "app:app" backend/Dockerfile; then
    success "Backend CMD uses uvicorn with app:app"
else
    failure "Backend CMD not correctly configured"
fi

if grep -q "HEALTHCHECK" backend/Dockerfile; then
    success "Backend includes health check"
else
    warning "Backend does not include HEALTHCHECK instruction"
fi

echo ""
echo "=== Frontend Dockerfile Validation ==="
echo ""

# Check if frontend Dockerfile exists
if [ -f "frontend/Dockerfile" ]; then
    success "frontend/Dockerfile exists"
else
    failure "frontend/Dockerfile not found"
    exit 1
fi

# Check if frontend .dockerignore exists
if [ -f "frontend/.dockerignore" ]; then
    success "frontend/.dockerignore exists"
else
    failure "frontend/.dockerignore not found"
fi

# Validate frontend Dockerfile contents
if grep -q "FROM node:20-alpine" frontend/Dockerfile; then
    success "Frontend uses node:20-alpine base image"
else
    failure "Frontend does not use node:20-alpine base image"
fi

if grep -q "as deps" frontend/Dockerfile && grep -q "as builder" frontend/Dockerfile && grep -q "as runner" frontend/Dockerfile; then
    success "Frontend uses 3-stage multi-stage build (deps, builder, runner)"
else
    failure "Frontend does not use correct multi-stage build structure"
fi

if grep -q "adduser.*appuser" frontend/Dockerfile; then
    success "Frontend creates non-root user (appuser)"
else
    failure "Frontend does not create non-root user"
fi

if grep -q "USER appuser" frontend/Dockerfile; then
    success "Frontend switches to non-root user"
else
    failure "Frontend does not switch to non-root user"
fi

if grep -q "EXPOSE 3000" frontend/Dockerfile; then
    success "Frontend exposes port 3000"
else
    failure "Frontend does not expose port 3000"
fi

if grep -q "npm start" frontend/Dockerfile; then
    success "Frontend CMD uses npm start"
else
    failure "Frontend CMD not correctly configured"
fi

if grep -q "npm run build" frontend/Dockerfile; then
    success "Frontend includes production build step"
else
    failure "Frontend does not include production build step"
fi

if grep -q "HEALTHCHECK" frontend/Dockerfile; then
    success "Frontend includes health check"
else
    warning "Frontend does not include HEALTHCHECK instruction"
fi

if grep -q "NEXT_PUBLIC_API_URL" frontend/Dockerfile; then
    success "Frontend includes NEXT_PUBLIC_API_URL environment variable"
else
    warning "Frontend does not set NEXT_PUBLIC_API_URL (should be set at runtime)"
fi

echo ""
echo "=== .dockerignore Validation ==="
echo ""

# Check backend .dockerignore
if grep -q ".venv" backend/.dockerignore; then
    success "Backend .dockerignore excludes .venv"
else
    failure "Backend .dockerignore does not exclude .venv"
fi

if grep -q "__pycache__" backend/.dockerignore; then
    success "Backend .dockerignore excludes __pycache__"
else
    failure "Backend .dockerignore does not exclude __pycache__"
fi

if grep -q ".env" backend/.dockerignore; then
    success "Backend .dockerignore excludes .env"
else
    failure "Backend .dockerignore does not exclude .env files"
fi

# Check frontend .dockerignore
if grep -q "node_modules" frontend/.dockerignore; then
    success "Frontend .dockerignore excludes node_modules"
else
    failure "Frontend .dockerignore does not exclude node_modules"
fi

if grep -q ".next" frontend/.dockerignore; then
    success "Frontend .dockerignore excludes .next"
else
    failure "Frontend .dockerignore does not exclude .next"
fi

if grep -q ".env" frontend/.dockerignore; then
    success "Frontend .dockerignore excludes .env"
else
    failure "Frontend .dockerignore does not exclude .env files"
fi

echo ""
echo "=== Summary ==="
echo ""
echo -e "${GREEN}Passed:${NC} $PASSED checks"
echo -e "${RED}Failed:${NC} $FAILED checks"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All critical validations passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start Docker Desktop"
    echo "2. Build images: docker build -t backend:latest ./backend"
    echo "3. Build images: docker build -t frontend:latest ./frontend"
    echo "4. Verify image sizes: docker images | grep -E 'backend|frontend'"
    echo ""
    exit 0
else
    echo ""
    echo -e "${RED}✗ Some validations failed. Please fix the issues before building.${NC}"
    echo ""
    exit 1
fi
