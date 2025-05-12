#!/bin/bash
# Script to create all required databases for Shop-meetingAPI

# PostgreSQL credentials
PGUSER="hosea"
PGPASSWORD="moringa001"
PGHOST="localhost"
PGPORT="5432"

# List of databases to create
databases=(
    "auth_service_db"
    "profile_service_db"
    "cart_service_db"
    "order_service_db"
    "customer_support_db"
    "product_service_db"
)

# Export credentials for psql commands
export PGPASSWORD="$PGPASSWORD"

echo "Creating databases for Shop-meetingAPI..."

for db in "${databases[@]}"; do
    echo "Checking if $db exists..."
    # Check if database exists
    if psql -U "$PGUSER" -h "$PGHOST" -p "$PGPORT" -lqt | cut -d \| -f 1 | grep -qw "$db"; then
        echo "Database $db already exists."
    else
        echo "Creating database $db..."
        createdb -U "$PGUSER" -h "$PGHOST" -p "$PGPORT" "$db"
        if [ $? -eq 0 ]; then
            echo "Database $db created successfully."
        else
            echo "Failed to create database $db!"
        fi
    fi
done

echo "Database setup complete!"
