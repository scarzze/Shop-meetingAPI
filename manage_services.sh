#!/bin/bash

# Color settings
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

# Service definitions with correct directory mappings
declare -A SERVICES=(
    ["auth"]="5002"
    ["cart"]="5001"
    ["profile"]="5003"
    ["Orderservice"]="5005"
    ["Customer_support_back-end"]="5004"
    ["product"]="5006"
)

# Function to check if a port is in use
check_port() {
    lsof -i:$1 >/dev/null 2>&1
}

# Function to kill process on a port
kill_port() {
    echo -e "${YELLOW}Killing process on port $1${RESET}"
    fuser -k $1/tcp >/dev/null 2>&1
}

# Function to check service health
check_health() {
    local service=$1
    local port=$2
    local max_retries=5
    local retry=0
    
    while [ $retry -lt $max_retries ]; do
        if curl -s "http://localhost:$port/health" >/dev/null; then
            echo -e "${GREEN}✓ $service service is healthy${RESET}"
            return 0
        fi
        retry=$((retry + 1))
        sleep 2
    done
    
    echo -e "${RED}✗ $service service health check failed${RESET}"
    return 1
}

# Kill all service ports
kill_all() {
    echo -e "${YELLOW}Stopping all services...${RESET}"
    for port in ${SERVICES[@]}; do
        if check_port $port; then
            kill_port $port
            sleep 1
        fi
    done
    echo -e "${GREEN}All services stopped${RESET}"
}

# Start all services
start_all() {
    echo -e "${YELLOW}Starting all services...${RESET}"
    cd services
    
    # Start each service
    for service in "${!SERVICES[@]}"; do
        port=${SERVICES[$service]}
        echo -e "\n${YELLOW}Starting $service service on port $port${RESET}"
        
        # Navigate to service directory
        cd $service* 2>/dev/null || {
            echo -e "${RED}Could not find directory for $service${RESET}"
            continue
        }
        
        # Start the service based on available files
        if [ -f "run.py" ]; then
            python run.py &
        elif [ -f "app.py" ]; then
            python app.py &
        else
            echo -e "${RED}No entry point found for $service${RESET}"
            cd ..
            continue
        fi
        
        # Check health
        sleep 3
        check_health $service $port
        cd ..
    done
}

# Test inter-service communication
test_communication() {
    echo -e "\n${YELLOW}Testing inter-service communication...${RESET}"
    
    # Test profile service connectivity
    echo -e "\nTesting Profile Service:"
    curl -s -X GET "http://localhost/api/profile/health" | jq .
    
    # Test auth service connectivity
    echo -e "\nTesting Auth Service:"
    curl -s -X GET "http://localhost/api/auth/health" | jq .
    
    # Test other services
    for service in "${!SERVICES[@]}"; do
        port=${SERVICES[$service]}
        echo -e "\nTesting $service service (port $port):"
        curl -s -X GET "http://localhost:$port/health" | jq .
    done
}

# Command line interface
case "$1" in
    "start")
        start_all
        ;;
    "stop")
        kill_all
        ;;
    "restart")
        kill_all
        sleep 2
        start_all
        ;;
    "test")
        test_communication
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|test}"
        exit 1
        ;;
esac