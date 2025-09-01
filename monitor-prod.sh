#!/bin/bash
set -euo pipefail

# B-Search Production Monitoring Script
# Comprehensive health monitoring and alerting for production deployments
# Version: 1.0.0
# Author: B-Search DevOps Team

# Configuration
SCRIPT_VERSION="1.0.0"
MONITOR_INTERVAL=${MONITOR_INTERVAL:-60}
ALERT_THRESHOLD=${ALERT_THRESHOLD:-3}
LOG_FILE="/var/log/bsearch/monitor-$(date +%Y%m%d).log"
ALERT_LOG="/var/log/bsearch/alerts-$(date +%Y%m%d).log"
PID_FILE="/var/run/bsearch/monitor.pid"

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Global variables for tracking
declare -A service_status
declare -A alert_counts
declare -A last_alert_time

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

log_alert() {
    local message="$1"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [ALERT] $message" | tee -a "$ALERT_LOG"
    echo -e "${RED}[ALERT]${NC} $message" >&2
}

# Alert management
send_alert() {
    local alert_type="$1"
    local message="$2"
    local severity="${3:-warning}"

    # Rate limiting - don't send alerts too frequently
    local current_time=$(date +%s)
    local last_time=${last_alert_time[$alert_type]:-0}
    local time_diff=$((current_time - last_time))

    if [ $time_diff -lt 300 ]; then  # 5 minutes cooldown
        log_info "Alert rate limited for $alert_type (last alert ${time_diff}s ago)"
        return
    fi

    last_alert_time[$alert_type]=$current_time
    alert_counts[$alert_type]=$((alert_counts[$alert_type] + 1))

    log_alert "[$severity] $alert_type: $message"

    # Send external alerts if configured
    send_external_alert "$alert_type" "$message" "$severity"
}

send_external_alert() {
    local alert_type="$1"
    local message="$2"
    local severity="$3"

    # Email alerts
    if [ "${ALERT_EMAIL_ENABLED:-false}" = "true" ]; then
        send_email_alert "$alert_type" "$message" "$severity"
    fi

    # Slack alerts
    if [ "${ALERT_SLACK_ENABLED:-false}" = "true" ]; then
        send_slack_alert "$alert_type" "$message" "$severity"
    fi

    # Webhook alerts
    if [ "${ALERT_WEBHOOK_ENABLED:-false}" = "true" ]; then
        send_webhook_alert "$alert_type" "$message" "$severity"
    fi
}

send_email_alert() {
    local alert_type="$1"
    local message="$2"
    local severity="$3"

    if command -v mail >/dev/null 2>&1; then
        echo "B-Search Alert [$severity]
Type: $alert_type
Message: $message
Time: $(date)
Host: $(hostname)" | mail -s "B-Search Alert: $alert_type" ${ALERT_EMAIL_RECIPIENTS:-admin@localhost}
    fi
}

send_slack_alert() {
    local alert_type="$1"
    local message="$2"
    local severity="$3"

    local color="warning"
    [ "$severity" = "error" ] && color="danger"
    [ "$severity" = "info" ] && color="good"

    local payload=$(cat <<EOF
{
    "attachments": [
        {
            "color": "$color",
            "title": "B-Search Alert: $alert_type",
            "text": "$message",
            "fields": [
                {
                    "title": "Severity",
                    "value": "$severity",
                    "short": true
                },
                {
                    "title": "Host",
                    "value": "$(hostname)",
                    "short": true
                },
                {
                    "title": "Time",
                    "value": "$(date)",
                    "short": false
                }
            ]
        }
    ]
}
EOF
)

    curl -s -X POST -H 'Content-type: application/json' --data "$payload" "${ALERT_SLACK_WEBHOOK_URL}" >/dev/null 2>&1 || true
}

send_webhook_alert() {
    local alert_type="$1"
    local message="$2"
    local severity="$3"

    local payload=$(cat <<EOF
{
    "alert_type": "$alert_type",
    "message": "$message",
    "severity": "$severity",
    "timestamp": "$(date -Iseconds)",
    "host": "$(hostname)",
    "service": "b-search-monitor"
}
EOF
)

    curl -s -X POST -H 'Content-type: application/json' --data "$payload" "${ALERT_WEBHOOK_URL}" >/dev/null 2>&1 || true
}

# Health check functions
check_service_health() {
    local service_name="$1"
    local check_command="$2"
    local expected_output="${3:-}"

    local status="unknown"
    local output=""

    if eval "$check_command" >/dev/null 2>&1; then
        if [ -z "$expected_output" ] || eval "$check_command" | grep -q "$expected_output"; then
            status="healthy"
        else
            status="unhealthy"
        fi
    else
        status="unhealthy"
    fi

    # Track status changes
    local previous_status=${service_status[$service_name]:-unknown}

    if [ "$status" != "$previous_status" ]; then
        if [ "$status" = "healthy" ]; then
            log_success "$service_name is now healthy"
        else
            log_error "$service_name is now unhealthy"
            send_alert "service_down" "$service_name service is down or unresponsive" "error"
        fi
    fi

    service_status[$service_name]=$status
    echo "$status"
}

check_docker_services() {
    log_info "Checking Docker services..."

    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        send_alert "docker_down" "Docker daemon is not running" "error"
        return 1
    fi

    # Check core services
    local services=("postgres" "redis" "minio" "api" "workers")
    local failed_services=()

    for service in "${services[@]}"; do
        if ! docker ps --filter "name=$service" --filter "status=running" | grep -q "$service"; then
            failed_services+=("$service")
        fi
    done

    if [ ${#failed_services[@]} -gt 0 ]; then
        send_alert "services_down" "Services not running: ${failed_services[*]}" "error"
        return 1
    fi

    log_success "All Docker services are running"
    return 0
}

check_api_health() {
    local api_url="${API_URL:-http://localhost:8080}"

    # Basic connectivity check
    if ! curl -s --max-time 5 "${api_url}/healthz" >/dev/null; then
        send_alert "api_unreachable" "API is not reachable at ${api_url}" "error"
        return 1
    fi

    # Detailed health check
    local health_response=$(curl -s --max-time 10 "${api_url}/healthz" 2>/dev/null)
    if echo "$health_response" | jq -e '.status == "healthy"' >/dev/null 2>&1; then
        log_success "API health check passed"
        return 0
    else
        send_alert "api_unhealthy" "API health check failed: $health_response" "warning"
        return 1
    fi
}

check_database_health() {
    local db_container=$(docker ps -q -f name=postgres)

    if [ -z "$db_container" ]; then
        send_alert "database_down" "PostgreSQL container not found" "error"
        return 1
    fi

    # Check if PostgreSQL is accepting connections
    if docker exec "$db_container" pg_isready -U ${POSTGRES_USER:-bsearch_prod} -d ${POSTGRES_DB:-bsearch_db} >/dev/null 2>&1; then
        log_success "Database health check passed"
        return 0
    else
        send_alert "database_unhealthy" "PostgreSQL is not accepting connections" "error"
        return 1
    fi
}

check_redis_health() {
    local redis_container=$(docker ps -q -f name=redis)

    if [ -z "$redis_container" ]; then
        send_alert "redis_down" "Redis container not found" "error"
        return 1
    fi

    # Check Redis connectivity
    if docker exec "$redis_container" redis-cli ping | grep -q "PONG"; then
        log_success "Redis health check passed"
        return 0
    else
        send_alert "redis_unhealthy" "Redis is not responding to ping" "error"
        return 1
    fi
}

check_minio_health() {
    local minio_url="${MINIO_URL:-http://localhost:9000}"

    # Check MinIO health endpoint
    if curl -s "${minio_url}/minio/health/ready" >/dev/null 2>&1; then
        log_success "MinIO health check passed"
        return 0
    else
        send_alert "minio_unhealthy" "MinIO is not responding to health checks" "warning"
        return 1
    fi
}

check_system_resources() {
    log_info "Checking system resources..."

    # CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    if (( $(echo "$cpu_usage > 90" | bc -l) )); then
        send_alert "high_cpu" "CPU usage is ${cpu_usage}%" "warning"
    fi

    # Memory usage
    local mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [ $mem_usage -gt 90 ]; then
        send_alert "high_memory" "Memory usage is ${mem_usage}%" "warning"
    fi

    # Disk usage
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $disk_usage -gt 90 ]; then
        send_alert "low_disk_space" "Disk usage is ${disk_usage}%" "warning"
    fi

    log_info "CPU: ${cpu_usage}%, Memory: ${mem_usage}%, Disk: ${disk_usage}%"
}

check_application_metrics() {
    local api_url="${API_URL:-http://localhost:8080}"

    # Check API response time
    local start_time=$(date +%s%N)
    if curl -s --max-time 5 "${api_url}/healthz" >/dev/null; then
        local end_time=$(date +%s%N)
        local response_time=$(( (end_time - start_time) / 1000000 ))  # Convert to milliseconds

        if [ $response_time -gt 5000 ]; then  # 5 seconds
            send_alert "slow_api" "API response time is ${response_time}ms" "warning"
        fi

        log_info "API response time: ${response_time}ms"
    fi

    # Check error rates from logs (if accessible)
    check_error_rates
}

check_error_rates() {
    # Check recent error logs
    local error_count=0

    # Check Docker container logs for errors
    if command -v docker >/dev/null 2>&1; then
        error_count=$(docker compose logs --tail=100 2>&1 | grep -i error | wc -l)
    fi

    # Check application logs if accessible
    if [ -d "logs" ]; then
        local app_errors=$(find logs -name "*.log" -mtime -1 -exec grep -i error {} \; | wc -l)
        error_count=$((error_count + app_errors))
    fi

    if [ $error_count -gt 10 ]; then
        send_alert "high_error_rate" "High error rate detected: $error_count errors in recent logs" "warning"
    fi

    log_info "Error count in recent logs: $error_count"
}

check_network_connectivity() {
    # Check internet connectivity
    if ! curl -s --connect-timeout 5 https://www.google.com >/dev/null; then
        send_alert "network_down" "Internet connectivity lost" "error"
        return 1
    fi

    # Check DNS resolution
    if ! nslookup google.com >/dev/null 2>&1; then
        send_alert "dns_issue" "DNS resolution problems detected" "warning"
    fi

    log_info "Network connectivity: OK"
    return 0
}

generate_report() {
    log_info "Generating monitoring report..."

    local report_file="/var/log/bsearch/report-$(date +%Y%m%d-%H%M%S).txt"

    cat > "$report_file" << EOF
B-Search Production Monitoring Report
Generated: $(date)
Host: $(hostname)
Uptime: $(uptime -p)

=== SERVICE STATUS ===
$(for service in "${!service_status[@]}"; do
    echo "$service: ${service_status[$service]}"
done)

=== ALERT SUMMARY ===
$(for alert_type in "${!alert_counts[@]}"; do
    echo "$alert_type: ${alert_counts[$alert_type]} alerts"
done)

=== SYSTEM RESOURCES ===
$(top -bn1 | head -10)

=== DOCKER CONTAINERS ===
$(docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}")

=== NETWORK STATUS ===
$(ip addr show | grep "inet " | grep -v "127.0.0.1")

=== DISK USAGE ===
$(df -h)

=== MEMORY USAGE ===
$(free -h)

=== PROCESS SUMMARY ===
$(ps aux --sort=-%cpu | head -10)
EOF

    log_info "Report generated: $report_file"
}

cleanup_old_logs() {
    # Clean up old log files (keep last 7 days)
    find /var/log/bsearch -name "*.log" -mtime +7 -delete 2>/dev/null || true
    find /var/log/bsearch -name "*.txt" -mtime +7 -delete 2>/dev/null || true
}

# Main monitoring loop
main() {
    # Create PID file
    echo $$ > "$PID_FILE"

    # Create log directories
    mkdir -p /var/log/bsearch

    log_info "Starting B-Search Production Monitor v$SCRIPT_VERSION"
    log_info "Monitor interval: ${MONITOR_INTERVAL}s"
    log_info "Alert threshold: ${ALERT_THRESHOLD}"
    log_info "Log file: $LOG_FILE"
    log_info "Alert log: $ALERT_LOG"

    # Trap signals for graceful shutdown
    trap 'log_info "Received shutdown signal"; rm -f "$PID_FILE"; exit 0' INT TERM

    local iteration=0

    while true; do
        iteration=$((iteration + 1))
        log_info "Starting monitoring iteration #$iteration"

        # Run all health checks
        check_docker_services || true
        check_api_health || true
        check_database_health || true
        check_redis_health || true
        check_minio_health || true
        check_system_resources || true
        check_application_metrics || true
        check_network_connectivity || true

        # Generate periodic reports
        if [ $((iteration % 60)) -eq 0 ]; then  # Every hour (assuming 60s interval)
            generate_report
        fi

        # Clean up old logs weekly
        if [ $((iteration % 60480)) -eq 0 ]; then  # Every week (assuming 60s interval)
            cleanup_old_logs
        fi

        log_info "Monitoring iteration #$iteration completed"
        sleep "$MONITOR_INTERVAL"
    done
}

# Command line options
case "${1:-}" in
    --help|-h)
        echo "B-Search Production Monitoring Script v$SCRIPT_VERSION"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h              Show this help message"
        echo "  --version, -v           Show version information"
        echo "  --once                  Run checks once and exit"
        echo "  --report                Generate and display current report"
        echo "  --alert-test            Send test alert"
        echo ""
        echo "Environment Variables:"
        echo "  MONITOR_INTERVAL        Monitoring interval in seconds (default: 60)"
        echo "  ALERT_THRESHOLD         Alert threshold for rate limiting (default: 3)"
        echo "  API_URL                 API base URL (default: http://localhost:8080)"
        echo "  ALERT_EMAIL_ENABLED     Enable email alerts (default: false)"
        echo "  ALERT_SLACK_ENABLED     Enable Slack alerts (default: false)"
        echo "  ALERT_WEBHOOK_ENABLED   Enable webhook alerts (default: false)"
        echo ""
        exit 0
        ;;
    --version|-v)
        echo "B-Search Production Monitoring Script v$SCRIPT_VERSION"
        exit 0
        ;;
    --once)
        log_info "Running one-time health checks..."
        check_docker_services
        check_api_health
        check_database_health
        check_redis_health
        check_minio_health
        check_system_resources
        check_application_metrics
        check_network_connectivity
        generate_report
        log_success "One-time checks completed"
        exit 0
        ;;
    --report)
        generate_report
        echo "Report generated. Check /var/log/bsearch/ for the latest report."
        exit 0
        ;;
    --alert-test)
        send_alert "test_alert" "This is a test alert from the monitoring system" "info"
        log_success "Test alert sent"
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac