#!/bin/bash
# Script to run all microservices with real database connections (DEBUG_MODE=false)

echo "=== Running all microservices with real database connections ==="
echo "This script will set DEBUG_MODE=false for all services"

# Set terminal colors for better visibility
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

SERVICES_DIR="$(pwd)/services"

# Function to update DEBUG_MODE in .env files
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
        # Create new .env file with DEBUG_MODE
        echo "DEBUG_MODE=false" > "$env_file"
        echo -e "${YELLOW}⚠${RESET} Created new .env file with DEBUG_MODE=false in ${env_file}"
    fi
}

# Update all .env files
echo -e "\n${YELLOW}Updating .env files to disable DEBUG_MODE${RESET}"
update_env_file "${SERVICES_DIR}/auth-service"
update_env_file "${SERVICES_DIR}/profile-service"
update_env_file "${SERVICES_DIR}/cart-service"
update_env_file "${SERVICES_DIR}/Orderservice"
update_env_file "${SERVICES_DIR}/Customer_support_back-end"
update_env_file "${SERVICES_DIR}/product-service"

# Function to run a service
run_service() {
    local service_name=$1
    local service_dir=$2
    local run_command=$3
    local port=$4
    
    echo -e "\n${YELLOW}Starting ${service_name}${RESET}"
    echo "Directory: ${service_dir}"
    echo "Command: ${run_command}"
    
    # Run the service in a new terminal window
    # This uses gnome-terminal, but you might need to change depending on your environment
    gnome-terminal --title="${service_name}" -- bash -c "cd \"${service_dir}\" && ${run_command}; read -p 'Press Enter to close...'"
    
    # Wait a moment to allow service to start
    sleep 2
    
    # Check if the service is responding
    if curl -s "http://localhost:${port}/health" > /dev/null; then
        echo -e "${GREEN}✓${RESET} ${service_name} is running on port ${port}"
    else
        echo -e "${RED}✗${RESET} ${service_name} failed to start or is not responding on port ${port}"
    fi
}

# Run all services
echo -e "\n${YELLOW}Starting all services with real database connections${RESET}"

# Auth Service (port 5002)
run_service "Auth Service" "${SERVICES_DIR}/auth-service" "DEBUG_MODE=false python run.py" 5002

# Profile Service (port 5003)
run_service "Profile Service" "${SERVICES_DIR}/profile-service" "DEBUG_MODE=false python run.py" 5003

# Cart Service (port 5001)
run_service "Cart Service" "${SERVICES_DIR}/cart-service" "DEBUG_MODE=false python run.py" 5001

# Order Service (port 5005)
run_service "Order Service" "${SERVICES_DIR}/Orderservice" "DEBUG_MODE=false python run.py" 5005

# Customer Support Service (port 5004)
run_service "Customer Support Service" "${SERVICES_DIR}/Customer_support_back-end" "DEBUG_MODE=false python run.py" 5004

# Product Service (port 5006)
run_service "Product Service" "${SERVICES_DIR}/product-service" "DEBUG_MODE=false python run.py" 5006

echo -e "\n${GREEN}All services have been started with DEBUG_MODE=false${RESET}"
echo "Each service is running in its own terminal window"
echo "You can now test the services with real database connections"

# Run the database connection check script
echo -e "\n${YELLOW}Running database connection check${RESET}"
python check_db_connections.py
