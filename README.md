# NaviGate App

Business Intelligence News Recommender for Colombian hospitality businesses.

## Overview

NaviGate analyzes local news, events, and social media to provide actionable business recommendations for coffee shops, restaurants, pubs, and bookstores in Colombian cities (Medellín, Bogotá, Cartagena, Barranquilla).

**🆕 Phase 2 Update**: Now features an advanced news crawler system that automatically discovers RSS feeds and manually crawls news websites from any country, with intelligent content extraction and processing.

## Technology Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Django + Django REST Framework
- **News Crawling**: Trafilatura + BeautifulSoup + Feedparser
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

### Core Features
- **Multi-language Support**: Spanish/English switching
- **Business Profiles**: Manage business information and preferences
- **Smart Recommendations**: ML-powered business suggestions
- **Mobile-First**: PWA for mobile access

### 🆕 Advanced News Crawler System (Phase 2)
- **Intelligent RSS Discovery**: Automatically finds RSS feeds from any news website
- **Manual Website Crawling**: Extracts articles from sites without RSS feeds
- **Global News Sources**: Support for news websites from any country
- **Content Processing Pipeline**: Standardizes and deduplicates articles
- **Admin Management**: Visual crawler status, one-click operations, bulk actions
- **Crawl History Tracking**: Detailed logs and performance metrics
- **API Integration**: RESTful endpoints for crawler management

### News Processing Pipeline
1. **RSS Discovery**: Automatically detect RSS feeds using multiple strategies
2. **Structure Analysis**: Analyze website layout for manual crawling
3. **Content Extraction**: Use Trafilatura for high-quality text extraction
4. **Content Processing**: Standardize, validate, and deduplicate articles
5. **ML Integration**: Prepare articles for business relevance analysis

## News Crawler Usage

### Adding News Sources (Admin Panel)

1. **Access Admin Panel**: http://localhost:8000/admin
2. **Go to News Sources**: Click "News sources" in the News section
3. **Add New Source**: Click "Add News Source"
4. **Configure Source**:
   - **Name**: News website name (e.g., "El Tiempo")
   - **Source Type**: Select "Periódico" or "Medio digital"
   - **Country**: Select from dropdown (Colombia first)
   - **Crawler URL**: Main website URL (e.g., "https://www.eltiempo.com")

### Automatic Setup

After adding a source, use the admin interface buttons:
- **Setup**: Auto-discover RSS feeds and analyze site structure
- **Discover RSS**: Find RSS feeds specifically
- **Analyze Site**: Map website sections for manual crawling
- **Crawl Now**: Extract articles immediately

### Bulk Operations

Select multiple sources and use admin actions:
- **Setup selected sources**: Batch RSS discovery and structure analysis
- **Crawl selected sources**: Batch article extraction
- **Discover RSS feeds**: Batch RSS discovery

### API Endpoints

```bash
# Source management
POST /api/news/sources/{id}/setup/
POST /api/news/sources/{id}/discover-rss/
POST /api/news/sources/{id}/crawl/
GET  /api/news/sources/{id}/crawl-history/

# System operations
POST /api/news/crawler/bulk-crawl/
GET  /api/news/crawler/system-status/
GET  /api/news/crawler/stats/
```

### Monitoring

- **Crawl History**: View detailed logs of all crawl attempts
- **System Status**: Monitor overall crawler performance
- **Source Recommendations**: Get suggestions for improving configurations

## Development

The project uses Docker for consistent development across environments. See `/docker/` directory for configuration files.

### Development Architecture

```
backend/
├── news/
│   ├── models.py           # NewsSource, NewsArticle, CrawlHistory
│   ├── admin.py            # Enhanced admin with crawler controls
│   ├── services/           # Crawler services
│   │   ├── rss_discovery.py      # RSS feed discovery
│   │   ├── manual_crawler.py     # Manual website crawling
│   │   ├── content_processor.py  # Content standardization
│   │   └── crawler_orchestrator.py # Main coordination service
│   └── api/
│       └── crawler.py      # Crawler management APIs
```

## License

Private project - All rights reserved