#!/bin/bash

# NaviGate Server Shutdown Script
# This script gracefully stops all services in the correct order

set -e

echo "🛑 Stopping NaviGate Development Environment..."
echo "============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ℹ️  Docker is not running. Nothing to stop."
    exit 0
fi

# Check if containers are running
if ! docker-compose -f docker/docker-compose.dev.yml ps | grep -q "Up"; then
    echo "ℹ️  No containers are currently running."
    exit 0
fi

echo "📊 Current container status:"
docker-compose -f docker/docker-compose.dev.yml ps

echo ""
echo "🔄 Gracefully stopping services in order..."

# Stop services in reverse dependency order
echo "⏹️  Stopping frontend service..."
docker-compose -f docker/docker-compose.dev.yml stop frontend

echo "⏹️  Stopping worker service..."
docker-compose -f docker/docker-compose.dev.yml stop worker

echo "⏹️  Stopping backend service..."
docker-compose -f docker/docker-compose.dev.yml stop backend

echo "⏹️  Stopping Redis cache..."
docker-compose -f docker/docker-compose.dev.yml stop redis

echo "⏹️  Stopping PostgreSQL database..."
docker-compose -f docker/docker-compose.dev.yml stop db

echo ""
echo "🧹 Cleaning up containers..."
docker-compose -f docker/docker-compose.dev.yml down --remove-orphans

echo ""
echo "✅ All services stopped successfully!"
echo "===================================="
echo ""
echo "📊 System Status:"
echo "   • All containers: Stopped"
echo "   • Data volumes: Preserved"
echo "   • Images: Available for quick restart"
echo ""
echo "🚀 To restart the server:"
echo "   ./scripts/start-server.sh"
echo ""
echo "🔄 To reset everything:"
echo "   ./scripts/reset-app.sh"
echo ""
echo "📋 To view stopped containers:"
echo "   docker-compose -f docker/docker-compose.dev.yml ps -a"