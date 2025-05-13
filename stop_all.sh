#!/bin/bash

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping all components...${NC}"

# Stop Frontend
if [ -f "/tmp/frontend_pid" ]; then
    FRONTEND_PID=$(cat /tmp/frontend_pid)
    echo -e "${YELLOW}Stopping Frontend (PID: $FRONTEND_PID)...${NC}"
    kill $FRONTEND_PID 2>/dev/null
    rm /tmp/frontend_pid
fi

# Stop API Gateway
if [ -f "/tmp/api_gateway_pid" ]; then
    API_GATEWAY_PID=$(cat /tmp/api_gateway_pid)
    echo -e "${YELLOW}Stopping API Gateway (PID: $API_GATEWAY_PID)...${NC}"
    kill $API_GATEWAY_PID 2>/dev/null
    rm /tmp/api_gateway_pid
fi

# Stop all microservices
echo -e "${YELLOW}Stopping all microservices...${NC}"
./run_services.sh stop

echo -e "${GREEN}All components stopped successfully!${NC}"
