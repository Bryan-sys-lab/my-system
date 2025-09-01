# B-Search Development Guide

## Overview

This guide provides comprehensive instructions for setting up and using B-Search in a development environment with full DevOps capabilities, monitoring, and development-friendly features.

## 🚀 Development Startup Script

### Features

The `startup-dev.sh` script provides:

- **Development Environment Validation**: Checks for Git repo, required files, and dev setup
- **Relaxed Requirements**: Lower memory/CPU requirements than production
- **Fast Startup**: Optimized for development workflow with shorter timeouts
- **Development Configuration**: Auto-generates dev-friendly `.env` file
- **Hot Reload Support**: Enables development features like auto-restart
- **Error Recovery**: Graceful handling of common development issues
- **Development Tools Setup**: Configures logging, directories, and dev utilities

### Quick Start

```bash
# Basic development startup
cd server && ./startup-dev.sh

# Show help
./startup-dev.sh --help

# Clean development environment and restart
./startup-dev.sh --clean

# Rebuild all containers from scratch
./startup-dev.sh --rebuild

# Start and show logs
./startup-dev.sh --logs

# Start and run basic tests
./startup-dev.sh --test
```

### What It Does

1. **Development Environment Check**
   - Validates Git repository and development files
   - Checks for required dependencies (Python, Docker, etc.)
   - Verifies development directory structure

2. **System Requirements (Relaxed)**
   - Minimum 4GB RAM (recommended 8GB+)
   - Minimum 10GB disk space
   - Basic CPU requirements
   - Network connectivity (optional for offline dev)

3. **Configuration Setup**
   - Auto-generates development `.env` file
   - Sets development-friendly defaults
   - Enables debug mode and development features
   - Configures relaxed security settings

4. **Infrastructure Startup**
   - Starts PostgreSQL, Redis, MinIO with dev settings
   - Shorter startup timeouts for faster development
   - Development-optimized resource allocation

5. **Database Setup**
   - Runs database migrations with dev-friendly settings
   - Creates development database schema
   - Sets up development data (if available)

6. **Python Environment**
   - Creates virtual environment
   - Installs dependencies (with SKIP_HEAVY_DEPS option)
   - Verifies critical imports
   - Sets up development tools

7. **Application Deployment**
   - Starts API with hot reload enabled
   - Starts Celery workers with dev settings
   - Enables development debugging features

8. **Health Checks (Development Mode)**
   - Lightweight health verification
   - Doesn't fail on minor issues
   - Provides helpful error messages and recovery suggestions

9. **Development Tools Setup**
   - Configures logging directories
   - Sets up development data directories
   - Prepares for hot reload and debugging

## 📊 Development Monitoring Script

### Features

The `monitor-dev.sh` script provides:

- **Lightweight Monitoring**: Less aggressive than production monitoring
- **Development-Friendly**: Provides helpful development tips and commands
- **Resource Tracking**: CPU, memory, and Docker container usage
- **Log Analysis**: Checks for errors in recent logs
- **Status Reports**: Quick status overview and actionable commands
- **Development Tools**: Integration with development workflow

### Usage

```bash
# Start continuous development monitoring
cd server && ./monitor-dev.sh

# Run one-time development check
./monitor-dev.sh --once

# Show current development status
./monitor-dev.sh --status

# Generate development report
./monitor-dev.sh --report

# Show recent logs from all services
./monitor-dev.sh --logs

# Show detailed resource usage
./monitor-dev.sh --resources

# Show help
./monitor-dev.sh --help
```

### Development Status Display

The `--status` command shows:
- Current service status (running/stopped)
- Quick access URLs for all services
- Useful development commands
- Development tips and shortcuts

## ⚙️ Development Configuration

### Environment Template

Use `.env.dev.template` for development configuration:

```bash
# Copy development template
cp .env.dev.template .env

# Or let startup script create it automatically
./startup-dev.sh  # Will create .env if missing
```

### Key Development Settings

```bash
# Development mode
DEBUG=True
LOG_LEVEL=DEBUG
ENVIRONMENT=development

# Relaxed security for development
SECRET_KEY=dev_secret_key_...
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Skip heavy dependencies for faster startup
SKIP_HEAVY_DEPS=1

# Development features
ENABLE_DEBUG_TOOLBAR=True
ENABLE_SQL_LOGGING=True
ENABLE_HOT_RELOAD=True

# Development database
POSTGRES_DB=bsearch_dev_db
POSTGRES_USER=dev_user
POSTGRES_PASSWORD=dev_password
```

### API Keys for Development

Add your API keys to `.env` for full functionality:

```bash
# Social Media APIs (optional)
TWITTER_BEARER_TOKEN=your_dev_token
FACEBOOK_GRAPH_TOKEN=your_dev_token
ETHERSCAN_API_KEY=your_dev_key

# Add other API keys as needed
```

## 🛠️ Development Workflow

### Daily Development

1. **Start Development Environment**
   ```bash
   cd server && ./startup-dev.sh
   ```

2. **Monitor Development Services**
   ```bash
   ./monitor-dev.sh --status
   ```

3. **Check Logs**
   ```bash
   docker compose logs -f api
   ```

4. **Access Services**
   - API: http://localhost:8080
   - API Docs: http://localhost:8080/docs
   - MinIO: http://localhost:9000 (minioadmin/minioadmin)

### Code Development

1. **Hot Reload**: API automatically restarts on code changes
2. **Debug Mode**: Detailed error messages and stack traces
3. **SQL Logging**: Database queries logged for debugging
4. **Debug Toolbar**: Web-based debugging interface (if enabled)

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=libs --cov-report=html

# Run specific tests
pytest tests/test_api.py -v

# Run integration tests
pytest tests/integration/ -v
```

### Database Development

```bash
# Access database directly
docker exec -it $(docker ps -q -f name=postgres) psql -U dev_user -d bsearch_dev_db

# Reset database
docker compose down
rm -rf dev-data/postgres
docker compose up -d postgres

# Run migrations
docker exec $(docker ps -q -f name=api) python -m alembic upgrade head
```

## 🔧 Development Commands

### Service Management

```bash
# Start all services
docker compose up -d

# Start specific service
docker compose up -d api

# Restart service
docker compose restart api

# Stop all services
docker compose down

# Stop and remove volumes (clean restart)
docker compose down -v
```

### Log Management

```bash
# View all logs
docker compose logs -f

# View API logs
docker compose logs -f api

# View worker logs
docker compose logs -f workers

# View recent errors
docker compose logs --tail=50 | grep -i error

# Follow logs with timestamps
docker compose logs -f -t
```

### Database Operations

```bash
# Backup database
docker exec $(docker ps -q -f name=postgres) pg_dump -U dev_user bsearch_dev_db > backup.sql

# Restore database
docker exec -i $(docker ps -q -f name=postgres) psql -U dev_user -d bsearch_dev_db < backup.sql

# Check database size
docker exec $(docker ps -q -f name=postgres) psql -U dev_user -d bsearch_dev_db -c "SELECT pg_size_pretty(pg_database_size('bsearch_dev_db'));"
```

### Performance Monitoring

```bash
# Check resource usage
docker stats

# Check container logs size
docker system df -v

# Clean up unused resources
docker system prune -f

# Check network usage
docker network ls
docker network inspect bsearch-dev_default
```

## 🐛 Debugging

### Common Issues

#### API Not Starting

```bash
# Check API logs
docker compose logs api

# Check if port is available
netstat -tlnp | grep :8080

# Restart API
docker compose restart api

# Check API health
curl http://localhost:8080/healthz
```

#### Database Connection Issues

```bash
# Check database logs
docker compose logs postgres

# Test database connection
docker exec $(docker ps -q -f name=postgres) pg_isready -U dev_user -d bsearch_dev_db

# Reset database
docker compose down -v
docker compose up -d postgres
```

#### Redis Connection Issues

```bash
# Check Redis logs
docker compose logs redis

# Test Redis connection
docker exec $(docker ps -q -f name=redis) redis-cli ping

# Restart Redis
docker compose restart redis
```

#### MinIO Issues

```bash
# Check MinIO logs
docker compose logs minio

# Test MinIO connection
curl http://localhost:9000/minio/health/ready

# Access MinIO console
open http://localhost:9000 (minioadmin/minioadmin)
```

### Debug Mode Features

When `DEBUG=True`:

- **Detailed Error Pages**: Full stack traces and error details
- **SQL Query Logging**: All database queries logged
- **Request/Response Logging**: HTTP requests and responses logged
- **Debug Toolbar**: Web-based debugging interface
- **Hot Reload**: Automatic restart on code changes

### Performance Debugging

```bash
# Check slow queries
docker exec $(docker ps -q -f name=postgres) psql -U dev_user -d bsearch_dev_db -c "SELECT * FROM pg_stat_activity;"

# Check Redis slow logs
docker exec $(docker ps -q -f name=redis) redis-cli slowlog get 10

# Profile Python code
python -m cProfile -s time your_script.py

# Check memory usage
docker exec $(docker ps -q -f name=api) ps aux --sort=-%mem | head -10
```

## 🧪 Testing

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ --cov=libs --cov-report=html

# Run specific test file
pytest tests/unit/test_collectors.py -v

# Run tests in watch mode (requires pytest-watch)
pytest-watch tests/unit/ -- -v
```

### Integration Tests

```bash
# Run integration tests
pytest tests/integration/ -v

# Run with environment setup
pytest tests/integration/ --setup-show

# Run API integration tests
pytest tests/integration/test_api.py -v
```

### End-to-End Tests

```bash
# Run E2E tests (requires test data)
pytest tests/e2e/ -v

# Run with browser GUI (for debugging)
pytest tests/e2e/ -v --headed

# Run specific E2E test
pytest tests/e2e/test_full_workflow.py -v
```

### Test Data Management

```bash
# Load test data
python scripts/load_test_data.py

# Reset test database
python scripts/reset_test_db.py

# Generate test fixtures
python scripts/generate_test_fixtures.py
```

## 📊 Development Analytics

### Code Quality

```bash
# Lint code
flake8 libs/ apps/

# Format code
black libs/ apps/

# Type checking
mypy libs/ apps/

# Security scanning
bandit -r libs/ apps/

# Complexity analysis
radon cc libs/ -a
```

### Performance Analysis

```bash
# Profile application
python -m cProfile -o profile.prof -m uvicorn apps.api.main:app
snakeviz profile.prof

# Memory profiling
python -m memory_profiler your_script.py

# Load testing
ab -n 1000 -c 10 http://localhost:8080/healthz
```

### Code Metrics

```bash
# Code coverage
pytest --cov=libs --cov-report=html
open htmlcov/index.html

# Code complexity
radon cc libs/ -s

# Maintainability index
radon mi libs/

# Raw metrics
radon raw libs/
```

## 🔄 Development Workflows

### Feature Development

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-collector
   ```

2. **Start Development Environment**
   ```bash
   cd server && ./startup-dev.sh
   ```

3. **Write Code and Tests**
   ```bash
   # Write code
   # Write tests
   pytest tests/ -v
   ```

4. **Test Integration**
   ```bash
   ./monitor-dev.sh --once
   curl http://localhost:8080/healthz
   ```

5. **Code Review**
   ```bash
   # Run quality checks
   flake8 libs/ apps/
   black libs/ apps/
   mypy libs/ apps/
   ```

6. **Merge and Deploy**
   ```bash
   git add .
   git commit -m "feat: add new collector"
   git push origin feature/new-collector
   ```

### Bug Fixing

1. **Reproduce Issue**
   ```bash
   cd server && ./startup-dev.sh
   # Reproduce the bug
   ```

2. **Debug Issue**
   ```bash
   # Check logs
   docker compose logs -f api

   # Enable debug logging
   export LOG_LEVEL=DEBUG
   docker compose restart api

   # Use debug tools
   python -m pdb your_script.py
   ```

3. **Fix and Test**
   ```bash
   # Fix the code
   pytest tests/ -v
   ./monitor-dev.sh --once
   ```

4. **Verify Fix**
   ```bash
   # Test the fix
   # Run integration tests
   pytest tests/integration/ -v
   ```

### Performance Optimization

1. **Profile Application**
   ```bash
   python -m cProfile -o profile.prof your_slow_function.py
   snakeviz profile.prof
   ```

2. **Identify Bottlenecks**
   ```bash
   # Check database queries
   docker compose logs postgres | grep -i select

   # Check Redis operations
   docker compose logs redis

   # Check API response times
   curl -w "@curl-format.txt" http://localhost:8080/some-endpoint
   ```

3. **Optimize Code**
   ```bash
   # Database query optimization
   # Caching implementation
   # Async processing
   ```

4. **Measure Improvements**
   ```bash
   # Before and after profiling
   # Load testing
   ab -n 1000 -c 10 http://localhost:8080/healthz
   ```

## 🚀 Deployment

### Development to Production

1. **Environment Setup**
   ```bash
   # Copy production template
   cp .env.production.template .env

   # Configure production settings
   nano .env
   ```

2. **Production Startup**
   ```bash
   # Use production startup script
   ./startup-prod.sh
   ```

3. **Production Monitoring**
   ```bash
   # Use production monitoring
   ./monitor-prod.sh
   ```

### CI/CD Integration

```yaml
# .github/workflows/dev-deployment.yml
name: Development Deployment
on:
  push:
    branches: [ develop, main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          cd server
          ./startup-dev.sh --test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to development
        run: |
          cd server
          ./startup-dev.sh
```

## 📚 Resources

### Documentation

- [API Documentation](http://localhost:8080/docs)
- [Production Deployment Guide](./PRODUCTION_DEPLOYMENT.md)
- [Testing Guide](./TESTING.md)
- [Contributing Guide](../CONTRIBUTING.md)

### Tools and Technologies

- **FastAPI**: Web framework
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **MinIO**: Object storage
- **Docker**: Containerization
- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking

### Community and Support

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and community support
- **Wiki**: Tutorials, guides, and best practices
- **Slack**: Real-time community support

---

**Happy coding with B-Search!** 🎉

Your development environment is now fully equipped with comprehensive tooling, monitoring, and automation capabilities.