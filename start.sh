#!/bin/bash

# Startup script for Enterprise Knowledge Graph Platform

echo "========================================================================"
echo "  Starting Enterprise Knowledge Graph & Ontology Platform"
echo "========================================================================"
echo

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}📡 Step 1: Starting API Server...${NC}"
cd "$SCRIPT_DIR"
source venv/bin/activate

# Start API in background
nohup python src/api/server.py > /dev/null 2>&1 &
API_PID=$!
echo "   API Server PID: $API_PID"
echo "   Waiting for API to start..."
sleep 3

# Check if API is running
if curl -s http://localhost:8000/api/v1/health > /dev/null; then
    echo -e "${GREEN}   ✅ API Server is running on http://localhost:8000${NC}"
else
    echo -e "${YELLOW}   ⚠️  API Server starting... (may take a few more seconds)${NC}"
fi

echo
echo -e "${BLUE}🎨 Step 2: Starting React Dashboard...${NC}"
cd "$SCRIPT_DIR/dashboard"

# Start dashboard in background
nohup npm run dev > /dev/null 2>&1 &
DASHBOARD_PID=$!
echo "   Dashboard PID: $DASHBOARD_PID"
echo "   Waiting for dashboard to start..."
sleep 5

echo
echo "========================================================================"
echo -e "${GREEN}✅ PLATFORM STARTED SUCCESSFULLY!${NC}"
echo "========================================================================"
echo
echo "Access the platform:"
echo -e "  🎨 Dashboard:       ${GREEN}http://localhost:3000${NC}"
echo -e "  📚 API Docs:        ${GREEN}http://localhost:8000/docs${NC}"
echo -e "  🔍 Health Check:    http://localhost:8000/api/v1/health"
echo
echo "To stop the platform:"
echo "  kill $API_PID $DASHBOARD_PID"
echo
echo "Or run:"
echo "  ./stop.sh"
echo
echo "========================================================================"
echo
