#!/bin/bash

# NaviGate Development Server Startup Script
# This script starts all required services and sets up the development environment

set -e  # Exit on any error

echo "🚀 Starting NaviGate Development Environment..."
echo "==============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose is not installed."
    exit 1
fi

# Function to wait for service to be ready
wait_for_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    echo "⏳ Waiting for $service_name to be ready on port $port..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f -s "http://localhost:$port/health/" > /dev/null 2>&1 || \
           nc -z localhost $port > /dev/null 2>&1; then
            echo "✅ $service_name is ready!"
            return 0
        fi
        
        echo "   Attempt $attempt/$max_attempts - $service_name not ready yet..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name failed to start after $max_attempts attempts"
    return 1
}

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
docker-compose -f docker/docker-compose.dev.yml down --remove-orphans

# Build and start all services
echo "🏗️  Building and starting all services..."
docker-compose -f docker/docker-compose.dev.yml up --build -d

# Wait for database to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Check if services are healthy
wait_for_service "Backend API" 8000
wait_for_service "Frontend" 3000

echo ""
echo "🎉 NaviGate is now running!"
echo "==============================================="
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "Django Admin: http://localhost:8000/admin"
echo ""
echo "📋 Next Steps:"
echo "1. Run: ./setup-admin.sh to create admin user and sample data"
echo "2. Visit http://localhost:8000/admin to manage data as admin"
echo "3. Visit http://localhost:3000 to use the client application"
echo ""
echo "🛑 To stop all services:"
echo "docker-compose -f docker/docker-compose.dev.yml down"
echo ""
echo "📊 To view logs:"
echo "docker-compose -f docker/docker-compose.dev.yml logs -f [service_name]"
echo ""
echo "Services:"
echo "- frontend: React application"
echo "- backend: Django API server"
echo "- worker: Celery background tasks"
echo "- db: PostgreSQL database"
echo "- redis: Cache and task queue"