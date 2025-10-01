#!/bin/bash

# Lane Worker Build Script
echo "Building Lane Worker container..."

# Build the container
podman build -t lane-worker -f Dockerfile .

if [ $? -eq 0 ]; then
    echo "✅ Lane Worker container built successfully!"
    echo "To run: podman run --name lane-worker lane-worker"
else
    echo "❌ Failed to build Lane Worker container"
    exit 1
fi