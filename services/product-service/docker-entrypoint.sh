#!/bin/bash
set -e

# Parse the DATABASE_URL to extract host and port for postgres
if [[ $DATABASE_URL == postgresql* ]]; then
    # Extract host and port from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed -E 's/.*@([^:]+):.*/\1/')
    DB_PORT=$(echo $DATABASE_URL | sed -E 's/.*:([0-9]+).*/\1/')
    
    echo "Waiting for PostgreSQL at $DB_HOST:$DB_PORT to become available..."
    
    # Wait for PostgreSQL to be ready
    until PGPASSWORD=$POSTGRES_PASSWORD psql -h $DB_HOST -p $DB_PORT -U $POSTGRES_USER -d $POSTGRES_DB -c '\q'; do
        echo "PostgreSQL is unavailable - sleeping"
        sleep 2
    done
    
    echo "PostgreSQL is up - continuing"
fi

# Initialize the database
echo "Running database migrations..."
flask db upgrade || (flask db init && flask db migrate -m "Initial migration" && flask db upgrade)

# Seed the database if desired
if [ "$SEED_DB" = "true" ]; then
    echo "Seeding the database..."
    python seed.py
fi

# Start the service using Gunicorn
echo "Starting Product Management Service..."
exec gunicorn -c gunicorn_config.py run:app
