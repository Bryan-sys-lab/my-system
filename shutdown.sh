#!/bin/bash
set -e

# B-Search System Shutdown Script
# This script stops all services and kills all bsearch-related processes

echo "🛑 Stopping B-Search System..."
echo "=============================="

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

# Stop systemd services if they exist
stop_systemd_services() {
    print_status "Stopping systemd services..."

    # Stop bsearch service
    if systemctl is-active --quiet bsearch; then
        sudo systemctl stop bsearch
        print_status "Stopped bsearch service"
    else
        print_warning "bsearch service is not running"
    fi

    # Stop bsearch-monitor service
    if systemctl is-active --quiet bsearch-monitor; then
        sudo systemctl stop bsearch-monitor
        print_status "Stopped bsearch-monitor service"
    else
        print_warning "bsearch-monitor service is not running"
    fi
}

# Stop Docker services
stop_docker_services() {
    print_status "Stopping Docker services..."

    if command -v docker-compose >/dev/null 2>&1; then
        docker-compose down
        print_status "Docker services stopped via docker-compose"
    elif docker compose version >/dev/null 2>&1; then
        docker compose down
        print_status "Docker services stopped via docker compose"
    else
        print_warning "Docker Compose not found, skipping Docker services"
    fi
}

# Kill remaining processes
kill_processes() {
    print_status "Killing remaining bsearch processes..."

    # Kill uvicorn processes
    if pgrep -f "uvicorn apps.api.main" >/dev/null 2>&1; then
        pkill -f "uvicorn apps.api.main"
        print_status "Killed uvicorn processes"
    else
        print_warning "No uvicorn processes found"
    fi

    # Kill any other bsearch-related processes
    if pgrep -f "bsearch" >/dev/null 2>&1; then
        pkill -f "bsearch"
        print_status "Killed bsearch processes"
    else
        print_warning "No bsearch processes found"
    fi

    # Kill Python processes related to the app
    if pgrep -f "apps.api.main" >/dev/null 2>&1; then
        pkill -f "apps.api.main"
        print_status "Killed API processes"
    fi

    # Kill worker processes if any
    if pgrep -f "apps.workers" >/dev/null 2>&1; then
        pkill -f "apps.workers"
        print_status "Killed worker processes"
    fi
}

# Clean up temporary files/logs if needed
cleanup() {
    print_status "Performing cleanup..."

    # Remove any temporary files if necessary
    # Add cleanup commands here if needed

    print_status "Cleanup completed"
}

# Main execution
main() {
    stop_systemd_services

    echo ""
    stop_docker_services

    echo ""
    kill_processes

    echo ""
    cleanup

    echo ""
    echo -e "${BLUE}✅ B-Search System Stopped Successfully!${NC}"
    echo "=========================================="
}

# Run main function
main "$@"