#!/bin/bash
# Script to run all microservices with real database connections (DEBUG_MODE=false)

echo "=== Running microservices with real database connections ==="

# Set terminal colors for better visibility
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
RESET="\033[0m"

# Update all .env files to disable DEBUG_MODE
update_env_files() {
    echo -e "\n${YELLOW}Disabling DEBUG_MODE in all services${RESET}"
    
    # Auth Service
    if [ -f "services/auth-service/.env" ]; then
        sed -i 's/DEBUG_MODE=.*/DEBUG_MODE=false/' services/auth-service/.env
        echo -e "${GREEN}✓${RESET} Updated Auth Service"
    fi
    
    # Profile Service
    if [ -f "services/profile-service/.env" ]; then
        sed -i 's/DEBUG_MODE=.*/DEBUG_MODE=false/' services/profile-service/.env
        echo -e "${GREEN}✓${RESET} Updated Profile Service"
    fi
    
    # Order Service
    if [ -f "services/Orderservice/.env" ]; then
        sed -i 's/DEBUG_MODE=.*/DEBUG_MODE=false/' services/Orderservice/.env
        echo -e "${GREEN}✓${RESET} Updated Order Service"
    fi
    
    # Customer Support Service
    if [ -f "services/Customer_support_back-end/.env" ]; then
        sed -i 's/DEBUG_MODE=.*/DEBUG_MODE=false/' services/Customer_support_back-end/.env
        echo -e "${GREEN}✓${RESET} Updated Customer Support Service"
    fi
    
    # Product Service
    if [ -f "services/product-service/.env" ]; then
        sed -i 's/DEBUG_MODE=.*/DEBUG_MODE=false/' services/product-service/.env
        echo -e "${GREEN}✓${RESET} Updated Product Service"
    fi
    
    # Cart Service
    if [ -f "services/cart-service/.env" ]; then
        sed -i 's/DEBUG_MODE=.*/DEBUG_MODE=false/' services/cart-service/.env
        echo -e "${GREEN}✓${RESET} Updated Cart Service"
    fi
}

# Start the working services
start_working_services() {
    echo -e "\n${YELLOW}Starting services with known working database connections${RESET}"
    
    # Order Service
    echo -e "\n${YELLOW}Starting Order Service on port 5005${RESET}"
    cd services/Orderservice
    python run.py &
    ORDER_PID=$!
    cd ../..
    sleep 2
    
    # Customer Support Service
    echo -e "\n${YELLOW}Starting Customer Support Service on port 5004${RESET}"
    cd services/Customer_support_back-end
    python run.py &
    SUPPORT_PID=$!
    cd ../..
    sleep 2
    
    # Product Service
    echo -e "\n${YELLOW}Starting Product Service on port 5006${RESET}"
    cd services/product-service
    python run.py &
    PRODUCT_PID=$!
    cd ../..
    sleep 2
    
    echo -e "\n${GREEN}Started services with real database connections${RESET}"
    echo "PIDs: Order:$ORDER_PID Support:$SUPPORT_PID Product:$PRODUCT_PID"
    
    # Run some basic health checks
    echo -e "\n${YELLOW}Running health checks for started services${RESET}"
    
    if curl -s http://localhost:5005/health > /dev/null; then
        echo -e "${GREEN}✓${RESET} Order Service is running"
    else
        echo -e "${RED}✗${RESET} Order Service is not responding"
    fi
    
    if curl -s http://localhost:5004/health > /dev/null; then
        echo -e "${GREEN}✓${RESET} Customer Support Service is running"
    else
        echo -e "${RED}✗${RESET} Customer Support Service is not responding"
    fi
    
    if curl -s http://localhost:5006/health > /dev/null; then
        echo -e "${GREEN}✓${RESET} Product Service is running"
    else
        echo -e "${RED}✗${RESET} Product Service is not responding"
    fi
}

# Main execution
update_env_files
start_working_services

echo -e "\n${GREEN}Services are running with real database connections${RESET}"
echo "Press Ctrl+C to stop all services"

# Wait for user to press Ctrl+C
trap "kill $ORDER_PID $SUPPORT_PID $PRODUCT_PID; echo -e '\n${YELLOW}Stopping all services${RESET}'" INT
wait
