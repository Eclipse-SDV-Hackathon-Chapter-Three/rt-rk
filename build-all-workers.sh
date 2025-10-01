#!/bin/bash

# Master Build Script for All Workers
echo "🚀 Building all worker containers..."

WORKERS=("emergency" "lane" "pedestrian" "rona")
SUCCESS_COUNT=0
TOTAL_COUNT=${#WORKERS[@]}

for worker in "${WORKERS[@]}"; do
    echo ""
    echo "🔧 Building $worker worker..."
    cd "workers/$worker"
    
    if ./build.sh; then
        ((SUCCESS_COUNT++))
    else
        echo "❌ Failed to build $worker worker"
    fi
    
    cd - > /dev/null
done

echo ""
echo "📊 Build Summary:"
echo "✅ Successfully built: $SUCCESS_COUNT/$TOTAL_COUNT workers"

if [ $SUCCESS_COUNT -eq $TOTAL_COUNT ]; then
    echo "🎉 All workers built successfully!"
    echo ""
    echo "To run all workers:"
    echo "  podman run -d --name emergency-worker emergency-worker"
    echo "  podman run -d --name lane-worker lane-worker"
    echo "  podman run -d --name pedestrian-worker pedestrian-worker"
    echo "  podman run -d --name rona-worker rona-worker"
    echo ""
    echo "To stop all workers:"
    echo "  podman stop emergency-worker lane-worker pedestrian-worker rona-worker"
    echo ""
    echo "To remove all workers:"
    echo "  podman rm emergency-worker lane-worker pedestrian-worker rona-worker"
else
    echo "⚠️  Some workers failed to build. Check the logs above."
    exit 1
fi