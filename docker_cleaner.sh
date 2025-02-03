#!/bin/bash

echo "🚀 Starting Docker Cleanup..."

# Clean dangling images
echo "🗑️ Removing dangling images..."
docker image prune -f

# Remove all unused data (images, containers, volumes, cache)
echo "⚡ Removing all unused data..."
docker system prune -a -f --volumes

# Clear build cache
echo "🧹 Clearing build cache..."
docker builder prune -af

echo "✅ Docker Cleanup Complete!"

# Show disk usage after cleanup
docker system df
