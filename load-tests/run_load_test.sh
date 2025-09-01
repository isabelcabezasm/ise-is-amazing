#!/bin/bash

# Load Test Runner Script for Amazing API
# This script provides easy ways to run different types of load tests

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
API_URL="https://youareamazing-api.ambitiousmushroom-0229ef63.westus2.azurecontainerapps.io/"
USERS=5
REQUESTS=10
TEST_TYPE="simple"

# Function to print usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Run load tests for the Amazing API"
    echo ""
    echo "Options:"
    echo "  -u, --url URL       API base URL (default: http://localhost:8000)"
    echo "  -c, --users NUM     Number of concurrent users (default: 5)"
    echo "  -r, --requests NUM  Number of requests per user (default: 10)"
    echo "  -t, --type TYPE     Test type: simple, async, locust (default: simple)"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Test Types:"
    echo "  simple    - Basic load test using requests library (no extra deps)"
    echo "  async     - Advanced async load test using aiohttp (requires install)"
    echo "  locust    - Web-based load test using Locust framework (requires install)"
    echo ""
    echo "Examples:"
    echo "  $0                           # Run simple test with defaults"
    echo "  $0 -c 20 -r 50               # 20 users, 50 requests each"
    echo "  $0 -t async -c 50 -r 100     # Async test with 50 users"
    echo "  $0 -t locust                 # Start Locust web interface"
}

# Function to check if API is running
check_api() {
    echo -e "${BLUE}🔍 Checking if API is running at $API_URL...${NC}"
    
    if curl -sf "$API_URL/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ API is running and healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ API is not running or not healthy at $API_URL${NC}"
        echo -e "${YELLOW}💡 Make sure to start the API first with:${NC}"
        echo "   cd api-python && uvicorn main:app --host 0.0.0.0 --port 8000"
        return 1
    fi
}

# Function to install dependencies
install_deps() {
    local test_type=$1
    
    if [ "$test_type" = "simple" ]; then
        echo -e "${GREEN}✅ Simple test requires no additional dependencies${NC}"
        return 0
    fi
    
    if [ ! -f "requirements.txt" ]; then
        echo -e "${RED}❌ requirements.txt not found in load-tests directory${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📦 Installing dependencies for $test_type test...${NC}"
    
    # Check if we're in a virtual environment
    if [ -z "$VIRTUAL_ENV" ]; then
        echo -e "${YELLOW}⚠️  Warning: Not in a virtual environment${NC}"
        echo -e "${YELLOW}   Consider creating one: python -m venv load-test-env${NC}"
        echo -e "${YELLOW}   Then activate: source load-test-env/bin/activate${NC}"
    fi
    
    pip install -r requirements.txt
}

# Function to run simple test
run_simple_test() {
    echo -e "${BLUE}🚀 Running simple load test...${NC}"
    python load_test_simple.py --url "$API_URL" --users "$USERS" --requests "$REQUESTS" --health
}

# Function to run async test
run_async_test() {
    echo -e "${BLUE}🚀 Running async load test...${NC}"
    python load_test_async.py --url "$API_URL" --users "$USERS" --requests "$REQUESTS"
}

# Function to run locust test
run_locust_test() {
    echo -e "${BLUE}🚀 Starting Locust web interface...${NC}"
    echo -e "${YELLOW}📊 Open http://localhost:8089 in your browser to configure and run tests${NC}"
    echo -e "${YELLOW}🎯 Use target host: $API_URL${NC}"
    echo ""
    locust -f load_test_locust.py --host="$API_URL"
}

# Function to generate report
generate_report() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local report_file="load_test_report_$timestamp.txt"
    
    echo -e "${BLUE}📊 Generating load test report...${NC}"
    
    {
        echo "Load Test Report - Generated on $(date)"
        echo "=================================================="
        echo "Configuration:"
        echo "  - API URL: $API_URL"
        echo "  - Concurrent Users: $USERS"
        echo "  - Requests per User: $REQUESTS"
        echo "  - Test Type: $TEST_TYPE"
        echo ""
        echo "Test Results:"
        echo "See console output above for detailed results."
    } > "$report_file"
    
    echo -e "${GREEN}📄 Report saved to: $report_file${NC}"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)
            API_URL="$2"
            shift 2
            ;;
        -c|--users)
            USERS="$2"
            shift 2
            ;;
        -r|--requests)
            REQUESTS="$2"
            shift 2
            ;;
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Validate test type
if [[ ! "$TEST_TYPE" =~ ^(simple|async|locust)$ ]]; then
    echo -e "${RED}❌ Invalid test type: $TEST_TYPE${NC}"
    echo "Valid types: simple, async, locust"
    exit 1
fi

# Change to the load-tests directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

echo -e "${GREEN}🔥 Amazing API Load Test Runner${NC}"
echo "=================================="
echo "Configuration:"
echo "  - API URL: $API_URL"
echo "  - Concurrent Users: $USERS"
echo "  - Requests per User: $REQUESTS"
echo "  - Test Type: $TEST_TYPE"
echo ""

# Check if API is running (except for locust setup)
if ! check_api; then
    exit 1
fi

# Install dependencies if needed
if [ "$TEST_TYPE" != "simple" ]; then
    if ! install_deps "$TEST_TYPE"; then
        echo -e "${RED}❌ Failed to install dependencies${NC}"
        exit 1
    fi
fi

# Run the appropriate test
case $TEST_TYPE in
    simple)
        run_simple_test
        ;;
    async)
        run_async_test
        ;;
    locust)
        run_locust_test
        ;;
esac

# Generate report (except for locust which handles its own reporting)
if [ "$TEST_TYPE" != "locust" ]; then
    generate_report
fi

echo -e "${GREEN}✅ Load test completed!${NC}"
