#!/bin/bash
set -euo pipefail

# B-Search Development Startup Script
# Comprehensive development startup with health checks, error detection, and dev-friendly features
# Version: 1.0.0
# Author: B-Search DevOps Team

# Configuration
SCRIPT_VERSION="1.0.0"
START_TIME=$(date +%s)
LOG_FILE="/tmp/bsearch-dev-startup-$(date +%Y%m%d-%H%M%S).log"
PID_FILE="/tmp/bsearch-dev-startup.pid"
HEALTH_CHECK_TIMEOUT=120
SERVICE_STARTUP_TIMEOUT=90
DEV_MODE=true

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Logging functions
log() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO" "$1"
}

log_warn() {
    log "WARN" "$1"
    echo -e "${YELLOW}[WARN]${NC} $1" >&2
}

log_error() {
    log "ERROR" "$1"
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_success() {
    log "SUCCESS" "$1"
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_dev() {
    log "DEV" "$1"
    echo -e "${CYAN}[DEV]${NC} $1"
}

log_header() {
    local message="$1"
    echo "" | tee -a "$LOG_FILE"
    echo "==================================================================" | tee -a "$LOG_FILE"
    echo "$message" | tee -a "$LOG_FILE"
    echo "==================================================================" | tee -a "$LOG_FILE"
    echo -e "${BLUE}$message${NC}"
    echo -e "${BLUE}$(printf '%.0s=' {1..66})${NC}"
}

# Error handling
trap 'handle_error $? $LINENO' ERR
trap 'cleanup' EXIT

handle_error() {
    local exit_code=$1
    local line_number=$2
    log_error "Script failed at line $line_number with exit code $exit_code"
    log_error "Check $LOG_FILE for detailed logs"
    echo -e "${RED}❌ Development startup failed! Check logs at: $LOG_FILE${NC}" >&2
    exit $exit_code
}

cleanup() {
    if [ -f "$PID_FILE" ]; then
        rm -f "$PID_FILE"
    fi
}

# Development-specific functions
check_dev_environment() {
    log_header "🔧 DEVELOPMENT ENVIRONMENT CHECK"

    # Check if we're in a development environment
    if [ -d ".git" ]; then
        log_dev "Git repository detected - development environment confirmed"
    else
        log_warn "No .git directory found - this might not be a development environment"
    fi

    # Check for development files
    local dev_files=(".env.example" "requirements.txt" "docker-compose.yml" "README.md")
    local missing_files=()

    for file in "${dev_files[@]}"; do
        if [ ! -f "$file" ]; then
            missing_files+=("$file")
        fi
    done

    if [ ${#missing_files[@]} -gt 0 ]; then
        log_error "Missing development files: ${missing_files[*]}"
        log_error "Please ensure you're in the correct project directory"
        return 1
    fi

    log_dev "Development environment validation passed"
    return 0
}

# System validation functions
check_system_requirements() {
    log_header "🔍 SYSTEM REQUIREMENTS CHECK (DEVELOPMENT MODE)"

    # Check OS and architecture
    local os=$(uname -s)
    local arch=$(uname -m)
    log_info "Operating System: $os $arch"

    # Check available memory (lower requirements for dev)
    local total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    local available_mem=$(free -m | awk 'NR==2{printf "%.0f", $7}')

    if [ $total_mem -lt 4096 ]; then
        log_warn "Low memory: ${total_mem}MB (recommended 8GB+ for production, 4GB minimum for dev)"
    fi

    if [ $available_mem -lt 2048 ]; then
        log_warn "Low available memory: ${available_mem}MB (2GB+ recommended for development)"
    fi

    log_info "Memory: ${total_mem}MB total, ${available_mem}MB available"

    # Check available disk space (lower requirements for dev)
    local disk_space=$(df / | awk 'NR==2{printf "%.0f", $4/1024}')
    if [ $disk_space -lt 10 ]; then
        log_error "Insufficient disk space: ${disk_space}GB (minimum 10GB required)"
        return 1
    fi
    log_info "Disk space: ${disk_space}GB available"

    # Check CPU cores
    local cpu_cores=$(nproc)
    if [ $cpu_cores -lt 2 ]; then
        log_warn "Low CPU cores: $cpu_cores (2+ recommended for optimal development performance)"
    fi
    log_info "CPU cores: $cpu_cores"

    return 0
}

check_dependencies() {
    log_header "🔧 DEPENDENCY CHECK (DEVELOPMENT MODE)"

    local missing_deps=()

    # Check Docker
    if ! command -v docker >/dev/null 2>&1; then
        missing_deps+=("docker")
    else
        local docker_version=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        log_info "Docker version: $docker_version"

        if ! docker info >/dev/null 2>&1; then
            log_error "Docker daemon is not running"
            return 1
        fi
    fi

    # Check Docker Compose
    if command -v docker-compose >/dev/null 2>&1; then
        local compose_version=$(docker-compose --version | cut -d' ' -f3)
        log_info "Docker Compose version: $compose_version"
    elif docker compose version >/dev/null 2>&1; then
        local compose_version=$(docker compose version | cut -d' ' -f4)
        log_info "Docker Compose (plugin) version: $compose_version"
    else
        missing_deps+=("docker-compose")
    fi

    # Check Python
    if ! command -v python3 >/dev/null 2>&1; then
        missing_deps+=("python3")
    else
        local python_version=$(python3 --version | cut -d' ' -f2)
        log_info "Python version: $python_version"
    fi

    # Check git
    if ! command -v git >/dev/null 2>&1; then
        log_warn "Git not found - version control features will be limited"
    else
        local git_version=$(git --version | cut -d' ' -f3)
        log_info "Git version: $git_version"
    fi

    # Optional development tools
    local optional_tools=("curl" "jq" "make" "npm" "node")
    for tool in "${optional_tools[@]}"; do
        if ! command -v "$tool" >/dev/null 2>&1; then
            log_warn "$tool not found - some development features may be limited"
        fi
    done

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing required dependencies: ${missing_deps[*]}"
        log_error "Please install missing dependencies and try again"
        return 1
    fi

    return 0
}

validate_configuration() {
    log_header "⚙️ CONFIGURATION VALIDATION (DEVELOPMENT MODE)"

    # Check .env file
    if [ ! -f ".env" ]; then
        log_warn ".env file not found. Creating development configuration..."
        create_dev_env
    fi

    # Validate required environment variables (relaxed for dev)
    local required_vars=("POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_DB")
    local missing_vars=()

    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env 2>/dev/null; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        log_error "Please set these variables in .env file"
        return 1
    fi

    # Check for development-friendly settings
    if grep -q "DEBUG=False" .env 2>/dev/null; then
        log_warn "DEBUG is set to False - consider enabling for development"
    fi

    if grep -q "LOG_LEVEL=INFO" .env 2>/dev/null; then
        log_dev "Consider setting LOG_LEVEL=DEBUG for more verbose development logging"
    fi

    log_dev "Configuration validation passed"
    return 0
}

create_dev_env() {
    log_dev "Creating development environment configuration..."

    cat > .env << 'EOF'
# Development Database Configuration
POSTGRES_USER=dev_user
POSTGRES_PASSWORD=dev_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=bsearch_dev_db

# Development Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# Development MinIO Configuration
MINIO_ENDPOINT=minio:9000
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin
MINIO_BUCKET=bsearch-dev-bucket

# Development Application Security
SECRET_KEY=dev_secret_key_change_in_production_12345678901234567890
RUN_ALL_SECRET=dev_run_all_secret_1234567890

# Development API Keys (Add your own for testing)
TWITTER_BEARER_TOKEN=
FACEBOOK_GRAPH_TOKEN=
IG_GRAPH_TOKEN=
TELEGRAM_BOT_TOKEN=
DISCORD_BOT_TOKEN=
MASTODON_ACCESS_TOKEN=
ETHERSCAN_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=

# Development Settings
DEBUG=True
LOG_LEVEL=DEBUG
SKIP_HEAVY_DEPS=1
ENVIRONMENT=development

# Development Performance Settings
WORKER_CONCURRENCY=2
MAX_REQUEST_SIZE=50MB
REQUEST_TIMEOUT=30

# Development Monitoring (Lightweight)
PROMETHEUS_METRICS_ENABLED=False
SENTRY_DSN=

# Development Features
ENABLE_HOT_RELOAD=True
ENABLE_DEBUG_TOOLBAR=True
ENABLE_SQL_LOGGING=True
ENABLE_CORS=true

# Development Database (Lighter settings)
DATABASE_POOL_SIZE=5
DATABASE_POOL_TIMEOUT=30
REDIS_POOL_SIZE=5

# Development Security (Relaxed for dev)
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
CORS_ORIGINS=http://localhost:3000,http://localhost:8080,http://localhost:5173
RATE_LIMIT_REQUESTS=10000
RATE_LIMIT_WINDOW=3600

# Development File Paths
LOG_FILE=/tmp/bsearch-dev.log
DATA_DIR=./dev-data
TEMP_DIR=/tmp/bsearch-dev

# Development Git/Version Control
GIT_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
GIT_COMMIT=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_DATE=$(date -Iseconds)
EOF

    log_dev "Created .env file with development-friendly settings"
    log_warn "Please review and customize .env file with your API keys for full functionality"
}

check_network_connectivity() {
    log_header "🌐 NETWORK CONNECTIVITY CHECK (DEVELOPMENT MODE)"

    # Test internet connectivity (with timeout for dev)
    if ! timeout 5 curl -s --connect-timeout 3 https://www.google.com >/dev/null; then
        log_warn "No internet connectivity detected - some features may not work"
        log_dev "Continuing in offline development mode..."
        return 0  # Don't fail in dev mode
    fi
    log_info "Internet connectivity: OK"

    # Test DNS resolution
    if ! timeout 3 nslookup google.com >/dev/null 2>&1; then
        log_warn "DNS resolution may have issues"
    else
        log_info "DNS resolution: OK"
    fi

    return 0
}

start_infrastructure_services() {
    log_header "🏗️ STARTING INFRASTRUCTURE SERVICES (DEVELOPMENT MODE)"

    # Create required directories
    mkdir -p logs dev-data/minio dev-data/postgres dev-data/redis

    # Start core services with development-friendly settings
    log_info "Starting PostgreSQL, Redis, and MinIO (development mode)..."

    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose up -d postgres redis minio
    else
        docker compose up -d postgres redis minio
    fi

    # Wait for services to be healthy (shorter timeout for dev)
    log_info "Waiting for services to become healthy..."
    local start_time=$(date +%s)

    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))

        if [ $elapsed -gt $SERVICE_STARTUP_TIMEOUT ]; then
            log_error "Services failed to start within ${SERVICE_STARTUP_TIMEOUT}s timeout"
            return 1
        fi

        # Check PostgreSQL
        if docker exec $(docker ps -q -f name=postgres 2>/dev/null) pg_isready -U ${POSTGRES_USER:-dev_user} -d ${POSTGRES_DB:-bsearch_dev_db} >/dev/null 2>&1; then
            log_success "PostgreSQL is ready"
            postgres_ready=true
        else
            postgres_ready=false
        fi

        # Check Redis
        if docker exec $(docker ps -q -f name=redis 2>/dev/null) redis-cli ping 2>/dev/null | grep -q "PONG"; then
            log_success "Redis is ready"
            redis_ready=true
        else
            redis_ready=false
        fi

        # Check MinIO
        if timeout 3 curl -s http://localhost:9000/minio/health/ready >/dev/null 2>&1; then
            log_success "MinIO is ready"
            minio_ready=true
        else
            minio_ready=false
        fi

        if [ "$postgres_ready" = true ] && [ "$redis_ready" = true ] && [ "$minio_ready" = true ]; then
            break
        fi

        sleep 2
    done

    # Start optional development services
    if grep -q "^ENABLE_MONITORING=True" .env 2>/dev/null; then
        log_dev "Starting monitoring services..."
        if command -v docker-compose >/dev/null 2>&1; then
            docker-compose up -d prometheus grafana
        else
            docker compose up -d prometheus grafana
        fi
    fi

    log_success "Infrastructure services started successfully"
    return 0
}

run_database_migrations() {
    log_header "🗄️ DATABASE MIGRATIONS (DEVELOPMENT MODE)"

    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    local retries=15
    while [ $retries -gt 0 ]; do
        if docker exec $(docker ps -q -f name=postgres 2>/dev/null) pg_isready -U ${POSTGRES_USER:-dev_user} -d ${POSTGRES_DB:-bsearch_dev_db} >/dev/null 2>&1; then
            break
        fi
        retries=$((retries - 1))
        sleep 1
    done

    if [ $retries -eq 0 ]; then
        log_error "Database failed to become ready"
        return 1
    fi

    # Run migrations if migration script exists
    if [ -f "infra/migrations/init.sql" ]; then
        log_info "Running database initialization..."
        docker exec -i $(docker ps -q -f name=postgres) psql -U ${POSTGRES_USER:-dev_user} -d ${POSTGRES_DB:-bsearch_dev_db} < infra/migrations/init.sql
        log_success "Database initialized successfully"
    else
        log_dev "No database migration script found - using auto-migration"
    fi

    return 0
}

setup_python_environment() {
    log_header "🐍 PYTHON ENVIRONMENT SETUP (DEVELOPMENT MODE)"

    # Create virtual environment
    if [ ! -d ".venv" ]; then
        log_dev "Creating Python virtual environment..."
        python3 -m venv .venv
    fi

    # Activate virtual environment
    source .venv/bin/activate

    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip

    # Install dependencies (development mode - may skip heavy deps)
    log_info "Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        if grep -q "SKIP_HEAVY_DEPS=1" .env 2>/dev/null; then
            log_dev "Installing lightweight dependencies (SKIP_HEAVY_DEPS=1)"
            pip install -r requirements.txt --no-deps
        else
            pip install -r requirements.txt
        fi
    else
        log_error "requirements.txt not found"
        return 1
    fi

    # Install development dependencies
    if [ -f "requirements-dev.txt" ]; then
        log_dev "Installing development dependencies..."
        pip install -r requirements-dev.txt
    fi

    # Verify critical imports
    log_info "Verifying critical imports..."
    python3 -c "
import sys
critical_modules = ['fastapi', 'sqlalchemy', 'uvicorn']
missing = []
for module in critical_modules:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)

if missing:
    print(f'Missing modules: {missing}')
    sys.exit(1)
else:
    print('All critical modules available')
"

    if [ $? -ne 0 ]; then
        log_error "Critical Python modules missing"
        return 1
    fi

    log_success "Python environment setup complete"
    return 0
}

start_application_services() {
    log_header "🚀 STARTING APPLICATION SERVICES (DEVELOPMENT MODE)"

    # Start Celery workers (lighter for dev)
    log_info "Starting Celery workers (development mode)..."
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose up -d workers
    else
        docker compose up -d workers
    fi

    # Start API service with development settings
    log_info "Starting API service (development mode)..."
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose up -d api
    else
        docker compose up -d api
    fi

    # Start Label Studio if configured and requested
    if grep -q "^ENABLE_LABEL_STUDIO=True" .env 2>/dev/null; then
        log_dev "Starting Label Studio..."
        if command -v docker-compose >/dev/null 2>&1; then
            docker-compose up -d label-studio
        else
            docker compose up -d label-studio
        fi
    fi

    log_success "Application services started"
    return 0
}

perform_health_checks() {
    log_header "🏥 HEALTH CHECKS (DEVELOPMENT MODE)"

    local health_check_start=$(date +%s)
    local all_healthy=true

    # API Health Check (with dev timeout)
    log_info "Checking API health..."
    local api_retries=5
    while [ $api_retries -gt 0 ]; do
        if timeout 5 curl -s --max-time 3 http://localhost:8080/healthz | jq -e '.status == "healthy"' >/dev/null 2>&1; then
            log_success "API health check passed"
            break
        fi
        api_retries=$((api_retries - 1))
        sleep 1
    done

    if [ $api_retries -eq 0 ]; then
        log_warn "API health check failed - this is normal during initial startup"
        all_healthy=false
    fi

    # Database connectivity check
    log_info "Checking database connectivity..."
    if docker exec $(docker ps -q -f name=postgres 2>/dev/null) pg_isready -U ${POSTGRES_USER:-dev_user} -d ${POSTGRES_DB:-bsearch_dev_db} >/dev/null 2>&1; then
        log_success "Database connectivity check passed"
    else
        log_error "Database connectivity check failed"
        all_healthy=false
    fi

    # Redis connectivity check
    log_info "Checking Redis connectivity..."
    if docker exec $(docker ps -q -f name=redis 2>/dev/null) redis-cli ping 2>/dev/null | grep -q "PONG"; then
        log_success "Redis connectivity check passed"
    else
        log_error "Redis connectivity check failed"
        all_healthy=false
    fi

    # MinIO connectivity check
    log_info "Checking MinIO connectivity..."
    if timeout 3 curl -s http://localhost:9000/minio/health/ready >/dev/null 2>&1; then
        log_success "MinIO connectivity check passed"
    else
        log_warn "MinIO connectivity check failed - this is normal if MinIO is still starting"
        all_healthy=false
    fi

    # API endpoints check (lighter for dev)
    log_info "Checking critical API endpoints..."
    local endpoints=(
        "http://localhost:8080/healthz"
        "http://localhost:8080/docs"
    )

    for endpoint in "${endpoints[@]}"; do
        if timeout 3 curl -s --max-time 2 "$endpoint" >/dev/null 2>&1; then
            log_success "Endpoint $endpoint is accessible"
        else
            log_warn "Endpoint $endpoint is not accessible yet"
        fi
    done

    # Performance check (optional for dev)
    if [ "$all_healthy" = true ]; then
        log_info "Running performance baseline check..."
        local perf_start=$(date +%s)
        timeout 3 curl -s http://localhost:8080/healthz >/dev/null
        local perf_end=$(date +%s)
        local response_time=$((perf_end - perf_start))

        if [ $response_time -gt 3 ]; then  # More lenient for dev
            log_warn "Slow API response time: ${response_time}s (expected < 3s)"
        else
            log_info "API response time: ${response_time}s"
        fi
    fi

    local health_check_end=$(date +%s)
    local total_health_time=$((health_check_end - health_check_start))

    if [ $all_healthy = true ]; then
        log_success "All health checks passed (${total_health_time}s)"
        return 0
    else
        log_warn "Some health checks failed (${total_health_time}s) - this is normal during development"
        log_dev "Services may still be starting up. Check status with: docker compose ps"
        return 0  # Don't fail in dev mode
    fi
}

setup_development_tools() {
    log_header "🛠️ DEVELOPMENT TOOLS SETUP"

    # Setup git hooks if available
    if [ -d ".git" ] && [ -d ".git-hooks" ]; then
        log_dev "Setting up git hooks..."
        find .git-hooks -type f -exec chmod +x {} \;
        # Note: Actual git hooks setup would require more complex logic
    fi

    # Create development directories
    mkdir -p dev-data/logs dev-data/uploads dev-data/cache

    # Setup development database if using SQLite
    if grep -q "DATABASE_URL.*sqlite" .env 2>/dev/null; then
        log_dev "Setting up SQLite database for development..."
        touch dev-data/bsearch-dev.db
    fi

    # Setup log files
    touch logs/bsearch-dev.log
    touch logs/workers-dev.log

    log_dev "Development tools setup complete"
}

display_development_info() {
    log_header "🎉 B-SEARCH DEVELOPMENT ENVIRONMENT READY"

    local end_time=$(date +%s)
    local total_time=$((end_time - START_TIME))

    echo ""
    echo -e "${GREEN}✅ Development startup completed in ${total_time}s${NC}"
    echo ""

    echo -e "${CYAN}🚀 Development Services:${NC}"
    echo -e "  🌐 API Gateway:     http://localhost:8080"
    echo -e "  📚 API Docs:        http://localhost:8080/docs"
    echo -e "  🔄 API ReDoc:       http://localhost:8080/redoc"
    echo -e "  📊 Prometheus:      http://localhost:9090 (if enabled)"
    echo -e "  📈 Grafana:         http://localhost:3000 (if enabled)"
    echo -e "  🗄️  PostgreSQL:      localhost:5432"
    echo -e "  🔄 Redis:           localhost:6379"
    echo -e "  📦 MinIO:           http://localhost:9000"
    echo -e "  🏷️  Label Studio:    http://localhost:8081 (if enabled)"

    echo ""
    echo -e "${CYAN}🛠️ Development Commands:${NC}"
    echo -e "  View logs:          docker compose logs -f"
    echo -e "  Stop services:      docker compose down"
    echo -e "  Restart API:        docker compose restart api"
    echo -e "  Check status:       docker compose ps"
    echo -e "  Health check:       curl http://localhost:8080/healthz"

    echo ""
    echo -e "${CYAN}🐛 Development Features:${NC}"
    echo -e "  🔄 Hot Reload:      Enabled (API auto-restarts on code changes)"
    echo -e "  🐛 Debug Mode:       Enabled (detailed error messages)"
    echo -e "  📝 SQL Logging:      $(grep -q "ENABLE_SQL_LOGGING=True" .env 2>/dev/null && echo "Enabled" || echo "Disabled")"
    echo -e "  🔍 Debug Toolbar:    $(grep -q "ENABLE_DEBUG_TOOLBAR=True" .env 2>/dev/null && echo "Enabled" || echo "Disabled")"
    echo -e "  🌐 CORS:            Enabled for development"

    echo ""
    echo -e "${CYAN}📝 Development Tips:${NC}"
    echo -e "  • Use 'docker compose logs -f api' to watch API logs"
    echo -e "  • API will auto-reload when you modify Python files"
    echo -e "  • Check $LOG_FILE for detailed startup logs"
    echo -e "  • Use 'make test' to run tests (if available)"
    echo -e "  • Visit /docs for interactive API documentation"

    echo ""
    echo -e "${YELLOW}⚠️ Development Notes:${NC}"
    echo -e "  • This is a development environment - not suitable for production"
    echo -e "  • Default passwords are used - change for security"
    echo -e "  • Some features may be disabled (SKIP_HEAVY_DEPS=1)"
    echo -e "  • Add your API keys to .env for full functionality"
    echo -e "  • Use production startup script for production deployment"

    echo ""
    echo -e "${BLUE}🎯 Happy coding with B-Search!${NC}"
}

# Main execution
main() {
    # Create PID file
    echo $$ > "$PID_FILE"

    log_header "🚀 B-SEARCH DEVELOPMENT STARTUP v$SCRIPT_VERSION"
    log_info "Log file: $LOG_FILE"
    log_info "PID file: $PID_FILE"
    log_dev "Development mode: Enabled"

    # Development environment checks
    check_dev_environment || exit 1

    # Pre-flight checks
    check_system_requirements || exit 1
    check_dependencies || exit 1
    check_network_connectivity || true  # Don't fail on network issues in dev
    validate_configuration || exit 1

    # Start infrastructure
    start_infrastructure_services || {
        log_error "Failed to start infrastructure services"
        log_dev "Try: docker compose down && docker compose up -d"
        exit 1
    }

    # Database setup
    run_database_migrations || {
        log_error "Failed to run database migrations"
        log_dev "Check database logs: docker compose logs postgres"
        exit 1
    }

    # Python environment
    setup_python_environment || {
        log_error "Failed to setup Python environment"
        log_dev "Try: rm -rf .venv && python3 -m venv .venv"
        exit 1
    }

    # Start application services
    start_application_services || {
        log_error "Failed to start application services"
        log_dev "Check service logs: docker compose logs"
        exit 1
    }

    # Health checks (relaxed for dev)
    perform_health_checks || true  # Don't fail on health check issues in dev

    # Development tools setup
    setup_development_tools

    # Display development info
    display_development_info

    # Remove PID file
    rm -f "$PID_FILE"

    log_success "Development startup completed successfully"
    exit 0
}

# Command line options
case "${1:-}" in
    --help|-h)
        echo "B-Search Development Startup Script v$SCRIPT_VERSION"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h              Show this help message"
        echo "  --version, -v           Show version information"
        echo "  --clean                 Clean development environment and restart"
        echo "  --rebuild               Rebuild all containers from scratch"
        echo "  --logs                  Show recent logs after startup"
        echo "  --test                  Run basic functionality tests"
        echo ""
        echo "Environment Variables:"
        echo "  LOG_FILE                Custom log file path (default: auto-generated)"
        echo "  DEBUG                   Enable debug mode (default: True)"
        echo "  SKIP_HEAVY_DEPS         Skip heavy ML dependencies (default: 1)"
        echo ""
        exit 0
        ;;
    --version|-v)
        echo "B-Search Development Startup Script v$SCRIPT_VERSION"
        exit 0
        ;;
    --clean)
        log_info "Cleaning development environment..."
        docker compose down -v --remove-orphans
        rm -rf .venv logs dev-data .env
        log_success "Development environment cleaned"
        exit 0
        ;;
    --rebuild)
        log_info "Rebuilding all containers..."
        docker compose down
        docker compose build --no-cache
        log_success "Containers rebuilt"
        exit 0
        ;;
    --logs)
        main "$@" && docker compose logs -f --tail=50
        ;;
    --test)
        main "$@" && run_development_tests
        ;;
    *)
        main "$@"
        ;;
esac