#!/bin/bash

# Emergency Worker Build Script
echo "Building Emergency Worker container..."

# Build the container
podman build -t emergency-worker -f Dockerfile .

if [ $? -eq 0 ]; then
    echo "✅ Emergency Worker container built successfully!"
    echo "To run: podman run --name emergency-worker emergency-worker"
else
    echo "❌ Failed to build Emergency Worker container"
    exit 1
fi