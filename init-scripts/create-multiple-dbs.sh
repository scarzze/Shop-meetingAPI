#!/bin/bash

set -e

# Function to create database and grant privileges
create_db() {
    local db=$1
    echo "Creating database: $db"
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
        CREATE DATABASE $db;
        GRANT ALL PRIVILEGES ON DATABASE $db TO $POSTGRES_USER;
EOSQL
}

# Create each database from the list
for db in auth_db cart_db profile_db order_db customer_support_db product_service_db; do
    create_db $db
done
