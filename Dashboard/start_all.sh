#!/bin/bash

# Start both dashboard and test app

echo "=========================================="
echo "  Vehicle Dashboard Complete Setup"
echo "=========================================="

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Check ports
if ! check_port 5000; then
    echo "Dashboard may already be running on port 5000"
fi

if ! check_port 5001; then
    echo "Test app may already be running on port 5001"
fi

echo ""
echo "Starting applications..."
echo ""

# Function to cleanup
cleanup() {
    echo ""
    echo "🛑 Stopping applications..."
    
    # Kill all child processes
    if [ ! -z "$DASHBOARD_PID" ]; then
        echo "Stopping dashboard (PID: $DASHBOARD_PID)..."
        kill -TERM $DASHBOARD_PID 2>/dev/null
        # Also kill the Python process specifically
        pkill -f "python.*app.py" 2>/dev/null
    fi
    
    if [ ! -z "$TEST_APP_PID" ]; then
        echo "Stopping test app (PID: $TEST_APP_PID)..."
        kill -TERM $TEST_APP_PID 2>/dev/null
    fi
    
    # Kill any remaining Python processes from our apps
    pkill -f "python.*Dashboard.*app.py" 2>/dev/null
    
    # Wait a moment for graceful shutdown
    sleep 1
    
    # Force kill if still running
    if [ ! -z "$DASHBOARD_PID" ]; then
        kill -KILL $DASHBOARD_PID 2>/dev/null
    fi
    
    if [ ! -z "$TEST_APP_PID" ]; then
        kill -KILL $TEST_APP_PID 2>/dev/null
    fi
    
    echo "✅ Applications stopped."
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM EXIT

# Start dashboard in background
echo "🚗 Starting Vehicle Dashboard (Port 5000)..."
./start.sh &
DASHBOARD_PID=$!

# Wait a moment for dashboard to start
sleep 3

# Start test app in background
echo "🧪 Starting Test Interface (Port 5001)..."
cd test-app
./start_test.sh &
TEST_APP_PID=$!
cd ..

echo ""
echo "✅ Both applications are starting..."
echo ""
echo "📊 Dashboard: http://localhost:5000"
echo "🧪 Test Interface: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop both applications"
echo ""

# Wait for user interrupt
while true; do
    # Check if processes are still running
    if ! kill -0 $DASHBOARD_PID 2>/dev/null && ! kill -0 $TEST_APP_PID 2>/dev/null; then
        echo "Both applications have stopped."
        break
    fi
    sleep 1
done