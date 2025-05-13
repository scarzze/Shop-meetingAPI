#!/bin/bash

# Script to start all components of Shop-meetingAPI microservices architecture

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Shop-meetingAPI Microservices Starter${NC}"
echo "========================================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start all services
echo -e "${YELLOW}Starting all microservices...${NC}"
./run_services.sh start

# Wait for services to initialize
echo -e "${YELLOW}Waiting for services to initialize...${NC}"
sleep 5

# Start API Gateway
echo -e "${YELLOW}Starting API Gateway...${NC}"
cd api-gateway
python app.py > ../logs/api-gateway.log 2>&1 &
API_GATEWAY_PID=$!
echo $API_GATEWAY_PID > /tmp/api_gateway_pid
cd ..

# Start Frontend
echo -e "${YELLOW}Starting Frontend...${NC}"
cd frontend
node server.js > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > /tmp/frontend_pid
cd ..

echo -e "${GREEN}All components started successfully!${NC}"
echo "API Gateway: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo ""
echo "To stop all components, run: ./stop_all.sh"

# Create stop script
cat > stop_all.sh << 'EOF'
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
EOF

chmod +x stop_all.sh

# Create logs directory if it doesn't exist
mkdir -p logs
