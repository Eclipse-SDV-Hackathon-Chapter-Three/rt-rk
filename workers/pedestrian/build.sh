#!/bin/bash

# Pedestrian Worker Build Script
echo "Building Pedestrian Worker container..."

# Build the container
podman build -t pedestrian-worker -f Dockerfile .

if [ $? -eq 0 ]; then
    echo "✅ Pedestrian Worker container built successfully!"
    echo "To run: podman run --name pedestrian-worker pedestrian-worker"
else
    echo "❌ Failed to build Pedestrian Worker container"
    exit 1
fi