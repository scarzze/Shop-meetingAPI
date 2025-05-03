#!/bin/bash

# Database configuration
DB_USER="hosea"
DB_PASSWORD="moringa001"
DB_HOST="localhost"
DB_PORT="5432"

# List of databases to create
DATABASES=(
    "auth_db"
    "cart_db"
    "profile_db"
    "order_db"
    "customer_support_db"
)

# Function to create database if it doesn't exist
create_database() {
    local db_name=$1
    echo "Creating database: $db_name"
    psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c "CREATE DATABASE $db_name;" 2>/dev/null || echo "Database $db_name already exists"
}

# Create each database
for db in "${DATABASES[@]}"
do
    create_database $db
done

echo "Database initialization complete!"