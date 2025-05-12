#!/bin/bash
# Script to update database connection strings across all services

# Get the project root directory
PROJECT_ROOT=$(dirname "$(readlink -f "$0")")

# Define PostgreSQL connection parameters
# Update these with your actual PostgreSQL credentials
PG_USER="hosea"
PG_PASSWORD="moringa001"
PG_HOST="localhost"
PG_PORT="5432"

# Function to update service .env file
update_service_env() {
    local service_dir=$1
    local env_var_name=$2
    local db_name=$3
    local env_file="$PROJECT_ROOT/services/$service_dir/.env"
    
    echo "Updating $service_dir..."
    
    # Create or modify the .env file
    if [ -f "$env_file" ]; then
        # Check if the variable exists in the file
        if grep -q "^$env_var_name=" "$env_file"; then
            # Replace the existing line
            sed -i "s|^$env_var_name=.*|$env_var_name=postgresql://$PG_USER:$PG_PASSWORD@$PG_HOST:$PG_PORT/$db_name|" "$env_file"
        else
            # Add the variable to the file
            echo "$env_var_name=postgresql://$PG_USER:$PG_PASSWORD@$PG_HOST:$PG_PORT/$db_name" >> "$env_file"
        fi
        echo "  Updated $env_file"
    else
        # Create new .env file with the variable
        echo "$env_var_name=postgresql://$PG_USER:$PG_PASSWORD@$PG_HOST:$PG_PORT/$db_name" > "$env_file"
        echo "  Created $env_file"
    fi
    
    # Add DEBUG_MODE=true for development
    if ! grep -q "^DEBUG_MODE=" "$env_file"; then
        echo "DEBUG_MODE=true" >> "$env_file"
        echo "  Added DEBUG_MODE=true"
    fi
}

# Update each service's .env file
update_service_env "auth-service" "DATABASE_URL" "auth_service_db"
update_service_env "profile-service" "DATABASE_URL" "profile_service_db"
update_service_env "cart-service" "DATABASE_URI" "cart_service_db"
update_service_env "Orderservice" "DATABASE_URL" "order_service_db"
update_service_env "Customer_support_back-end" "DATABASE_URI" "customer_support_db"
update_service_env "product-service" "DATABASE_URL" "product_service_db"

echo "Database connections updated for all services."
echo "Don't forget to ensure your PostgreSQL server is running and these databases exist."
echo "You can create the databases with: createdb auth_service_db profile_service_db cart_service_db order_service_db customer_support_db product_service_db"
