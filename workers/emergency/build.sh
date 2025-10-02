#!/bin/bash

# Build script for Simple Zenoh Publisher Podman image

IMAGE_NAME="emergency"
TAG="latest"

echo "Building Podman image: ${IMAGE_NAME}:${TAG}"
echo "=================================="

# Build the image
podman build -t "${IMAGE_NAME}:${TAG}" .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Image built successfully!"
    echo ""
    echo "Usage examples:"
    echo "  # Run with default router (127.0.0.1)"
    echo "  podman run --rm ${IMAGE_NAME}:${TAG}"
    echo ""
    echo "  # Run with custom router"
    echo "  podman run --rm ${IMAGE_NAME}:${TAG} --router 192.168.1.100"
    echo ""
    echo "  # Run in background"
    echo "  podman run -d --name zenoh-publisher ${IMAGE_NAME}:${TAG}"
    echo ""
    echo "  # View logs"
    echo "  podman logs -f zenoh-publisher"
    echo ""
    echo "  # Stop background container"
    echo "  podman stop zenoh-publisher"
else
    echo "❌ Build failed!"
    exit 1
fi