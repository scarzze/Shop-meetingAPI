#!/bin/bash

# Script to run all microservices for Shop-meetingAPI

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Shop-meetingAPI Microservices Launcher${NC}"
echo "========================================"

# Function to check if a port is already in use
port_in_use() {
  lsof -i:$1 >/dev/null 2>&1
  return $?
}

# Function to run a service
run_service() {
  local service_name=$1
  local port=$2
  
  echo -e "${YELLOW}Starting $service_name on port $port...${NC}"
  
  # Check if port is already in use
  if port_in_use $port; then
    echo -e "${RED}Port $port is already in use. Cannot start $service_name.${NC}"
    return 1
  fi
  
  # Change to service directory
  cd ./services/$service_name
  
  # Run the service in the background
  FLASK_APP=app.py FLASK_ENV=development python -m flask run --port=$port &
  
  # Store the PID
  local pid=$!
  echo "$pid" > /tmp/${service_name}_pid
  
  echo -e "${GREEN}$service_name started with PID $pid${NC}"
  
  # Return to the root directory
  cd ../..
}

# Function to stop a service
stop_service() {
  local service_name=$1
  
  if [ -f "/tmp/${service_name}_pid" ]; then
    local pid=$(cat /tmp/${service_name}_pid)
    echo -e "${YELLOW}Stopping $service_name (PID: $pid)...${NC}"
    kill $pid 2>/dev/null
    rm /tmp/${service_name}_pid
    echo -e "${GREEN}$service_name stopped${NC}"
  else
    echo -e "${RED}$service_name is not running${NC}"
  fi
}

# Function to stop all services
stop_all_services() {
  echo -e "${YELLOW}Stopping all services...${NC}"
  
  for service in auth-service profile-service product-service cart-service order-service customer-support-service; do
    stop_service $service
  done
  
  echo -e "${GREEN}All services stopped${NC}"
}

# Handle command-line arguments
case "$1" in
  start)
    # Run all services
    run_service auth-service 5001
    sleep 2  # Wait for auth service to start
    
    run_service profile-service 5002
    run_service product-service 5003
    run_service cart-service 5004
    run_service order-service 5005
    run_service customer-support-service 5006
    
    echo -e "${GREEN}All services started${NC}"
    echo "Auth Service: http://localhost:5001"
    echo "Profile Service: http://localhost:5002"
    echo "Product Service: http://localhost:5003"
    echo "Cart Service: http://localhost:5004"
    echo "Order Service: http://localhost:5005"
    echo "Customer Support Service: http://localhost:5006"
    ;;
    
  stop)
    stop_all_services
    ;;
    
  restart)
    stop_all_services
    sleep 2
    
    run_service auth-service 5001
    sleep 2
    
    run_service profile-service 5002
    run_service product-service 5003
    run_service cart-service 5004
    run_service order-service 5005
    run_service customer-support-service 5006
    
    echo -e "${GREEN}All services restarted${NC}"
    ;;
    
  status)
    echo -e "${YELLOW}Checking service status...${NC}"
    
    for service in auth-service profile-service product-service cart-service order-service customer-support-service; do
      if [ -f "/tmp/${service}_pid" ]; then
        local pid=$(cat /tmp/${service}_pid)
        if ps -p $pid > /dev/null; then
          echo -e "${GREEN}$service is running (PID: $pid)${NC}"
        else
          echo -e "${RED}$service is not running (stale PID file)${NC}"
          rm /tmp/${service}_pid
        fi
      else
        echo -e "${RED}$service is not running${NC}"
      fi
    done
    ;;
    
  *)
    echo "Usage: $0 {start|stop|restart|status}"
    exit 1
    ;;
esac

exit 0
