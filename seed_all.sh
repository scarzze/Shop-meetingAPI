#!/bin/bash

# Script to seed all databases for Shop-meetingAPI microservices

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Seeding databases for Shop-meetingAPI Microservices${NC}"
echo "========================================================"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Function to seed a service database
seed_service() {
    local service_name=$1
    
    echo -e "${YELLOW}Seeding database for $service_name...${NC}"
    
    # Change to service directory
    cd ./services/$service_name
    
    # Run the seed script
    python seed.py
    
    # Check if seeding was successful
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Successfully seeded database for $service_name${NC}"
    else
        echo -e "${RED}Failed to seed database for $service_name${NC}"
    fi
    
    # Return to the root directory
    cd ../..
}

# Seed databases for each service
seed_service auth-service
seed_service profile-service
seed_service product-service
seed_service cart-service
seed_service order-service
seed_service customer-support-service

echo -e "${GREEN}All databases seeded successfully!${NC}"
echo "You can now run the services using: ./run_services.sh start"
