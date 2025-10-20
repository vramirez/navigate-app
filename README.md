# NaviGate App

Business Intelligence News Recommender for Colombian hospitality businesses.

## Overview

NaviGate analyzes local news, events, and social media to provide actionable business recommendations for coffee shops, restaurants, pubs, and bookstores in Colombian cities (Medellín, Bogotá, Cartagena, Barranquilla).

## Project Status

✅ **Phase 1 Complete**: Core infrastructure, models, UI
✅ **Phase 2 Complete**: Advanced news crawler system with real data ingestion
🔄 **Phase 3 In Progress**: Frontend integration and ML engine enhancement
📋 **Phase 4 Planned**: Advanced ML features and deployment

## Technology Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: Django + Django REST Framework
- **News Crawling**: Trafilatura + BeautifulSoup + Feedparser
- **ML/AI**: spaCy (Spanish NLP) + Ollama (Llama 3.2 1B) + scikit-learn
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **Infrastructure**: Docker containers
- **Languages**: Spanish (primary) + English

## ML Architecture (Phase 3 - Implemented)

### Dual Extraction Pipeline (spaCy + LLM)
- **spaCy Extraction**: Fast, rule-based feature extraction using Spanish NLP models
- **LLM Extraction**: Ollama (Llama 3.2 1B) for enhanced feature understanding
- **Hybrid Approach**: Both methods run in parallel for high-suitability articles
- **Comparison System**: Automatic comparison and quality metrics tracking

### Core ML Components
- **Text Processing**: spaCy Spanish models for NLP
- **Event Detection**: Automated extraction from news content (event type, dates, venues)
- **Business Matching**: Keyword relevance scoring algorithm
- **Recommendation Generation**: Template-based with ML confidence scores
- **Feedback Loop**: User ratings improve future recommendations

### LLM Integration (task-9.6)
- **Model**: Llama 3.2 1B (lightweight, optimized for local deployment)
- **Trigger**: Only runs for articles with suitability score >= 0.3
- **Features Extracted**: Event type, location, dates, attendance, keywords, entities
- **Comparison Tracking**: Agreement rates and completeness scores stored for analysis

## Quick Start

```bash
# Initial Setup (First time only)
./scripts/start-server.sh       # Start all Docker services
./scripts/setup-ollama.sh        # Setup Ollama and pull Llama 3.2 1B model
./scripts/setup-admin.sh         # Create admin user and demo data
./scripts/create-mock-data.sh    # Generate sample news

# Development Cycle (Daily usage)
./scripts/start-server.sh        # Start of day
./scripts/stop-server.sh         # End of day

# Troubleshooting
./scripts/reset-app.sh           # Nuclear option: complete reset
```

**Note on Ollama Setup:**
- The `setup-ollama.sh` script pulls the Llama 3.2 1B model (~1.3GB download)
- This only needs to be run once after first starting the services
- LLM extraction is optional - the system works fine with spaCy-only extraction
- If Ollama is unavailable, articles will be processed with spaCy only

**Script Safety Features:** All scripts include directory validation, confirmation prompts, status checking, and detailed logging.

### Access Points

- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin

### Test Accounts

**Admin User (Django Admin)**
- URL: http://localhost:8000/admin
- Username: `admin` / Password: `admin123`

**Business Owner (React App)**
- URL: http://localhost:3001
- Username: Any email (mock auth)
- Password: Any password (mock auth)
- Demo Business: Irish Pub Medellín

## LLM Configuration

### Environment Variables

The following environment variables control LLM extraction behavior (configured in `docker-compose.dev.yml`):

- `OLLAMA_HOST`: Ollama service URL (default: `http://ollama:11434`)
- `LLM_MODEL_NAME`: Model to use (default: `llama3.2:1b`)
- `LLM_TIMEOUT_SECONDS`: Request timeout (default: `30`)
- `LLM_EXTRACTION_ENABLED`: Enable/disable LLM extraction (default: `True`)

### Changing the Ollama Model

You can easily switch to a different Ollama model using either method:

**Method 1: Environment Variable (Quick Test)**

```bash
# Download and test a different model
OLLAMA_MODEL=llama3.2:3b ./scripts/setup-ollama.sh

# Other popular options:
OLLAMA_MODEL=mistral:7b ./scripts/setup-ollama.sh      # 4.1GB - High quality
OLLAMA_MODEL=qwen2.5:0.5b ./scripts/setup-ollama.sh    # 397MB - Super fast
```

**Method 2: Docker Compose (Persistent)**

1. Edit `docker/docker-compose.dev.yml` and update both `backend` and `worker` services:

```yaml
backend:
  environment:
    - LLM_MODEL_NAME=llama3.2:3b  # Change this

worker:
  environment:
    - LLM_MODEL_NAME=llama3.2:3b  # And this
```

2. Restart services and pull new model:

```bash
./scripts/stop-server.sh
./scripts/start-server.sh
OLLAMA_MODEL=llama3.2:3b ./scripts/setup-ollama.sh
```

**Available Models:**

| Model | Size | Speed | Quality | Best For |
|-------|------|-------|---------|----------|
| `qwen2.5:0.5b` | 397 MB | ⚡⚡⚡ | ⭐⭐ | Low-resource environments |
| `llama3.2:1b` | 1.3 GB | ⚡⚡ | ⭐⭐⭐ | Default - Good balance |
| `llama3.2:3b` | 2.0 GB | ⚡⚡ | ⭐⭐⭐⭐ | Better accuracy |
| `mistral:7b` | 4.1 GB | ⚡ | ⭐⭐⭐⭐⭐ | High quality extraction |
| `llama3.1:8b` | 4.7 GB | ⚡ | ⭐⭐⭐⭐⭐ | Best quality |

**Note:** The model is stored in a Docker volume and persists between restarts. You only need to download it once.

### Testing LLM Extraction

```bash
# Check if Ollama is running and model is available
docker compose -f docker/docker-compose.dev.yml exec ollama ollama list

# Test LLM with a simple prompt
docker compose -f docker/docker-compose.dev.yml exec ollama ollama run llama3.2:1b "Hola"

# Process articles with LLM extraction (via Django shell or management command)
docker compose -f docker/docker-compose.dev.yml exec backend python manage.py process_articles --limit 5
```

### Viewing Extraction Results

LLM extraction results are stored in the `NewsArticle` model:
- `llm_features_extracted`: Boolean indicating if LLM processed the article
- `llm_extraction_results`: JSON with all extracted features
- `extraction_comparison`: JSON with comparison between spaCy and LLM results

Access via Django Admin → News → Articles → Select article → View JSON fields

### Performance Considerations

- **Selective Processing**: LLM only runs for articles with `business_suitability_score >= 0.3`
- **Async Processing**: Celery worker handles extraction asynchronously
- **Fallback**: System continues with spaCy extraction if LLM fails
- **Model Size**: Llama 3.2 1B is lightweight (~1.3GB) for local deployment

## Development Workflow

1. **Initial Setup**: Run all scripts in sequence (start-server, setup-admin, create-mock-data)
2. **Daily Development**: Use start-server.sh and stop-server.sh for daily coding sessions
3. **Testing Changes**: Use reset-app.sh for a clean slate when needed
4. **Data Management**: Use Django Admin panel for content creation and configuration
5. **Client Testing**: React app includes mock authentication for easy frontend testing

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

## Development Features

- **Comprehensive Scripts**: All scripts include error handling, validation, and user guidance
- **Mock Authentication**: Easy frontend testing without real authentication setup
- **Internationalization**: Spanish-first design with English fallback support
- **Mobile-First PWA**: Responsive design optimized for Colombian market
- **Docker Environment**: Consistent development across all platforms
- **Open-Source Stack**: 100% free and open-source technology throughout
- **Advanced News Crawler**: International support with RSS discovery and manual crawling
- **Admin Interface**: Non-technical user-friendly Django admin with visual indicators
- **RESTful APIs**: Programmatic access to all crawler and ML operations

## License

Private project - All rights reserved