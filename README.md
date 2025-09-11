# NaviTest App

Business Intelligence News Recommender for Colombian hospitality businesses.

## Overview

NaviTest analyzes local news, events, and social media to provide actionable business recommendations for coffee shops, restaurants, pubs, and bookstores in Colombian cities (Medellín, Bogotá, Cartagena, Barranquilla).

## Technology Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Django + Django REST Framework
- **ML/AI**: spaCy (Spanish NLP) + scikit-learn
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **Infrastructure**: Docker containers
- **Languages**: Spanish (primary) + English

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd navigate-app

# Start development environment
docker-compose -f docker/docker-compose.dev.yml up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

## Project Structure

```
navigate-app/
├── frontend/          # React + Vite application
├── backend/           # Django API server
├── docker/            # Docker configuration files
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