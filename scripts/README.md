# NaviGate Scripts

This directory contains utility scripts for development and setup.

## Available Scripts

### 🚀 `start-server.sh`
**Main development server startup script**
- Stops any existing containers
- Builds and starts all Docker services
- Waits for services to be ready
- Provides service URLs and next steps

```bash
./scripts/start-server.sh
```

### 👤 `setup-admin.sh`
**Admin user and initial data setup**
- Runs database migrations
- Creates admin superuser (admin/admin123)
- Creates sample business owner (pub_owner/pub123)
- Sets up Irish Pub Medellín as demo business
- Loads Colombian news sources

```bash
./scripts/setup-admin.sh
```

### 📰 `create-mock-data.sh`
**Mock news and recommendations generator**
- Creates sample news articles for 6 demo scenarios
- Generates intelligent business recommendations
- Links recommendations to news sources
- Populates dashboard with realistic data

```bash
./scripts/create-mock-data.sh
```

### 🛑 `stop-server.sh`
**Graceful server shutdown**
- Stops all services in correct dependency order
- Preserves data volumes for quick restart
- Cleans up containers and networks
- Shows system status after shutdown

```bash
./scripts/stop-server.sh
```

### 🔄 `reset-app.sh`
**Complete application reset**
- ⚠️ **DESTRUCTIVE**: Wipes all data and volumes
- Removes database, cache, user accounts, businesses
- Forces clean rebuild of Docker images  
- Requires confirmation before proceeding

```bash
./scripts/reset-app.sh
```

## Quick Start Guide

1. **Start the server:**
   ```bash
   ./scripts/start-server.sh
   ```

2. **Set up admin and data:**
   ```bash
   ./scripts/setup-admin.sh
   ```

3. **Create mock content:**
   ```bash
   ./scripts/create-mock-data.sh
   ```

## Access Points

After running the scripts:

- **Frontend:** http://localhost:3001
- **Backend API:** http://localhost:8000
- **Django Admin:** http://localhost:8000/admin

## Test Accounts

### Admin User
- **URL:** http://localhost:8000/admin
- **Username:** admin
- **Password:** admin123
- **Permissions:** Full system access

### Business Owner
- **URL:** http://localhost:3001
- **Username:** pub_owner (or any email for mock auth)
- **Password:** pub123 (or any password for mock auth)
- **Business:** Irish Pub Medellín (Pub/Bar in Medellín)

## Service Management

### Starting Services
```bash
./scripts/start-server.sh          # Start all services
```

### Stopping Services  
```bash
./scripts/stop-server.sh           # Graceful shutdown
```

### Resetting Application
```bash
./scripts/reset-app.sh             # Complete reset (destructive)
```

## Troubleshooting

### If containers fail to start:
```bash
./scripts/stop-server.sh           # Stop everything cleanly
./scripts/start-server.sh          # Restart fresh
```

### If you need a complete clean slate:
```bash
./scripts/reset-app.sh             # Nuclear option - wipes everything
./scripts/start-server.sh          # Start from scratch
./scripts/setup-admin.sh           # Recreate admin and data
```

### View service logs:
```bash
docker-compose -f docker/docker-compose.dev.yml logs -f [service_name]

# Examples:
docker-compose -f docker/docker-compose.dev.yml logs -f backend
docker-compose -f docker/docker-compose.dev.yml logs -f frontend
docker-compose -f docker/docker-compose.dev.yml logs -f db
```

### Check service status:
```bash
docker-compose -f docker/docker-compose.dev.yml ps
```