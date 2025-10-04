#!/bin/bash

# =============================================================================
# Local Development Server Startup Script
# =============================================================================
# This script starts the FastAPI server locally with hot reload enabled.
# It loads environment variables from .env and runs with uvicorn --reload.
#
# Usage: ./scripts/run_local.sh
# =============================================================================

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================================${NC}"
echo -e "${BLUE}Starting Economic Dashboard API - Development Server${NC}"
echo -e "${BLUE}======================================================================${NC}"

# Get the script directory and navigate to backend root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
cd "$BACKEND_DIR"

echo -e "\n${YELLOW}Working directory:${NC} $BACKEND_DIR"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}WARNING: .env file not found!${NC}"
    echo "Please create a .env file with required environment variables."
    echo "See .env.example for reference."
    exit 1
fi

echo -e "${GREEN}.env file found${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo -e "\n${YELLOW}WARNING: No virtual environment found!${NC}"
    echo "It's recommended to use a virtual environment."
    echo "Create one with: python -m venv venv"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Load environment variables from .env
echo -e "\n${YELLOW}Loading environment variables from .env...${NC}"
export $(grep -v '^#' .env | xargs)

# Check if required environment variables are set
required_vars=("DATABASE_URL" "REDIS_URL" "SECRET_KEY" "FRED_API_KEY")
missing_vars=()

for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        missing_vars+=("$var")
    fi
done

if [ ${#missing_vars[@]} -ne 0 ]; then
    echo -e "\n${YELLOW}ERROR: Missing required environment variables:${NC}"
    for var in "${missing_vars[@]}"; do
        echo "  - $var"
    done
    exit 1
fi

echo -e "${GREEN}All required environment variables are set${NC}"

# Check if dependencies are installed
echo -e "\n${YELLOW}Checking dependencies...${NC}"
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${YELLOW}WARNING: Dependencies not installed!${NC}"
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi
echo -e "${GREEN}Dependencies OK${NC}"

# Run migrations
echo -e "\n${YELLOW}Running database migrations...${NC}"
alembic upgrade head
echo -e "${GREEN}Migrations complete${NC}"

# Start the server
echo -e "\n${BLUE}======================================================================${NC}"
echo -e "${GREEN}Starting server with hot reload...${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""
echo -e "${YELLOW}Server will be available at:${NC}"
echo "  http://localhost:8000"
echo ""
echo -e "${YELLOW}API Documentation:${NC}"
echo "  http://localhost:8000/docs (Swagger UI)"
echo "  http://localhost:8000/redoc (ReDoc)"
echo ""
echo -e "${YELLOW}Press CTRL+C to stop the server${NC}"
echo -e "${BLUE}======================================================================${NC}"
echo ""

# Start uvicorn with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level info
