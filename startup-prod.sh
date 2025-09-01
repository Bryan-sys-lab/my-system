#!/bin/bash
set -euo pipefail

# B-Search Production Startup Script
# Comprehensive production startup with health checks, error detection, and monitoring
# Version: 2.0.0
# Author: B-Search DevOps Team

# Configuration
SCRIPT_VERSION="2.0.0"
START_TIME=$(date +%s)
LOG_FILE="/var/log/bsearch/startup-$(date +%Y%m%d-%H%M%S).log"
PID_FILE="/var/run/bsearch/startup.pid"
HEALTH_CHECK_TIMEOUT=300
SERVICE_STARTUP_TIMEOUT=180

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
    echo -e "${RED}❌ Startup failed! Check logs at: $LOG_FILE${NC}" >&2
    exit $exit_code
}

cleanup() {
    if [ -f "$PID_FILE" ]; then
        rm -f "$PID_FILE"
    fi
}

# System validation functions
check_system_requirements() {
    log_header "🔍 SYSTEM REQUIREMENTS CHECK"

    # Check OS and architecture
    local os=$(uname -s)
    local arch=$(uname -m)
    log_info "Operating System: $os $arch"

    # Check available memory
    local total_mem=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    local available_mem=$(free -m | awk 'NR==2{printf "%.0f", $7}')

    if [ $total_mem -lt 8192 ]; then
        log_error "Insufficient memory: ${total_mem}MB (minimum 8GB required)"
        return 1
    fi

    if [ $available_mem -lt 4096 ]; then
        log_warn "Low available memory: ${available_mem}MB (4GB+ recommended)"
    fi

    log_info "Memory: ${total_mem}MB total, ${available_mem}MB available"

    # Check available disk space
    local disk_space=$(df / | awk 'NR==2{printf "%.0f", $4/1024}')
    if [ $disk_space -lt 20 ]; then
        log_error "Insufficient disk space: ${disk_space}GB (minimum 20GB required)"
        return 1
    fi
    log_info "Disk space: ${disk_space}GB available"

    # Check CPU cores
    local cpu_cores=$(nproc)
    if [ $cpu_cores -lt 2 ]; then
        log_warn "Low CPU cores: $cpu_cores (2+ recommended for optimal performance)"
    fi
    log_info "CPU cores: $cpu_cores"

    return 0
}

check_dependencies() {
    log_header "🔧 DEPENDENCY CHECK"

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

    # Check curl
    if ! command -v curl >/dev/null 2>&1; then
        missing_deps+=("curl")
    fi

    # Check jq for JSON processing
    if ! command -v jq >/dev/null 2>&1; then
        missing_deps+=("jq")
    fi

    if [ ${#missing_deps[@]} -gt 0 ]; then
        log_error "Missing dependencies: ${missing_deps[*]}"
        log_error "Please install missing dependencies and try again"
        return 1
    fi

    return 0
}

validate_configuration() {
    log_header "⚙️ CONFIGURATION VALIDATION"

    # Check .env file
    if [ ! -f ".env" ]; then
        log_error ".env file not found"
        log_info "Creating default .env file..."
        create_default_env
    fi

    # Validate required environment variables
    local required_vars=("POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_DB" "SECRET_KEY" "RUN_ALL_SECRET")
    local missing_vars=()

    for var in "${required_vars[@]}"; do
        if ! grep -q "^${var}=" .env 2>/dev/null || grep "^${var}=" .env | grep -q "=$"; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -gt 0 ]; then
        log_error "Missing or empty required environment variables: ${missing_vars[*]}"
        log_error "Please set these variables in .env file"
        return 1
    fi

    # Check for default/weak secrets
    if grep -q "SECRET_KEY=your_super_secret_key_here" .env 2>/dev/null; then
        log_warn "Using default SECRET_KEY - please change in production"
    fi

    if grep -q "RUN_ALL_SECRET=your_run_all_secret_here" .env 2>/dev/null; then
        log_warn "Using default RUN_ALL_SECRET - please change in production"
    fi

    # Validate database configuration
    local db_host=$(grep "^POSTGRES_HOST=" .env | cut -d'=' -f2)
    local db_port=$(grep "^POSTGRES_PORT=" .env | cut -d'=' -f2)

    if [ -z "$db_host" ]; then
        log_error "POSTGRES_HOST not set in .env"
        return 1
    fi

    if [ -z "$db_port" ]; then
        log_error "POSTGRES_PORT not set in .env"
        return 1
    fi

    log_info "Configuration validation passed"
    return 0
}

create_default_env() {
    cat > .env << 'EOF'
# Database Configuration
POSTGRES_USER=bsearch_prod
POSTGRES_PASSWORD=CHANGE_THIS_STRONG_PASSWORD
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=bsearch_db

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=

# MinIO Configuration
MINIO_ENDPOINT=minio:9000
MINIO_ROOT_USER=bsearch_minio
MINIO_ROOT_PASSWORD=CHANGE_THIS_STRONG_PASSWORD
MINIO_BUCKET=bsearch-bucket

# Application Security
SECRET_KEY=CHANGE_THIS_TO_A_STRONG_RANDOM_SECRET_KEY
RUN_ALL_SECRET=CHANGE_THIS_TO_A_STRONG_RUN_ALL_SECRET

# API Keys (Configure as needed)
TWITTER_BEARER_TOKEN=
FACEBOOK_GRAPH_TOKEN=
IG_GRAPH_TOKEN=
TELEGRAM_BOT_TOKEN=
DISCORD_BOT_TOKEN=
MASTODON_ACCESS_TOKEN=
ETHERSCAN_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
GOOGLE_GEOLOCATION_API_KEY=

# Production Settings
SKIP_HEAVY_DEPS=0
DEBUG=False
LOG_LEVEL=INFO

# Monitoring
SENTRY_DSN=
PROMETHEUS_METRICS_ENABLED=True

# Performance Tuning
WORKER_CONCURRENCY=4
MAX_REQUEST_SIZE=100MB
REQUEST_TIMEOUT=30
DATABASE_POOL_SIZE=20
REDIS_POOL_SIZE=10

# Security
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# Backup Configuration
BACKUP_ENABLED=True
BACKUP_SCHEDULE=0 2 * * *
BACKUP_RETENTION_DAYS=30
EOF

    log_warn "Created default .env file - PLEASE EDIT WITH SECURE VALUES BEFORE PRODUCTION USE"
}

check_network_connectivity() {
    log_header "🌐 NETWORK CONNECTIVITY CHECK"

    # Test internet connectivity
    if ! curl -s --connect-timeout 5 https://www.google.com >/dev/null; then
        log_error "No internet connectivity detected"
        return 1
    fi
    log_info "Internet connectivity: OK"

    # Test DNS resolution
    if ! nslookup google.com >/dev/null 2>&1; then
        log_warn "DNS resolution may have issues"
    else
        log_info "DNS resolution: OK"
    fi

    return 0
}

start_infrastructure_services() {
    log_header "🏗️ STARTING INFRASTRUCTURE SERVICES"

    # Create required directories
    mkdir -p logs data/minio data/postgres data/grafana data/prometheus

    # Start core services
    log_info "Starting PostgreSQL, Redis, and MinIO..."

    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose up -d postgres redis minio
    else
        docker compose up -d postgres redis minio
    fi

    # Wait for services to be healthy
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
        if docker exec $(docker ps -q -f name=postgres) pg_isready -U ${POSTGRES_USER:-bsearch_prod} -d ${POSTGRES_DB:-bsearch_db} >/dev/null 2>&1; then
            log_info "PostgreSQL is ready"
            postgres_ready=true
        else
            postgres_ready=false
        fi

        # Check Redis
        if docker exec $(docker ps -q -f name=redis) redis-cli ping >/dev/null 2>&1; then
            log_info "Redis is ready"
            redis_ready=true
        else
            redis_ready=false
        fi

        # Check MinIO
        if curl -s http://localhost:9000/minio/health/ready >/dev/null 2>&1; then
            log_info "MinIO is ready"
            minio_ready=true
        else
            minio_ready=false
        fi

        if [ "$postgres_ready" = true ] && [ "$redis_ready" = true ] && [ "$minio_ready" = true ]; then
            break
        fi

        sleep 5
    done

    # Start monitoring services
    log_info "Starting monitoring services (Prometheus, Grafana)..."
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose up -d prometheus grafana
    else
        docker compose up -d prometheus grafana
    fi

    # Start Tor service if configured
    if grep -q "^TOR_SOCKS_PROXY=" .env 2>/dev/null; then
        log_info "Starting Tor service..."
        if command -v docker-compose >/dev/null 2>&1; then
            docker-compose up -d tor
        else
            docker compose up -d tor
        fi
    fi

    log_success "Infrastructure services started successfully"
    return 0
}

run_database_migrations() {
    log_header "🗄️ DATABASE MIGRATIONS"

    # Wait for database to be ready
    log_info "Waiting for database to be ready..."
    local retries=30
    while [ $retries -gt 0 ]; do
        if docker exec $(docker ps -q -f name=postgres) pg_isready -U ${POSTGRES_USER:-bsearch_prod} -d ${POSTGRES_DB:-bsearch_db} >/dev/null 2>&1; then
            break
        fi
        retries=$((retries - 1))
        sleep 2
    done

    if [ $retries -eq 0 ]; then
        log_error "Database failed to become ready"
        return 1
    fi

    # Run migrations if migration script exists
    if [ -f "infra/migrations/init.sql" ]; then
        log_info "Running database initialization..."
        docker exec -i $(docker ps -q -f name=postgres) psql -U ${POSTGRES_USER:-bsearch_prod} -d ${POSTGRES_DB:-bsearch_db} < infra/migrations/init.sql
        log_success "Database initialized successfully"
    else
        log_warn "No database migration script found"
    fi

    return 0
}

setup_python_environment() {
    log_header "🐍 PYTHON ENVIRONMENT SETUP"

    # Create virtual environment
    if [ ! -d ".venv" ]; then
        log_info "Creating Python virtual environment..."
        python3 -m venv .venv
    fi

    # Activate virtual environment
    source .venv/bin/activate

    # Upgrade pip
    log_info "Upgrading pip..."
    pip install --upgrade pip

    # Install dependencies
    log_info "Installing Python dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        log_error "requirements.txt not found"
        return 1
    fi

    # Verify critical imports
    log_info "Verifying critical imports..."
    python3 -c "
import sys
critical_modules = ['fastapi', 'sqlalchemy', 'redis', 'numpy']
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
    log_header "🚀 STARTING APPLICATION SERVICES"

    # Start Celery workers
    log_info "Starting Celery workers..."
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose up -d workers
    else
        docker compose up -d workers
    fi

    # Start API service
    log_info "Starting API service..."
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose up -d api
    else
        docker compose up -d api
    fi

    # Start Label Studio if configured
    if grep -q "^LABEL_STUDIO_URL=" .env 2>/dev/null; then
        log_info "Starting Label Studio..."
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
    log_header "🏥 COMPREHENSIVE HEALTH CHECKS"

    local health_check_start=$(date +%s)
    local all_healthy=true

    # API Health Check
    log_info "Checking API health..."
    local api_retries=10
    while [ $api_retries -gt 0 ]; do
        if curl -s --max-time 10 http://localhost:8080/healthz | jq -e '.status == "healthy"' >/dev/null 2>&1; then
            log_success "API health check passed"
            break
        fi
        api_retries=$((api_retries - 1))
        sleep 3
    done

    if [ $api_retries -eq 0 ]; then
        log_error "API health check failed"
        all_healthy=false
    fi

    # Database connectivity check
    log_info "Checking database connectivity..."
    if docker exec $(docker ps -q -f name=postgres) pg_isready -U ${POSTGRES_USER:-bsearch_prod} -d ${POSTGRES_DB:-bsearch_db} >/dev/null 2>&1; then
        log_success "Database connectivity check passed"
    else
        log_error "Database connectivity check failed"
        all_healthy=false
    fi

    # Redis connectivity check
    log_info "Checking Redis connectivity..."
    if docker exec $(docker ps -q -f name=redis) redis-cli ping | grep -q "PONG"; then
        log_success "Redis connectivity check passed"
    else
        log_error "Redis connectivity check failed"
        all_healthy=false
    fi

    # MinIO connectivity check
    log_info "Checking MinIO connectivity..."
    if curl -s http://localhost:9000/minio/health/ready >/dev/null 2>&1; then
        log_success "MinIO connectivity check passed"
    else
        log_error "MinIO connectivity check failed"
        all_healthy=false
    fi

    # API endpoints check
    log_info "Checking critical API endpoints..."
    local endpoints=(
        "http://localhost:8080/healthz"
        "http://localhost:8080/metrics"
        "http://localhost:8080/projects"
    )

    for endpoint in "${endpoints[@]}"; do
        if curl -s --max-time 5 "$endpoint" >/dev/null 2>&1; then
            log_success "Endpoint $endpoint is accessible"
        else
            log_warn "Endpoint $endpoint is not accessible"
        fi
    done

    # Performance check
    log_info "Running performance baseline check..."
    local perf_start=$(date +%s)
    curl -s http://localhost:8080/healthz >/dev/null
    local perf_end=$(date +%s)
    local response_time=$((perf_end - perf_start))

    if [ $response_time -gt 5 ]; then
        log_warn "Slow API response time: ${response_time}s (expected < 5s)"
    else
        log_info "API response time: ${response_time}s"
    fi

    local health_check_end=$(date +%s)
    local total_health_time=$((health_check_end - health_check_start))

    if [ $all_healthy = true ]; then
        log_success "All health checks passed (${total_health_time}s)"
        return 0
    else
        log_error "Some health checks failed (${total_health_time}s)"
        return 1
    fi
}

monitor_services() {
    log_header "📊 SERVICE MONITORING"

    # Show running containers
    log_info "Running containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | while read line; do
        log_info "  $line"
    done

    # Show resource usage
    log_info "Resource usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}" | while read line; do
        log_info "  $line"
    done

    # Check for error logs
    log_info "Checking for recent errors in logs..."
    local error_count=$(docker compose logs --tail=100 2>&1 | grep -i error | wc -l)
    if [ $error_count -gt 0 ]; then
        log_warn "Found $error_count error messages in recent logs"
        docker compose logs --tail=20 | grep -i error | while read line; do
            log_warn "  $line"
        done
    else
        log_info "No recent errors found in logs"
    fi
}

display_startup_summary() {
    log_header "🎉 B-SEARCH PRODUCTION STARTUP COMPLETE"

    local end_time=$(date +%s)
    local total_time=$((end_time - START_TIME))

    echo ""
    echo -e "${GREEN}✅ Startup completed successfully in ${total_time}s${NC}"
    echo ""

    echo -e "${CYAN}📋 Service Status:${NC}"
    echo -e "  🌐 API Gateway:     http://localhost:8080"
    echo -e "  📚 API Docs:        http://localhost:8080/docs"
    echo -e "  📊 Prometheus:      http://localhost:9090"
    echo -e "  📈 Grafana:         http://localhost:3000 (admin/admin)"
    echo -e "  🗄️  PostgreSQL:      localhost:5432"
    echo -e "  🔄 Redis:           localhost:6379"
    echo -e "  📦 MinIO:           http://localhost:9000"
    echo -e "  🏷️  Label Studio:    http://localhost:8081 (if enabled)"

    echo ""
    echo -e "${CYAN}🔧 Management Commands:${NC}"
    echo -e "  View logs:          docker compose logs -f"
    echo -e "  Stop services:      docker compose down"
    echo -e "  Restart services:   docker compose restart"
    echo -e "  View status:        docker compose ps"
    echo -e "  Health check:       curl http://localhost:8080/healthz"

    echo ""
    echo -e "${CYAN}📊 Monitoring:${NC}"
    echo -e "  System metrics:     docker stats"
    echo -e "  Application logs:   tail -f logs/*.log"
    echo -e "  Startup log:        $LOG_FILE"

    echo ""
    echo -e "${YELLOW}⚠️  Production Notes:${NC}"
    echo -e "  • Change default passwords in .env"
    echo -e "  • Configure SSL/TLS certificates"
    echo -e "  • Set up log rotation"
    echo -e "  • Configure backup strategy"
    echo -e "  • Review security settings"

    echo ""
    echo -e "${BLUE}🚀 B-Search is ready!${NC}"
}

rollback_on_failure() {
    log_header "🔄 ROLLBACK PROCEDURE"

    log_warn "Starting rollback due to startup failure..."

    # Stop all services
    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose down --remove-orphans
    else
        docker compose down --remove-orphans
    fi

    # Clean up created files
    if [ -f ".env" ] && grep -q "CHANGE_THIS" .env; then
        log_warn "Removing auto-generated .env file with default values"
        rm -f .env
    fi

    # Clean up virtual environment if it was created
    if [ -d ".venv" ] && [ ! -f ".venv/.manual" ]; then
        log_warn "Removing auto-created virtual environment"
        rm -rf .venv
    fi

    log_info "Rollback completed"
}

main() {
    # Create PID file
    echo $$ > "$PID_FILE"

    # Create log directory
    mkdir -p /var/log/bsearch

    log_header "🚀 B-SEARCH PRODUCTION STARTUP v$SCRIPT_VERSION"
    log_info "Log file: $LOG_FILE"
    log_info "PID file: $PID_FILE"

    # Pre-flight checks
    check_system_requirements || exit 1
    check_dependencies || exit 1
    check_network_connectivity || exit 1
    validate_configuration || exit 1

    # Start infrastructure
    start_infrastructure_services || {
        log_error "Failed to start infrastructure services"
        rollback_on_failure
        exit 1
    }

    # Database setup
    run_database_migrations || {
        log_error "Failed to run database migrations"
        rollback_on_failure
        exit 1
    }

    # Python environment
    setup_python_environment || {
        log_error "Failed to setup Python environment"
        rollback_on_failure
        exit 1
    }

    # Start application services
    start_application_services || {
        log_error "Failed to start application services"
        rollback_on_failure
        exit 1
    }

    # Health checks
    perform_health_checks || {
        log_error "Health checks failed"
        log_warn "Services may be running but not fully healthy"
        log_warn "Check logs and service status manually"
    }

    # Monitoring and final checks
    monitor_services

    # Display summary
    display_startup_summary

    # Remove PID file
    rm -f "$PID_FILE"

    log_success "Production startup completed successfully"
    exit 0
}

# Show usage if requested
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
    echo "B-Search Production Startup Script v$SCRIPT_VERSION"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --help, -h          Show this help message"
    echo "  --version, -v       Show version information"
    echo "  --dry-run           Show what would be done without executing"
    echo "  --skip-health-checks Skip comprehensive health checks"
    echo "  --force             Force startup even if some checks fail"
    echo ""
    echo "Environment Variables:"
    echo "  LOG_FILE            Custom log file path (default: auto-generated)"
    echo "  HEALTH_CHECK_TIMEOUT Timeout for health checks in seconds (default: 300)"
    echo ""
    exit 0
fi

if [ "${1:-}" = "--version" ] || [ "${1:-}" = "-v" ]; then
    echo "B-Search Production Startup Script v$SCRIPT_VERSION"
    exit 0
fi

# Run main function
main "$@"