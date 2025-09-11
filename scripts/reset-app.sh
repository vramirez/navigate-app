#!/bin/bash

# NaviGate Application Reset Script
# This script completely resets the application to its initial state

set -e

echo "🔄 NaviGate Application Reset"
echo "============================"
echo ""
echo "⚠️  DANGER: This will completely reset the application!"
echo "   • All data will be deleted (users, businesses, news, recommendations)"
echo "   • Database will be wiped clean"
echo "   • All volumes will be removed"
echo "   • You'll need to run setup scripts again"
echo ""

# Safety checks
echo "🔒 Safety checks:"
echo "   • Current directory: $(pwd)"
echo "   • Target compose file: docker/docker-compose.dev.yml"

# Verify we're in the right directory
if [ ! -f "docker/docker-compose.dev.yml" ]; then
    echo "❌ Error: Not in NaviGate project root directory!"
    echo "   Please run this script from the project root where docker/ exists."
    exit 1
fi

# Show current data status
echo ""
echo "📊 Current system status:"
if docker compose -f docker/docker-compose.dev.yml ps | grep -q "Up"; then
    echo "   • Status: Services are RUNNING"
    docker compose -f docker/docker-compose.dev.yml ps --format "table {{.Service}}\t{{.State}}"
else
    echo "   • Status: Services are stopped"
fi

# Check if any volumes exist
volumes=$(docker volume ls -q | grep -E "(navitest|navigate)" | wc -l)
if [ "$volumes" -gt 0 ]; then
    echo "   • Data volumes: $volumes found (will be deleted)"
    docker volume ls | grep -E "(navitest|navigate)" | head -5
else
    echo "   • Data volumes: None found"
fi

echo ""
echo "💀 This operation is IRREVERSIBLE!"
echo ""

# Double confirmation with countdown
echo "⏳ You have 10 seconds to cancel (Ctrl+C)..."
for i in {10..1}; do
    echo -n "$i "
    sleep 1
done
echo ""
echo ""

# First confirmation
read -p "Type 'RESET' in capital letters to continue: " confirmation1

if [ "$confirmation1" != "RESET" ]; then
    echo "❌ Reset cancelled - incorrect confirmation."
    exit 0
fi

# Second confirmation with project name
read -p "Type the project name 'NaviGate' to confirm: " confirmation2

if [ "$confirmation2" != "NaviGate" ]; then
    echo "❌ Reset cancelled - project name mismatch."
    exit 0
fi

echo ""
echo "✅ All confirmations received. Proceeding with reset..."

# Optional backup before reset
echo ""
read -p "🔐 Do you want to create a backup before reset? (y/N): " backup_choice

if [ "$backup_choice" = "y" ] || [ "$backup_choice" = "Y" ]; then
    backup_dir="backups/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    echo "📦 Creating backup in $backup_dir..."
    
    # Backup database if running
    if docker compose -f docker/docker-compose.dev.yml ps db | grep -q "Up"; then
        echo "   • Backing up database..."
        docker compose -f docker/docker-compose.dev.yml exec -T db pg_dump -U navigate navigate > "$backup_dir/database.sql" 2>/dev/null || echo "   ⚠️ Database backup failed (might be empty)"
    fi
    
    # Backup important config files
    echo "   • Backing up configuration..."
    cp -r backend/.env* "$backup_dir/" 2>/dev/null || true
    cp docker/docker-compose.dev.yml "$backup_dir/" 2>/dev/null || true
    
    echo "✅ Backup created in $backup_dir"
    echo "   To restore: Import database.sql after fresh setup"
fi

echo ""
echo "🛑 Starting complete application reset..."
echo "========================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

echo "⏹️  Stopping all running containers..."
docker compose -f docker/docker-compose.dev.yml down --remove-orphans

echo "🗑️  Removing all volumes and data..."
docker compose -f docker/docker-compose.dev.yml down --volumes

echo "🧹 Removing unused Docker resources..."
docker system prune -f --volumes

echo "📦 Removing application-specific volumes..."
# Remove any named volumes that might persist
docker volume ls -q | grep -E "(navitest|navigate)" | xargs -r docker volume rm || true

echo "🏗️  Removing built images to ensure clean rebuild..."
docker compose -f docker/docker-compose.dev.yml down --rmi local || true

echo ""
echo "✅ Application reset completed successfully!"
echo "=========================================="
echo ""
echo "🎯 Next Steps:"
echo "1. Start fresh environment:"
echo "   ./scripts/start-server.sh"
echo ""
echo "2. Set up admin user and initial data:"
echo "   ./scripts/setup-admin.sh"
echo ""
echo "3. Create mock content for testing:"
echo "   ./scripts/create-mock-data.sh"
echo ""
echo "📋 What was reset:"
echo "   ✅ All database data (PostgreSQL)"
echo "   ✅ All cached data (Redis)"
echo "   ✅ All application volumes"
echo "   ✅ All built Docker images"
echo "   ✅ All user accounts and businesses"
echo "   ✅ All news articles and recommendations"
echo ""
echo "💡 The application is now in pristine initial state."
echo "   Run the setup scripts to configure it again."