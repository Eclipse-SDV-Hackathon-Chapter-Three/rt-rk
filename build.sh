#!/bin/bash

# RT-RK Podman Build Script
# This script builds the container using Podman and manages Ankaios workloads

set -e

IMAGE_NAME="localhost/example_python_workload:0.1"
WORKLOADS=("PedestrianDetection" "EmergencyStop" "LaneAssistance" "RONA")

# Function to display usage
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help      Show this help message"
    echo "  -r, --rebuild   Rebuild and redeploy (deletes existing workloads and reapplies)"
    echo "  -d, --deploy    Deploy to Ankaios after building"
    echo "  --clean         Delete all workloads without rebuilding"
    echo ""
    echo "Examples:"
    echo "  $0              # Just build the container"
    echo "  $0 --deploy     # Build and deploy"
    echo "  $0 --rebuild    # Build, delete workloads, and redeploy"
    echo "  $0 --clean      # Delete workloads only"
}

# Function to delete workloads
delete_workloads() {
    echo "Deleting existing workloads..."
    for workload in "${WORKLOADS[@]}"; do
        echo "Deleting workload: $workload"
        ank delete workloads "$workload" 2>/dev/null || echo "  (workload $workload not found or already deleted)"
    done
    echo "Workload deletion completed"
}

# Function to deploy workloads
deploy_workloads() {
    echo "Deploying workloads to Ankaios..."
    ank apply manifest.yaml
    echo "Deployment completed"
    echo ""
    echo "Check deployment status with:"
    echo "  ank get workloads"
}

# Function to build container
build_container() {
    echo "Building container with Podman..."
    podman build -t "${IMAGE_NAME}" .
    echo "Container built successfully: ${IMAGE_NAME}"
    
    # Show the created image
    echo ""
    echo "Available images:"
    podman images | grep -E "(REPOSITORY|example_python_workload)"
}

# Parse command line arguments
REBUILD=false
DEPLOY=false
CLEAN_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -r|--rebuild)
            REBUILD=true
            shift
            ;;
        -d|--deploy)
            DEPLOY=true
            shift
            ;;
        --clean)
            CLEAN_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Execute based on options
if [[ "$CLEAN_ONLY" == true ]]; then
    delete_workloads
    exit 0
fi

if [[ "$REBUILD" == true ]]; then
    delete_workloads
    build_container
    deploy_workloads
elif [[ "$DEPLOY" == true ]]; then
    build_container
    deploy_workloads
else
    build_container
    echo ""
    echo "Container built successfully!"
    echo ""
    echo "Next steps:"
    echo "  • Test locally: podman run --rm ${IMAGE_NAME} python3 workers/lane/worker_lane.py"
    echo "  • Deploy to Ankaios: $0 --deploy"
    echo "  • Rebuild and redeploy: $0 --rebuild"
fi