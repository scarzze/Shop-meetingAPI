#!/bin/bash

# Script to install dependencies for all microservices

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Installing dependencies for Shop-meetingAPI Microservices${NC}"
echo "========================================================"

# Create and activate virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
python -m venv venv
source venv/bin/activate

# Install dependencies for each service
echo -e "${YELLOW}Installing dependencies for API Gateway...${NC}"
pip install -r api-gateway/requirements.txt

echo -e "${YELLOW}Installing dependencies for Auth Service...${NC}"
pip install -r services/auth-service/requirements.txt

echo -e "${YELLOW}Installing dependencies for Profile Service...${NC}"
pip install -r services/profile-service/requirements.txt

echo -e "${YELLOW}Installing dependencies for Product Service...${NC}"
pip install -r services/product-service/requirements.txt

echo -e "${YELLOW}Installing dependencies for Cart Service...${NC}"
pip install -r services/cart-service/requirements.txt

echo -e "${YELLOW}Installing dependencies for Order Service...${NC}"
pip install -r services/order-service/requirements.txt

echo -e "${YELLOW}Installing dependencies for Customer Support Service...${NC}"
pip install -r services/customer-support-service/requirements.txt

echo -e "${GREEN}All dependencies installed successfully!${NC}"
echo "To activate the virtual environment, run: source venv/bin/activate"
