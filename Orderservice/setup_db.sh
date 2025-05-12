#!/bin/bash

# This script creates the PostgreSQL user and test database for the Orderservice tests.

# Variables
PG_USER="orderservice_user"
PG_PASSWORD="orderservice_pass"
PG_DB="orderservice_test_db"

# Create user with password
psql -U postgres -c "DO \$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = '${PG_USER}'
   ) THEN
      CREATE ROLE ${PG_USER} LOGIN PASSWORD '${PG_PASSWORD}';
   END IF;
END
\$;"

# Create database owned by the user
psql -U postgres -c "DO \$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_database WHERE datname = '${PG_DB}'
   ) THEN
      CREATE DATABASE ${PG_DB} OWNER ${PG_USER};
   END IF;
END
\$;"

# Grant all privileges on database to user
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE ${PG_DB} TO ${PG_USER};"

echo "PostgreSQL user '${PG_USER}' and database '${PG_DB}' setup completed."
