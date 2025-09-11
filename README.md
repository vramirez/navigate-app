# NaviGate App

Business Intelligence News Recommender for Colombian hospitality businesses.

## Overview

NaviGate analyzes local news, events, and social media to provide actionable business recommendations for coffee shops, restaurants, pubs, and bookstores in Colombian cities (Medellín, Bogotá, Cartagena, Barranquilla).

## Technology Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Django + Django REST Framework
- **ML/AI**: spaCy (Spanish NLP) + scikit-learn
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **Infrastructure**: Docker containers
- **Languages**: Spanish (primary) + English

## Quick Start

```bash
# 1. Start the development environment
./scripts/start-server.sh

# 2. Set up admin user and initial data
./scripts/setup-admin.sh

# 3. Create mock news and recommendations
./scripts/create-mock-data.sh

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Django Admin: http://localhost:8000/admin
```

### Test Accounts

**Admin User (Django Admin)**
- URL: http://localhost:8000/admin
- Username: `admin` / Password: `admin123`

**Business Owner (React App)**
- URL: http://localhost:3000
- Username: Any email (mock auth)
- Password: Any password (mock auth)
- Demo Business: Irish Pub Medellín

## Project Structure

```
navigate-app/
├── frontend/          # React + Vite application
├── backend/           # Django API server
├── docker/            # Docker configuration files
├── scripts/           # Development and setup scripts
├── test/              # Testing and debugging files
├── backlog.md         # Project backlog and tasks
└── README.md          # This file
```

## Features

- **Multi-language Support**: Spanish/English switching
- **Business Profiles**: Manage business information and preferences
- **News Analysis**: Colombian news sources with NLP processing
- **Smart Recommendations**: ML-powered business suggestions
- **Mobile-First**: PWA for mobile access

## Development

The project uses Docker for consistent development across environments. See `/docker/` directory for configuration files.

## License

Private project - All rights reserved