#!/bin/bash
set -euo pipefail

# B-Search Development Monitoring Script
# Lightweight monitoring for development environment
# Version: 1.0.0
# Author: B-Search DevOps Team

# Configuration
SCRIPT_VERSION="1.0.0"
MONITOR_INTERVAL=${MONITOR_INTERVAL:-30}
LOG_FILE="/tmp/bsearch-dev-monitor-$(date +%Y%m%d).log"
PID_FILE="/tmp/bsearch-dev-monitor.pid"

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

log_dev() {
    log "DEV" "$1"
    echo -e "${CYAN}[DEV]${NC} $1"
}

log_success() {
    log "SUCCESS" "$1"
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Development-specific monitoring functions
check_dev_services() {
    log_info "Checking development services..."

    # Check Docker services
    local services=("postgres" "redis" "minio" "api" "workers")
    local running_services=()
    local failed_services=()

    for service in "${services[@]}"; do
        if docker ps --filter "name=$service" --filter "status=running" --format "{{.Names}}" | grep -q "^$service"; then
            running_services+=("$service")
        else
            failed_services+=("$service")
        fi
    done

    if [ ${#running_services[@]} -gt 0 ]; then
        log_success "Running services: ${running_services[*]}"
    fi

    if [ ${#failed_services[@]} -gt 0 ]; then
        log_warn "Stopped services: ${failed_services[*]}"
        log_dev "Try: docker compose up -d ${failed_services[*]}"
    fi

    return 0
}

check_api_dev() {
    local api_url="${API_URL:-http://localhost:8080}"

    # Quick connectivity check
    if curl -s --max-time 2 "${api_url}/healthz" >/dev/null 2>&1; then
        log_success "API is responding"

        # Check if API docs are accessible
        if curl -s --max-time 2 "${api_url}/docs" >/dev/null 2>&1; then
            log_dev "API documentation is accessible at ${api_url}/docs"
        fi

        return 0
    else
        log_warn "API is not responding at ${api_url}"
        log_dev "Check API logs: docker compose logs -f api"
        return 1
    fi
}

check_database_dev() {
    local db_container=$(docker ps -q -f name=postgres 2>/dev/null)

    if [ -z "$db_container" ]; then
        log_warn "PostgreSQL container not found"
        return 1
    fi

    # Quick connectivity check
    if docker exec "$db_container" pg_isready -U ${POSTGRES_USER:-dev_user} -d ${POSTGRES_DB:-bsearch_dev_db} >/dev/null 2>&1; then
        log_success "Database is accessible"
        return 0
    else
        log_warn "Database is not accessible"
        log_dev "Check database logs: docker compose logs postgres"
        return 1
    fi
}

check_redis_dev() {
    local redis_container=$(docker ps -q -f name=redis 2>/dev/null)

    if [ -z "$redis_container" ]; then
        log_warn "Redis container not found"
        return 1
    fi

    # Quick connectivity check
    if docker exec "$redis_container" redis-cli ping 2>/dev/null | grep -q "PONG"; then
        log_success "Redis is responding"
        return 0
    else
        log_warn "Redis is not responding"
        log_dev "Check Redis logs: docker compose logs redis"
        return 1
    fi
}

check_minio_dev() {
    local minio_url="${MINIO_URL:-http://localhost:9000}"

    # Quick connectivity check
    if curl -s --max-time 2 "${minio_url}/minio/health/ready" >/dev/null 2>&1; then
        log_success "MinIO is accessible"
        return 0
    else
        log_warn "MinIO is not accessible"
        log_dev "MinIO console: ${minio_url} (minioadmin/minioadmin)"
        return 1
    fi
}

check_resource_usage() {
    log_info "Checking resource usage..."

    # Docker resource usage
    if docker ps --format "table {{.Names}}\t{{.CPUPerc}}\t{{.MemUsage}}" | grep -v "NAMES" >/dev/null 2>&1; then
        echo ""
        echo -e "${CYAN}Docker Resource Usage:${NC}"
        docker ps --format "table {{.Names}}\t{{.CPUPerc}}\t{{.MemUsage}}"
    fi

    # System resource usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    local mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')

    echo ""
    echo -e "${CYAN}System Resources:${NC}"
    echo -e "  CPU Usage: ${cpu_usage}%"
    echo -e "  Memory Usage: ${mem_usage}%"

    # Warn if resources are high
    if (( $(echo "$cpu_usage > 80" | bc -l) )); then
        log_warn "High CPU usage: ${cpu_usage}%"
    fi

    if [ $mem_usage -gt 80 ]; then
        log_warn "High memory usage: ${mem_usage}%"
    fi
}

check_logs() {
    log_info "Checking recent logs..."

    # Check for recent errors in API logs
    local api_errors=$(docker compose logs --tail=20 api 2>&1 | grep -i error | wc -l 2>/dev/null || echo "0")
    if [ "$api_errors" -gt 0 ]; then
        log_warn "Found $api_errors error(s) in recent API logs"
        log_dev "View API logs: docker compose logs -f api"
    fi

    # Check for recent errors in worker logs
    local worker_errors=$(docker compose logs --tail=20 workers 2>&1 | grep -i error | wc -l 2>/dev/null || echo "0")
    if [ "$worker_errors" -gt 0 ]; then
        log_warn "Found $worker_errors error(s) in recent worker logs"
        log_dev "View worker logs: docker compose logs -f workers"
    fi
}

show_dev_status() {
    echo ""
    echo -e "${BLUE}=== B-SEARCH DEVELOPMENT STATUS ===${NC}"
    echo ""

    # Show service status
    echo -e "${CYAN}Service Status:${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "No services running"

    echo ""
    echo -e "${CYAN}Quick Actions:${NC}"
    echo -e "  🌐 API:           http://localhost:8080"
    echo -e "  📚 API Docs:      http://localhost:8080/docs"
    echo -e "  📦 MinIO:         http://localhost:9000 (minioadmin/minioadmin)"
    echo -e "  🔄 Redis:         localhost:6379"
    echo -e "  🗄️  PostgreSQL:    localhost:5432 (dev_user/dev_password)"

    echo ""
    echo -e "${CYAN}Useful Commands:${NC}"
    echo -e "  View all logs:    docker compose logs -f"
    echo -e "  Restart API:      docker compose restart api"
    echo -e "  Stop all:         docker compose down"
    echo -e "  Clean restart:    docker compose down && docker compose up -d"
    echo -e "  Check health:     curl http://localhost:8080/healthz"

    echo ""
    echo -e "${CYAN}Development Tips:${NC}"
    echo -e "  • API auto-reloads on code changes"
    echo -e "  • Check $LOG_FILE for detailed logs"
    echo -e "  • Use 'docker compose logs -f api' to watch API logs"
    echo -e "  • Visit /docs for interactive API documentation"
}

generate_dev_report() {
    local report_file="/tmp/bsearch-dev-report-$(date +%Y%m%d-%H%M%S).txt"

    {
        echo "B-Search Development Report"
        echo "Generated: $(date)"
        echo "Host: $(hostname)"
        echo "Uptime: $(uptime -p)"
        echo ""
        echo "=== DOCKER SERVICES ==="
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo ""
        echo "=== SYSTEM RESOURCES ==="
        echo "CPU Usage: $(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')%"
        echo "Memory Usage: $(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')%"
        echo ""
        echo "=== RECENT LOGS ==="
        echo "API Errors (last 10 lines):"
        docker compose logs --tail=10 api 2>&1 | grep -i error || echo "No recent errors"
        echo ""
        echo "Worker Errors (last 10 lines):"
        docker compose logs --tail=10 workers 2>&1 | grep -i error || echo "No recent errors"
    } > "$report_file"

    log_info "Development report generated: $report_file"
    echo -e "${CYAN}Report saved to: $report_file${NC}"
}

# Main monitoring loop
main() {
    # Create PID file
    echo $$ > "$PID_FILE"

    log_info "Starting B-Search Development Monitor v$SCRIPT_VERSION"
    log_info "Monitor interval: ${MONITOR_INTERVAL}s"
    log_info "Log file: $LOG_FILE"

    # Trap signals for graceful shutdown
    trap 'log_info "Received shutdown signal"; rm -f "$PID_FILE"; exit 0' INT TERM

    local iteration=0

    while true; do
        iteration=$((iteration + 1))
        log_info "=== Development Check #$iteration ==="

        # Run development checks
        check_dev_services
        check_api_dev || true
        check_database_dev || true
        check_redis_dev || true
        check_minio_dev || true
        check_resource_usage
        check_logs

        # Show status every 10 iterations
        if [ $((iteration % 10)) -eq 0 ]; then
            show_dev_status
        fi

        # Generate report every 30 iterations (15 minutes at 30s interval)
        if [ $((iteration % 30)) -eq 0 ]; then
            generate_dev_report
        fi

        log_info "Development check #$iteration completed"
        sleep "$MONITOR_INTERVAL"
    done
}

# Command line options
case "${1:-}" in
    --help|-h)
        echo "B-Search Development Monitoring Script v$SCRIPT_VERSION"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h          Show this help message"
        echo "  --version, -v       Show version information"
        echo "  --once              Run checks once and exit"
        echo "  --status            Show current development status"
        echo "  --report            Generate and show development report"
        echo "  --logs              Show recent logs from all services"
        echo "  --resources         Show detailed resource usage"
        echo ""
        echo "Environment Variables:"
        echo "  MONITOR_INTERVAL    Monitoring interval in seconds (default: 30)"
        echo "  API_URL            API base URL (default: http://localhost:8080)"
        echo "  MINIO_URL          MinIO base URL (default: http://localhost:9000)"
        echo ""
        exit 0
        ;;
    --version|-v)
        echo "B-Search Development Monitoring Script v$SCRIPT_VERSION"
        exit 0
        ;;
    --once)
        log_info "Running one-time development checks..."
        check_dev_services
        check_api_dev || true
        check_database_dev || true
        check_redis_dev || true
        check_minio_dev || true
        check_resource_usage
        check_logs
        show_dev_status
        log_success "One-time checks completed"
        exit 0
        ;;
    --status)
        show_dev_status
        exit 0
        ;;
    --report)
        generate_dev_report
        exit 0
        ;;
    --logs)
        echo -e "${CYAN}Recent logs from all services:${NC}"
        docker compose logs --tail=20
        exit 0
        ;;
    --resources)
        echo -e "${CYAN}Detailed resource usage:${NC}"
        check_resource_usage
        echo ""
        echo -e "${CYAN}Docker container details:${NC}"
        docker stats --no-stream
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac