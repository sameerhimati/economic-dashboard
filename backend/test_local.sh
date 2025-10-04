#!/bin/bash

# =============================================================================
# Economic Dashboard Backend API Test Suite
# =============================================================================
# This script runs comprehensive integration tests for the FastAPI backend.
# It checks API availability, runs pytest tests, and provides a clear summary.
#
# USAGE:
#   ./test_local.sh                    # Test against localhost:8000
#   API_BASE_URL=<url> ./test_local.sh # Test against custom URL
#
# PREREQUISITES:
#   1. Install dependencies: pip install -r requirements-dev.txt
#   2. Start the API server (if testing locally)
#   3. Ensure .env file is configured with proper credentials
#
# EXAMPLES:
#   ./test_local.sh                                        # Local testing
#   API_BASE_URL=https://your-app.railway.app ./test_local.sh  # Railway testing
# =============================================================================

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Symbols
CHECK_MARK="✅"
CROSS_MARK="❌"
INFO_MARK="ℹ️"
RUNNING_MARK="🔄"

# Configuration
DEFAULT_API_URL="http://localhost:8000"
API_URL="${API_BASE_URL:-$DEFAULT_API_URL}"

# =============================================================================
# Helper Functions
# =============================================================================

print_header() {
    echo ""
    echo -e "${BLUE}=========================================${NC}"
    echo -e "${BOLD}$1${NC}"
    echo -e "${BLUE}=========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}${CHECK_MARK} $1${NC}"
}

print_error() {
    echo -e "${RED}${CROSS_MARK} $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}${INFO_MARK}  $1${NC}"
}

print_running() {
    echo -e "${YELLOW}${RUNNING_MARK} $1${NC}"
}

# =============================================================================
# Main Script
# =============================================================================

print_header "Backend API Test Suite"

# Check if .env file exists and load it
if [ -f .env ]; then
    print_info "Loading environment variables from .env file..."
    set -a
    source .env
    set +a
    print_success "Environment variables loaded"
else
    print_warning "No .env file found, using defaults"
fi

# Display configuration
echo ""
print_info "Test Configuration:"
echo "  API URL: $API_URL"
echo "  Environment: ${ENVIRONMENT:-not set}"
echo ""

# Check if API is running
print_running "Checking API availability at $API_URL..."
echo ""

# Try to reach the health/ping endpoint
if command -v curl &> /dev/null; then
    response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/health/ping" --max-time 5 2>/dev/null)

    if [ "$response" = "200" ]; then
        print_success "API is running and responsive"

        # Get API info
        api_info=$(curl -s "$API_URL/" 2>/dev/null)
        if [ ! -z "$api_info" ]; then
            api_name=$(echo $api_info | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
            api_version=$(echo $api_info | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
            if [ ! -z "$api_name" ]; then
                echo "  API Name: $api_name"
                echo "  Version: $api_version"
            fi
        fi
    else
        print_error "API is not responding (HTTP $response)"
        print_warning "Make sure the API is running at $API_URL"
        print_info "Start the API with: uvicorn app.main:app --reload"
        echo ""
        exit 1
    fi
else
    print_warning "curl not found, skipping API availability check"
fi

echo ""

# Check if pytest is installed
print_running "Checking test dependencies..."
echo ""

if ! python -c "import pytest" 2>/dev/null; then
    print_error "pytest is not installed"
    print_info "Install with: pip install -r requirements-dev.txt"
    echo ""
    exit 1
fi

if ! python -c "import httpx" 2>/dev/null; then
    print_error "httpx is not installed"
    print_info "Install with: pip install -r requirements-dev.txt"
    echo ""
    exit 1
fi

print_success "Test dependencies are installed"
echo ""

# Run the tests
print_header "Running Test Suite"

# Set the API_BASE_URL environment variable for tests
export API_BASE_URL="$API_URL"

# Run pytest with verbose output and capture results
pytest test_api.py -v --tb=short --color=yes 2>&1 | tee .test_output.tmp

# Capture exit code
TEST_EXIT_CODE=${PIPESTATUS[0]}

echo ""
print_header "Test Summary"

# Parse test results
if [ -f .test_output.tmp ]; then
    # Count passed and failed tests by marker
    health_passed=$(grep -c "test_api.py::TestHealth.*PASSED" .test_output.tmp || echo "0")
    health_failed=$(grep -c "test_api.py::TestHealth.*FAILED" .test_output.tmp || echo "0")

    auth_passed=$(grep -c "test_api.py::TestAuthentication.*PASSED" .test_output.tmp || echo "0")
    auth_failed=$(grep -c "test_api.py::TestAuthentication.*FAILED" .test_output.tmp || echo "0")

    data_passed=$(grep -c "test_api.py::TestFredData.*PASSED" .test_output.tmp || echo "0")
    data_failed=$(grep -c "test_api.py::TestFredData.*FAILED" .test_output.tmp || echo "0")

    cache_passed=$(grep -c "test_api.py::TestCaching.*PASSED" .test_output.tmp || echo "0")
    cache_failed=$(grep -c "test_api.py::TestCaching.*FAILED" .test_output.tmp || echo "0")

    integration_passed=$(grep -c "test_api.py::TestIntegration.*PASSED" .test_output.tmp || echo "0")
    integration_failed=$(grep -c "test_api.py::TestIntegration.*FAILED" .test_output.tmp || echo "0")

    # Calculate totals
    health_total=$((health_passed + health_failed))
    auth_total=$((auth_passed + auth_failed))
    data_total=$((data_passed + data_failed))
    cache_total=$((cache_passed + cache_failed))
    integration_total=$((integration_passed + integration_failed))

    # Display category summaries
    if [ $health_total -gt 0 ]; then
        if [ $health_failed -eq 0 ]; then
            print_success "Health checks passed ($health_passed/$health_total)"
        else
            print_error "Health checks failed ($health_passed/$health_total passed)"
        fi
    fi

    if [ $auth_total -gt 0 ]; then
        if [ $auth_failed -eq 0 ]; then
            print_success "Authentication tests passed ($auth_passed/$auth_total)"
        else
            print_error "Authentication tests failed ($auth_passed/$auth_total passed)"
        fi
    fi

    if [ $data_total -gt 0 ]; then
        if [ $data_failed -eq 0 ]; then
            print_success "Data endpoint tests passed ($data_passed/$data_total)"
        else
            print_error "Data endpoint tests failed ($data_passed/$data_total passed)"
        fi
    fi

    if [ $cache_total -gt 0 ]; then
        if [ $cache_failed -eq 0 ]; then
            print_success "Caching tests passed ($cache_passed/$cache_total)"
        else
            print_error "Caching tests failed ($cache_passed/$cache_total passed)"
        fi
    fi

    if [ $integration_total -gt 0 ]; then
        if [ $integration_failed -eq 0 ]; then
            print_success "Integration tests passed ($integration_passed/$integration_total)"
        else
            print_error "Integration tests failed ($integration_passed/$integration_total passed)"
        fi
    fi

    echo ""

    # Extract final summary from pytest
    summary_line=$(grep -E "^=.*=.*in.*s" .test_output.tmp | tail -1)
    if [ ! -z "$summary_line" ]; then
        echo -e "${BOLD}Overall Result:${NC}"
        if [ $TEST_EXIT_CODE -eq 0 ]; then
            print_success "$summary_line"
        else
            print_error "$summary_line"
        fi
    fi

    # Clean up temp file
    rm -f .test_output.tmp
fi

echo ""

# Display health status
print_info "Component Health Status:"

# Check health endpoint for detailed status
if command -v curl &> /dev/null; then
    health_response=$(curl -s "$API_URL/health" 2>/dev/null)

    if [ ! -z "$health_response" ]; then
        # Parse health status (basic parsing)
        db_status=$(echo $health_response | grep -o '"database":{"status":"[^"]*"' | cut -d'"' -f6)
        redis_status=$(echo $health_response | grep -o '"redis":{"status":"[^"]*"' | cut -d'"' -f6)
        fred_status=$(echo $health_response | grep -o '"fred_api":{"status":"[^"]*"' | cut -d'"' -f6)

        if [ "$db_status" = "healthy" ]; then
            print_success "PostgreSQL connected"
        elif [ ! -z "$db_status" ]; then
            print_error "PostgreSQL: $db_status"
        fi

        if [ "$redis_status" = "healthy" ]; then
            print_success "Redis connected"
        elif [ ! -z "$redis_status" ]; then
            print_error "Redis: $redis_status"
        fi

        if [ "$fred_status" = "configured" ] || [ "$fred_status" = "healthy" ]; then
            print_success "FRED API configured"
        elif [ ! -z "$fred_status" ]; then
            print_error "FRED API: $fred_status"
        fi
    fi
fi

echo ""
print_header "Test Run Complete"

# Exit with pytest's exit code
exit $TEST_EXIT_CODE
