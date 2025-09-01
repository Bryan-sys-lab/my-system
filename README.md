# B-Search Server - Enterprise Intelligence Platform

## Overview

B-Search is a comprehensive, production-grade intelligence platform designed for advanced data collection, analysis, and enrichment. Built with modern microservices architecture, it provides powerful OSINT (Open Source Intelligence) capabilities with AI-powered analytics, real-time monitoring, and scalable data processing.

## 🚀 Core Capabilities

### 📊 **Data Collection & Enrichment**
- **Multi-Source Collectors**: Web scraping, RSS feeds, social media, crypto blockchains
- **AI-Powered Enrichment**: OCR, ASR, NER, entity resolution, similarity matching
- **Real-time Processing**: Async pipelines with Celery workers and Redis broker
- **Quality Assurance**: Deduplication, validation, and metadata enrichment

### 🧠 **AI & Machine Learning**
- **Computer Vision**: YOLOv8 object detection, CLIP image embeddings, FAISS similarity search
- **Natural Language Processing**: Sentiment analysis, topic clustering, content summarization
- **Predictive Analytics**: Trend forecasting, anomaly detection, pattern recognition
- **Automated Reporting**: AI-generated narratives and strategic insights

### 🌐 **Social Network Analysis**
- **Graph Algorithms**: Centrality measures, community detection, path finding
- **Relationship Mining**: Social connection extraction and analysis
- **Network Visualization**: Interactive graph rendering and analysis
- **Influence Mapping**: PageRank, betweenness centrality, eigenvector centrality

### 📈 **Business Intelligence**
- **Real-time Analytics**: Live dashboards with KPI tracking
- **Advanced Reporting**: Multi-format exports (JSON, CSV, HTML, PDF)
- **Trend Analysis**: Time-series data with statistical modeling
- **Performance Monitoring**: System metrics and health indicators

### 🔒 **Enterprise Security**
- **Access Control**: API authentication and authorization
- **Data Protection**: Encryption, secure storage, audit trails
- **Compliance**: GDPR compliance, data retention policies
- **Monitoring**: Security event logging and alerting

## 🏗️ **Architecture**

### **Microservices Design**
```
b-search-server/
├── apps/
│   ├── api/              # FastAPI REST API (Port 8080)
│   └── workers/          # Celery async workers
├── libs/
│   ├── collectors/       # Data collection modules
│   ├── enrichment/       # AI/ML enrichment pipelines
│   ├── crypto/          # Blockchain data connectors
│   ├── storage/         # Database and file storage
│   ├── common/          # Shared utilities
│   └── social_network/  # Graph analysis algorithms
├── services/            # External services (DB, Cache, Storage)
├── infra/               # Infrastructure and migrations
└── tests/               # Comprehensive test suite
```

### **Technology Stack**
- **Backend Framework**: FastAPI (Python async web framework)
- **Task Queue**: Celery with Redis broker
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis for session and data caching
- **Storage**: MinIO S3-compatible object storage
- **Monitoring**: Prometheus metrics + Grafana dashboards
- **Containerization**: Docker + Docker Compose
- **AI/ML**: PyTorch, CLIP, FAISS, YOLOv8

### **Infrastructure Components**
- **API Gateway**: FastAPI application server
- **Worker Pool**: Celery distributed task processing
- **Database Layer**: PostgreSQL with connection pooling
- **Cache Layer**: Redis for high-performance data access
- **Storage Layer**: MinIO for file and media assets
- **Monitoring Stack**: Prometheus + Grafana + AlertManager

## 📚 **API Reference**

### **Core Endpoints**

#### **Project Management**
```http
POST   /projects           # Create new project
GET    /projects           # List all projects
GET    /projects/{id}      # Get project details
PUT    /projects/{id}      # Update project
DELETE /projects/{id}      # Delete project
```

#### **Data Collection**
```http
POST   /collect/web        # Web page scraping
GET    /collect/rss-pack   # RSS feed collection
GET    /collect/reddit/{subreddit}  # Reddit data
GET    /collect/youtube    # YouTube channel data
GET    /collect/wayback    # Wayback Machine snapshots
POST   /batch/run          # Batch collection operations
```

#### **Social Media Collection**
```http
GET    /social/twitter/search       # Twitter/X search
GET    /social/facebook/page        # Facebook pages
GET    /social/instagram/user       # Instagram profiles
GET    /social/telegram/channel     # Telegram channels
GET    /social/discord/channel      # Discord channels
GET    /social/mastodon/public      # Mastodon timelines
GET    /social/bluesky/actor        # Bluesky profiles
GET    /social/tiktok/user          # TikTok users
POST   /social/reddit/multi         # Multi-subreddit collection
```

#### **Cryptocurrency Analysis**
```http
GET    /crypto/btc/{address}        # Bitcoin address analysis
GET    /crypto/eth/address/{addr}   # Ethereum address lookup
GET    /crypto/eth/tx/{hash}        # Transaction details
```

#### **AI Enrichment**
```http
POST   /enrich/yolo                 # Object detection
POST   /enrich/clip/index_images    # Image embedding indexing
POST   /enrich/clip/search_text     # Text-to-image search
POST   /ai/analyze/report           # Comprehensive AI analysis
POST   /ai/generate/narrative       # AI narrative generation
POST   /ai/insights/generate        # Targeted insights
POST   /ai/summarize/content        # Content summarization
```

#### **Social Network Analysis**
```http
POST   /social-network/build        # Build network graph
GET    /social-network/stats        # Network statistics
GET    /social-network/people       # Network nodes
GET    /social-network/centrality   # Centrality measures
GET    /social-network/communities  # Community detection
GET    /social-network/analysis     # Comprehensive analysis
```

#### **Advanced Search & Analytics**
```http
POST   /search/advanced             # Advanced search with filters
GET    /search/suggestions          # Search suggestions
GET    /analytics/overview          # Dashboard overview
GET    /analytics/time-series       # Time series data
GET    /analytics/platforms         # Platform analytics
GET    /analytics/export            # Export analytics data
```

#### **Monitoring & Watchers**
```http
POST   /watchers                    # Create monitoring watcher
GET    /watchers                    # List watchers
POST   /watchers/run_once           # Manual watcher execution
GET    /metrics                     # Prometheus metrics
GET    /healthz                     # Health check
```

#### **Data Export**
```http
GET    /export/items                # Export collected items
GET    /export/projects             # Export project data
```

### **Crawler Endpoints**
```http
POST   /crawl/deepweb               # Deep web crawling
POST   /crawl/onion                 # Onion network crawling
GET    /collect/web_fallback        # Fallback web collection
```

### **Label Studio Integration**
```http
POST   /labelstudio/projects        # Create labeling project
GET    /labelstudio/projects        # List projects
POST   /labelstudio/tasks/{id}      # Create labeling tasks
GET    /labelstudio/tasks/{id}      # Get project tasks
POST   /annotations                 # Submit annotations
GET    /annotations/export/{id}     # Export annotations
```

## 🚀 **Quick Start**

### **Prerequisites**
- Docker and Docker Compose
- 8GB+ RAM recommended
- 20GB+ disk space
- Internet connection for data collection

### **Installation**
```bash
# Clone repository
git clone <repository-url>
cd b-search-server

# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env  # Configure API keys and settings

# Start all services
docker compose up -d --build

# Check service status
docker compose ps
```

### **Access Points**
- **API Documentation**: http://localhost:8080/docs
- **Alternative Docs**: http://localhost:8080/redoc
- **Label Studio**: http://localhost:8081
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

### **Basic Usage**
```bash
# Create a project
curl -X POST http://localhost:8080/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "My Intelligence Project"}'

# Collect web data
curl -X POST http://localhost:8080/collect/web \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "project_id": "your-project-id"}'

# Get analytics overview
curl http://localhost:8080/analytics/overview
```

## ⚙️ **Configuration**

### **Environment Variables**
```bash
# Database Configuration
POSTGRES_USER=bsearch
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=bsearch_db

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# MinIO Configuration
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin

# API Keys (Optional - features disabled without them)
TWITTER_BEARER_TOKEN=your_twitter_token
FACEBOOK_GRAPH_TOKEN=your_facebook_token
ETHERSCAN_API_KEY=your_etherscan_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token

# Security
RUN_ALL_SECRET=your_secret_key
SECRET_KEY=your_app_secret

# Monitoring
SENTRY_DSN=your_sentry_dsn
```

### **Advanced Configuration**
```yaml
# docker-compose.override.yml
version: "3.9"
services:
  api:
    environment:
      - WORKER_CONCURRENCY=8
      - MAX_REQUEST_SIZE=100MB
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
```

## 🔧 **Development**

### **Local Development Setup**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install optional ML dependencies
pip install -r requirements-no-torch.txt  # Without PyTorch
# OR
pip install torch torchvision  # Full ML support

# Run database migrations
python -m alembic upgrade head

# Start development server
uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8080

# Start Celery workers
celery -A apps.workers.celery_app worker --loglevel=info
```

### **Testing**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=libs --cov-report=html

# Run specific test module
pytest tests/test_collectors/

# Run integration tests
pytest tests/integration/
```

### **Code Quality**
```bash
# Lint code
flake8 libs/ apps/

# Format code
black libs/ apps/

# Type checking
mypy libs/ apps/

# Security scanning
bandit -r libs/ apps/
```

## 📊 **Monitoring & Observability**

### **Metrics & Dashboards**
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
- **Real-time Metrics**: Request rates, response times, error rates
- **System Metrics**: CPU, memory, disk usage
- **Business Metrics**: Collection volumes, API usage

### **Logging**
- **Structured Logging**: JSON format with correlation IDs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Log Aggregation**: Centralized logging with searchable interface
- **Audit Trails**: Security events and data access logging

### **Alerting**
```yaml
# Alert Manager configuration
alerting:
  whatsapp:
    enabled: true
    to: "+1234567890"
  email:
    enabled: true
    smtp_server: "smtp.gmail.com"
    recipients: ["alerts@company.com"]
  webhook:
    enabled: true
    url: "https://your-siem.com/webhook"
```

## 🔒 **Security Features**

### **Authentication & Authorization**
- **API Key Authentication**: Secure API access
- **Role-Based Access Control**: Granular permissions
- **Session Management**: Secure session handling
- **Rate Limiting**: DDoS protection and abuse prevention

### **Data Protection**
- **Encryption at Rest**: Database and file encryption
- **TLS/SSL**: Encrypted data transmission
- **Data Sanitization**: Input validation and sanitization
- **Secure Deletion**: Safe data removal with overwrite

### **Compliance**
- **GDPR Compliance**: Data subject rights, consent management
- **Audit Logging**: Comprehensive activity logging
- **Data Retention**: Configurable retention policies
- **Privacy Controls**: Data minimization and purpose limitation

## 🚀 **Deployment**

### **Production Deployment**
```bash
# Production compose file
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# With custom configuration
docker compose --env-file .env.prod up -d
```

### **Scaling**
```yaml
# Scale workers based on load
services:
  workers:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

### **High Availability**
- **Load Balancing**: Multiple API instances
- **Database Clustering**: PostgreSQL streaming replication
- **Redis Clustering**: Distributed caching
- **Backup & Recovery**: Automated backups with point-in-time recovery

## 📈 **Performance Optimization**

### **Database Optimization**
- **Connection Pooling**: Efficient database connections
- **Query Optimization**: Indexed queries and query planning
- **Caching Strategy**: Multi-level caching (Redis + application)
- **Partitioning**: Data partitioning for large datasets

### **API Performance**
- **Async Processing**: Non-blocking I/O operations
- **Response Caching**: Intelligent caching with TTL
- **Request Batching**: Efficient bulk operations
- **Rate Limiting**: Fair usage policies

### **ML Optimization**
- **GPU Support**: CUDA acceleration for ML workloads
- **Model Caching**: Pre-loaded models for faster inference
- **Batch Processing**: Efficient batch operations
- **Memory Management**: Optimized memory usage for large models

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Service Startup Issues**
```bash
# Check service logs
docker compose logs api
docker compose logs workers

# Check service health
curl http://localhost:8080/healthz

# Restart services
docker compose restart api workers
```

#### **Database Connection Issues**
```bash
# Check database connectivity
docker compose exec postgres psql -U bsearch -d bsearch_db

# Reset database
docker compose down -v
docker compose up -d postgres
```

#### **Memory Issues**
```bash
# Monitor memory usage
docker stats

# Adjust memory limits
docker compose up -d --scale workers=2
```

#### **API Key Issues**
```bash
# Check API key configuration
docker compose exec api env | grep -i token

# Test API connectivity
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8080/projects
```

### **Debug Mode**
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
docker compose up -d

# Check detailed logs
docker compose logs -f --tail=100 api
```

## 🤝 **Contributing**

### **Development Workflow**
1. **Fork Repository**: Create your own fork
2. **Create Feature Branch**: `git checkout -b feature/new-collector`
3. **Write Tests**: Add comprehensive test coverage
4. **Update Documentation**: Update API docs and README
5. **Submit PR**: Create pull request with detailed description

### **Code Standards**
- **PEP 8**: Python code style guidelines
- **Type Hints**: Full type annotation coverage
- **Docstrings**: Comprehensive documentation
- **Testing**: 80%+ test coverage requirement

### **Commit Convention**
```bash
# Format: type(scope): description
feat(collectors): add TikTok collector
fix(api): resolve memory leak in image processing
docs(api): update endpoint documentation
test(collectors): add integration tests for Twitter API
refactor(enrichment): optimize CLIP model loading
```

## 📄 **License**

none

## 🆘 **Support**

### **Documentation**
- [API Documentation](http://localhost:8080/docs)
- [Deployment Guide](./DEPLOY.md)
- [Integration Guide](./INTEGRATION_README.md)
- [Testing Guide](./TESTING.md)

### **Community**
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and community support
- **Wiki**: Tutorials, guides, and best practices

### **Professional Support**
- **Enterprise Support**: 24/7 technical support
- **Custom Development**: Tailored solutions and integrations
- **Training**: Comprehensive training programs
- **Consulting**: Architecture review and optimization

---

**B-Search Server** - Enterprise-grade intelligence platform for comprehensive data collection, AI-powered analysis, and actionable insights.
