#!/bin/bash

# Test App Startup Script

echo "==================================="
echo "  Vehicle Dashboard Test App"
echo "==================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed!"
    exit 1
fi

# Navigate to test-app directory
cd "$(dirname "$0")"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start the test app
echo "Starting Test Interface..."
echo "Test Interface: http://localhost:5001"
echo "Make sure the main dashboard is running on http://localhost:5000"
echo "Press Ctrl+C to stop the test app"
echo ""

python app.py