#!/bin/bash

# Stop script for Enterprise Knowledge Graph Platform

echo "========================================================================"
echo "  Stopping Enterprise Knowledge Graph & Ontology Platform"
echo "========================================================================"
echo

# Kill API server
API_PIDS=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$API_PIDS" ]; then
    echo "🛑 Stopping API Server (port 8000)..."
    kill $API_PIDS 2>/dev/null
    echo "   ✅ API Server stopped"
else
    echo "   ℹ️  API Server not running"
fi

# Kill Dashboard
DASHBOARD_PIDS=$(lsof -ti:3000 2>/dev/null)
if [ ! -z "$DASHBOARD_PIDS" ]; then
    echo "🛑 Stopping Dashboard (port 3000)..."
    kill $DASHBOARD_PIDS 2>/dev/null
    echo "   ✅ Dashboard stopped"
else
    echo "   ℹ️  Dashboard not running"
fi

# Kill any remaining vite processes
VITE_PIDS=$(pgrep -f "vite" 2>/dev/null)
if [ ! -z "$VITE_PIDS" ]; then
    echo "🛑 Stopping remaining Vite processes..."
    kill $VITE_PIDS 2>/dev/null
fi

echo
echo "========================================================================"
echo "✅ All services stopped"
echo "========================================================================"
echo
