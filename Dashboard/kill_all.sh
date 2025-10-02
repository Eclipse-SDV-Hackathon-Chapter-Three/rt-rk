#!/bin/bash

# Kill all dashboard related processes

echo "🛑 Stopping all Dashboard processes..."

# Kill processes by name
pkill -f "python.*app.py" 2>/dev/null
pkill -f "Dashboard.*app.py" 2>/dev/null

# Kill processes on specific ports
lsof -ti:5000 | xargs kill -9 2>/dev/null
lsof -ti:5001 | xargs kill -9 2>/dev/null

echo "✅ All processes stopped."

# Optional: Check if ports are now free
sleep 1
if ! lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✓ Port 5000 is now free"
else
    echo "⚠ Port 5000 still in use"
fi

if ! lsof -Pi :5001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✓ Port 5001 is now free"
else
    echo "⚠ Port 5001 still in use"
fi