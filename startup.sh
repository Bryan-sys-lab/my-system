#!/bin/bash
set -e

# B-Search System Startup Script
# This script starts all services and the application with enhanced collectors

echo "🚀 Starting B-Search System with Enhanced Collectors..."
echo "======================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    print_status "Docker is running"
}

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose >/dev/null 2>&1 && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_status "Docker Compose is available"
}

# Create .env file if it doesn't exist
create_env_file() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating default configuration..."
        cat > .env << 'EOF'
# Database Configuration
POSTGRES_USER=testuser
POSTGRES_PASSWORD=testpass
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=bsearch_db

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# MinIO Configuration
MINIO_ENDPOINT=minio:9000
MINIO_ROOT_USER=testminio
MINIO_ROOT_PASSWORD=testminiopass
MINIO_BUCKET=bsearch-bucket

# Application Security
SECRET_KEY=your_super_secret_key_here_change_this_in_production
RUN_ALL_SECRET=your_run_all_secret_here
GOOGLE_GEOLOCATION_API_KEY=test_key

# Optional API Keys (leave empty if not using)
TWITTER_BEARER_TOKEN=
FACEBOOK_GRAPH_TOKEN=
IG_GRAPH_TOKEN=
TELEGRAM_BOT_TOKEN=
DISCORD_BOT_TOKEN=
MASTODON_ACCESS_TOKEN=

# Development Settings
SKIP_HEAVY_DEPS=1
DEBUG=True
EOF
        print_status "Created .env file with default configuration"
        print_warning "Please edit .env file and add your real API keys and secrets!"
    else
        print_status ".env file already exists"
    fi
}

# Start Docker services
start_docker_services() {
    print_status "Starting Docker services (PostgreSQL, Redis, MinIO, Prometheus, Grafana)..."
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose up -d
    else
        docker compose up -d
    fi

    print_status "Waiting 30 seconds for services to be ready..."
    sleep 30

    # Check if services are running
    if command -v docker-compose >/dev/null 2>&1; then
        if docker-compose ps | grep -q "Up"; then
            print_status "Docker services are running"
        else
            print_error "Some Docker services failed to start"
            docker-compose logs
            exit 1
        fi
    else
        if docker compose ps | grep -q "Up"; then
            print_status "Docker services are running"
        else
            print_error "Some Docker services failed to start"
            docker compose logs
            exit 1
        fi
    fi
}

# Run database migrations
run_migrations() {
    if [ -x "./migrate.sh" ]; then
        print_status "Running database migrations..."
        ./migrate.sh
    else
        print_warning "migrate.sh not found or not executable. Skipping migrations."
    fi
}

# Setup Python environment
setup_python() {
    print_status "Setting up Python environment..."

    # Create virtual environment if it doesn't exist
    if [ ! -d ".venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv .venv
    fi

    # Activate virtual environment
    source .venv/bin/activate

    # Install/update pip
    pip install -U pip

    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
}

# Start the application
start_application() {
    print_status "Starting FastAPI application..."

    # Check if uvicorn is already running
    if pgrep -f "uvicorn apps.api.main" >/dev/null 2>&1; then
        print_warning "Uvicorn is already running"
    else
        # Ensure logs directory exists
        mkdir -p logs

        # Start uvicorn in background
        nohup python -m uvicorn apps.api.main:app --host 0.0.0.0 --port 8000 --reload > logs/uvicorn.log 2>&1 &
        sleep 2

        # Check if it started successfully
        if pgrep -f "uvicorn apps.api.main" >/dev/null 2>&1; then
            print_status "FastAPI application started successfully"
            print_status "Application is running at: http://localhost:8000"
            print_status "API documentation at: http://localhost:8000/docs"
        else
            print_error "Failed to start FastAPI application"
            echo "Check logs/uvicorn.log for details"
            exit 1
        fi
    fi
}

# Display service information
show_service_info() {
    echo ""
    echo -e "${BLUE}🎉 B-Search System Started Successfully!${NC}"
    echo "=============================================="
    echo ""
    echo -e "${GREEN}Services Running:${NC}"
    echo "  🌐 FastAPI Application: http://localhost:8000"
    echo "  📚 API Documentation:   http://localhost:8000/docs"
    echo "  📊 Prometheus:          http://localhost:9090"
    echo "  📈 Grafana:             http://localhost:3000 (admin/admin)"
    echo "  🗄️  PostgreSQL:          localhost:5432"
    echo "  🔄 Redis:               localhost:6379"
    echo "  📦 MinIO:               http://localhost:9000"
    echo ""
    echo -e "${GREEN}Enhanced Collectors Available:${NC}"
    echo "  ✅ Reddit (with Wayback fallback)"
    echo "  ✅ YouTube RSS feeds"
    echo "  ✅ Web scraping with fallbacks"
    echo "  ✅ Twitter (API → Nitter → Web Scraper → Wayback)"
    echo "  ✅ Facebook (API → Web Scraper → Wayback)"
    echo "  ✅ Instagram (API → Web Scraper → Wayback)"
    echo "  ✅ Telegram (API → Wayback)"
    echo "  ✅ Discord (API → Wayback)"
    echo "  ✅ Mastodon (API → Public API)"
    echo "  ✅ Bluesky (Public API)"
    echo "  ✅ TikTok (yt-dlp)"
    echo ""
    echo -e "${YELLOW}Test Commands:${NC}"
    echo "  curl http://localhost:8000/healthz"
    echo "  curl -X POST 'http://localhost:8000/collect/run_all/stream' \\"
    echo "    -H 'Content-Type: application/json' \\"
    echo "    -d '{\"query\": \"test\", \"limit\": 5, \"whitelist\": [\"reddit\", \"web\"], \"secret\": \"your_run_all_secret_here\"}'"
    echo ""
    echo -e "${BLUE}To stop all services:${NC}"
    echo "  docker-compose down"
    echo "  pkill -f uvicorn"
}

# Main execution
main() {
    echo "Checking prerequisites..."
    check_docker
    check_docker_compose

    echo ""
    create_env_file

    echo ""
    start_docker_services

    echo ""
    run_migrations

    echo ""
    setup_python

    echo ""
    start_application

    show_service_info
}

# Run main function
main "$@"