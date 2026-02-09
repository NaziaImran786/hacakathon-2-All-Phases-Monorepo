#!/bin/bash

# Helm Charts Validation Script
# Validates all Helm charts before deployment

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Helm Charts Validation Script            ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    echo -e "${RED}✗ Helm is not installed${NC}"
    echo "Please install Helm: https://helm.sh/docs/intro/install/"
    exit 1
fi
echo -e "${GREEN}✓ Helm installed: $(helm version --short)${NC}"
echo ""

# Function to lint chart
lint_chart() {
    local chart_path=$1
    local chart_name=$(basename $chart_path)

    echo -e "${YELLOW}Linting $chart_name chart...${NC}"

    if helm lint $chart_path; then
        echo -e "${GREEN}✓ $chart_name chart passes lint${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ $chart_name chart fails lint${NC}"
        ((FAILED++))
    fi
    echo ""
}

# Function to template chart
template_chart() {
    local chart_path=$1
    local chart_name=$(basename $chart_path)

    echo -e "${YELLOW}Rendering $chart_name templates...${NC}"

    if helm template test $chart_path > /dev/null; then
        echo -e "${GREEN}✓ $chart_name templates render successfully${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ $chart_name templates fail to render${NC}"
        ((FAILED++))
    fi
    echo ""
}

# Function to validate Kubernetes YAML
validate_k8s() {
    local chart_path=$1
    local chart_name=$(basename $chart_path)

    echo -e "${YELLOW}Validating $chart_name Kubernetes manifests...${NC}"

    if helm template test $chart_path | kubectl apply --dry-run=client -f - &> /dev/null; then
        echo -e "${GREEN}✓ $chart_name manifests are valid Kubernetes resources${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗ $chart_name manifests contain invalid Kubernetes resources${NC}"
        ((FAILED++))
    fi
    echo ""
}

# Validate each chart
for chart in helm/*/; do
    chart_name=$(basename $chart)

    echo -e "${BLUE}═══ Validating $chart_name chart ═══${NC}"
    echo ""

    # Check Chart.yaml exists
    if [ ! -f "$chart/Chart.yaml" ]; then
        echo -e "${RED}✗ Chart.yaml not found in $chart${NC}"
        ((FAILED++))
        continue
    fi
    echo -e "${GREEN}✓ Chart.yaml exists${NC}"

    # Check values.yaml exists
    if [ ! -f "$chart/values.yaml" ]; then
        echo -e "${RED}✗ values.yaml not found in $chart${NC}"
        ((FAILED++))
        continue
    fi
    echo -e "${GREEN}✓ values.yaml exists${NC}"

    # Check templates directory exists
    if [ ! -d "$chart/templates" ]; then
        echo -e "${RED}✗ templates/ directory not found in $chart${NC}"
        ((FAILED++))
        continue
    fi
    echo -e "${GREEN}✓ templates/ directory exists${NC}"

    echo ""

    # Run validations
    lint_chart "$chart"
    template_chart "$chart"

    # Only validate against Kubernetes if cluster is accessible
    if kubectl cluster-info &> /dev/null; then
        validate_k8s "$chart"
    else
        echo -e "${YELLOW}⚠ Skipping Kubernetes validation (cluster not accessible)${NC}"
        echo ""
    fi

    echo -e "${BLUE}═══════════════════════════════════════════════${NC}"
    echo ""
done

# Summary
echo -e "${BLUE}╔═══════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              Validation Summary               ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Passed:${NC} $PASSED checks"
echo -e "${RED}Failed:${NC} $FAILED checks"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All Helm charts are valid!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Build Docker images"
    echo "  2. Deploy with: helm install <release> ./helm/<chart>"
    echo "  3. Or use: ./scripts/deploy-all-helm.sh"
    echo ""
    exit 0
else
    echo -e "${RED}✗ Some validations failed. Please fix the issues.${NC}"
    echo ""
    exit 1
fi
