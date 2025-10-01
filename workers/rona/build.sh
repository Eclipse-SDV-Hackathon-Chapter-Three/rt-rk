#!/bin/bash

# RONA Worker Build Script
echo "Building RONA Worker container..."

# Build the container
podman build -t rona-worker -f Dockerfile .

if [ $? -eq 0 ]; then
    echo "✅ RONA Worker container built successfully!"
    echo "To run: podman run --name rona-worker rona-worker"
else
    echo "❌ Failed to build RONA Worker container"
    exit 1
fi