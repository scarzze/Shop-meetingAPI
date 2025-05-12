#!/bin/bash
# Comprehensive service management shell script for Shop-meetingAPI
# Based on functionality from manage_services.py

# Define color codes
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

# Project root directory
PROJECT_ROOT=$(dirname "$(readlink -f "$0")")

# Service definitions
declare -A services=(
    ["auth-service"]="5002,run.py,DATABASE_URL"
    ["profile-service"]="5003,run.py,DATABASE_URL"
    ["cart-service"]="5001,app.py,DATABASE_URI"
    ["Orderservice"]="5005,run.py,DATABASE_URL"
    ["Customer_support_back-end"]="5004,run.py,DATABASE_URI"
    ["product-service"]="5006,run.py,DATABASE_URL"
)

# Print functions for formatting
print_success() {
    echo -e "${GREEN}✓ $1${RESET}"
}

print_warning() {
    echo -e "${YELLOW}! $1${RESET}"
}

print_error() {
    echo -e "${RED}✗ $1${RESET}"
}

print_section() {
    echo -e "\n${YELLOW}=== $1 ===${RESET}"
}

# Check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Kill process on port
kill_on_port() {
    local port=$1
    if check_port $port; then
        print_warning "Killing process on port $port"
        lsof -ti :$port | xargs kill -9
        sleep 1
    fi
}

# Check service health
check_health() {
    local service_name=$1
    local port=$2
    
    echo "Checking health of $service_name on port $port..."
    
    if timeout 2 curl -s "http://localhost:$port/health" >/dev/null; then
        print_success "$service_name is running"
        return 0
    else
        print_error "$service_name is not responding"
        return 1
    fi
}

# Start a service
start_service() {
    local service_dir=$1
    local port=$(echo ${services[$service_dir]} | cut -d, -f1)
    local entry_file=$(echo ${services[$service_dir]} | cut -d, -f2)
    local debug_mode=$2
    
    print_section "Starting $service_dir on port $port"
    
    # Check if service is already running
    if check_port $port; then
        print_warning "$service_dir is already running on port $port"
        if [ "$3" == "restart" ]; then
            kill_on_port $port
        else
            return 0
        fi
    fi
    
    # Set debug mode
    if [ "$debug_mode" == "true" ]; then
        export DEBUG_MODE=true
    else
        export DEBUG_MODE=false
    fi
    
    # Check if entry file exists
    if [ ! -f "$PROJECT_ROOT/services/$service_dir/$entry_file" ]; then
        print_error "Entry file $entry_file not found for $service_dir"
        return 1
    fi
    
    # Start service in background
    cd "$PROJECT_ROOT/services/$service_dir" || return 1
    python "$entry_file" &
    
    # Give it time to start
    sleep 2
    
    # Check if it's running
    if check_port $port; then
        print_success "$service_dir started successfully on port $port"
    else
        print_error "Failed to start $service_dir on port $port"
    fi
}

# Start all services
start_all_services() {
    local debug_mode=$1
    local restart_mode=$2
    
    print_section "Starting all services"
    
    for service_dir in "${!services[@]}"; do
        start_service "$service_dir" "$debug_mode" "$restart_mode"
    done
}

# Check all services
check_all_services() {
    print_section "Checking all services"
    
    for service_dir in "${!services[@]}"; do
        local port=$(echo ${services[$service_dir]} | cut -d, -f1)
        check_health "$service_dir" "$port"
    done
}

# Main function
main() {
    if [ $# -lt 1 ]; then
        echo "Usage: $0 {start|restart|check|debug|prod} [service_name]"
        exit 1
    fi
    
    ACTION=$1
    SERVICE=${2:-"all"}
    
    case $ACTION in
        start)
            if [ "$SERVICE" == "all" ]; then
                start_all_services "false" "no"
            else
                if [[ -v "services[$SERVICE]" ]]; then
                    start_service "$SERVICE" "false" "no"
                else
                    print_error "Unknown service: $SERVICE"
                    exit 1
                fi
            fi
            ;;
        restart)
            if [ "$SERVICE" == "all" ]; then
                start_all_services "false" "restart"
            else
                if [[ -v "services[$SERVICE]" ]]; then
                    start_service "$SERVICE" "false" "restart"
                else
                    print_error "Unknown service: $SERVICE"
                    exit 1
                fi
            fi
            ;;
        check)
            if [ "$SERVICE" == "all" ]; then
                check_all_services
            else
                if [[ -v "services[$SERVICE]" ]]; then
                    local port=$(echo ${services[$SERVICE]} | cut -d, -f1)
                    check_health "$SERVICE" "$port"
                else
                    print_error "Unknown service: $SERVICE"
                    exit 1
                fi
            fi
            ;;
        debug)
            if [ "$SERVICE" == "all" ]; then
                start_all_services "true" "restart"
            else
                if [[ -v "services[$SERVICE]" ]]; then
                    start_service "$SERVICE" "true" "restart"
                else
                    print_error "Unknown service: $SERVICE"
                    exit 1
                fi
            fi
            ;;
        prod)
            if [ "$SERVICE" == "all" ]; then
                start_all_services "false" "restart"
            else
                if [[ -v "services[$SERVICE]" ]]; then
                    start_service "$SERVICE" "false" "restart"
                else
                    print_error "Unknown service: $SERVICE"
                    exit 1
                fi
            fi
            ;;
        *)
            echo "Unknown action: $ACTION"
            echo "Usage: $0 {start|restart|check|debug|prod} [service_name]"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"
