#!/bin/bash
# Script to start the remaining microservices with real database connections

echo "=== Starting remaining microservices with real database connections ==="
echo "This script will start Auth, Profile, and Cart services with DEBUG_MODE=false"

# Set terminal colors for better visibility
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

# Directory containing all services
SERVICES_DIR="$(pwd)/services"

# Update .env files to ensure DEBUG_MODE=false
update_env_file() {
    local service_dir=$1
    local env_file="${service_dir}/.env"
    
    if [ -f "$env_file" ]; then
        # Check if DEBUG_MODE exists in the file
        if grep -q "DEBUG_MODE" "$env_file"; then
            # Replace DEBUG_MODE line
            sed -i 's/DEBUG_MODE=.*/DEBUG_MODE=false/' "$env_file"
            echo -e "${GREEN}✓${RESET} Updated DEBUG_MODE in ${env_file}"
        else
            # Add DEBUG_MODE line if it doesn't exist
            echo "DEBUG_MODE=false" >> "$env_file"
            echo -e "${GREEN}✓${RESET} Added DEBUG_MODE=false to ${env_file}"
        fi
    else
        echo -e "${RED}✗${RESET} .env file does not exist: ${env_file}"
        return 1
    fi
    return 0
}

# Start a service
start_service() {
    local service_name=$1
    local service_dir=$2
    local port=$3
    
    echo -e "\n${YELLOW}Starting ${service_name} (port ${port})${RESET}"
    
    # Update .env file
    update_env_file "$service_dir"
    
    # Check if the port is already in use
    if lsof -i :$port > /dev/null; then
        echo -e "${RED}✗${RESET} Port ${port} is already in use. Stopping existing process..."
        fuser -k -n tcp $port
        sleep 2
    fi
    
    # Start the service in a new terminal window
    if [ -f "${service_dir}/run.py" ]; then
        echo -e "${GREEN}✓${RESET} Found run.py in ${service_dir}"
        cd "$service_dir" && DEBUG_MODE=false python run.py &
        echo -e "${GREEN}✓${RESET} Started ${service_name}"
        cd - > /dev/null
    else
        echo -e "${RED}✗${RESET} run.py not found in ${service_dir}"
        return 1
    fi
    
    # Wait a moment for the service to start
    sleep 2
    
    # Check if the service is responding
    if curl -s "http://localhost:${port}/health" > /dev/null; then
        echo -e "${GREEN}✓${RESET} ${service_name} is running on port ${port}"
    else
        echo -e "${YELLOW}!${RESET} ${service_name} may not be responding on port ${port} yet"
    fi
    
    return 0
}

# Start Auth Service
echo -e "\n${YELLOW}=== Starting Auth Service ===${RESET}"
start_service "Auth Service" "${SERVICES_DIR}/auth-service" 5002

# Start Profile Service
echo -e "\n${YELLOW}=== Starting Profile Service ===${RESET}"
start_service "Profile Service" "${SERVICES_DIR}/profile-service" 5003

# Start Cart Service
echo -e "\n${YELLOW}=== Starting Cart Service ===${RESET}"
start_service "Cart Service" "${SERVICES_DIR}/cart-service" 5001

# Wait a moment for services to initialize
sleep 3

# Run health check
echo -e "\n${YELLOW}=== Running Health Checks ===${RESET}"

check_service() {
    local service_name=$1
    local port=$2
    
    echo -n "Checking ${service_name} (port ${port}): "
    if curl -s "http://localhost:${port}/health" > /dev/null; then
        echo -e "${GREEN}RUNNING${RESET}"
        return 0
    else
        echo -e "${RED}NOT RESPONDING${RESET}"
        return 1
    fi
}

check_service "Auth Service" 5002
check_service "Profile Service" 5003
check_service "Cart Service" 5001

echo -e "\n${GREEN}All remaining services have been started with DEBUG_MODE=false${RESET}"
echo "These services are now running in the background"
echo "You can verify they're using real database connections with the test_services.py script"
