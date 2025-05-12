#!/bin/bash

# Wait for Postgres to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h postgres -p 5432 -U profile_user
do
    sleep 2
done

# Initialize the database
echo "Initializing database..."
python init_db.py

# Start the health check server in the background
echo "Starting health check server..."
python direct_health_server.py &

# Start the main application
echo "Starting application..."
exec gunicorn --bind 0.0.0.0:5003 --workers 2 --timeout 120 --log-level debug "run:app"