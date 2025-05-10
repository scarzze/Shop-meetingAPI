#!/usr/bin/env python
"""
Script to set up local PostgreSQL databases for all microservices
"""
import os
import sys
import subprocess
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database configuration
POSTGRES_USER = "postgres"  # Default PostgreSQL superuser
POSTGRES_PASSWORD = None     # Will prompt for password if needed
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"

# Service database configurations
SERVICES = [
    {
        "name": "Auth Service",
        "db_name": "auth_service_db",
        "user_name": "auth_user",
        "password": "auth_password",
        "env_file": "services/auth-service/.env",
        "env_var": "DATABASE_URL"
    },
    {
        "name": "Profile Service",
        "db_name": "profile_service_db",
        "user_name": "profile_user",
        "password": "profile_password",
        "env_file": "services/profile-service/.env",
        "env_var": "DATABASE_URL"
    },
    {
        "name": "Cart Service",
        "db_name": "cart_service_db",
        "user_name": "cart_user",
        "password": "cart_password",
        "env_file": "services/cart-service/.env",
        "env_var": "DATABASE_URI"
    },
    {
        "name": "Order Service",
        "db_name": "order_service_db",
        "user_name": "order_user",
        "password": "order_password",
        "env_file": "services/Orderservice/.env",
        "env_var": "DATABASE_URL"
    },
    {
        "name": "Customer Support Service",
        "db_name": "customer_support_db",
        "user_name": "support_user",
        "password": "support_password",
        "env_file": "services/Customer_support_back-end/.env",
        "env_var": "DATABASE_URI"
    },
    {
        "name": "Product Service",
        "db_name": "product_service_db",
        "user_name": "product_user",
        "password": "product_password",
        "env_file": "services/product-service/.env",
        "env_var": "DATABASE_URL"
    }
]

def connect_to_postgres():
    """Connect to PostgreSQL server as superuser"""
    try:
        # First try connecting without password (trust authentication)
        try:
            conn = psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                user=POSTGRES_USER,
                database="postgres"
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            print("Connected to PostgreSQL using trust authentication")
            return conn
        except psycopg2.OperationalError:
            # Trust authentication failed, prompt for password
            import getpass
            password = getpass.getpass(f"Enter password for PostgreSQL user '{POSTGRES_USER}': ")
            
            conn = psycopg2.connect(
                host=POSTGRES_HOST,
                port=POSTGRES_PORT,
                user=POSTGRES_USER,
                password=password,
                database="postgres"
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            print("Connected to PostgreSQL using password authentication")
            return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {str(e)}")
        return None

def create_database(conn, db_name):
    """Create a new database if it doesn't exist"""
    try:
        cur = conn.cursor()
        
        # Check if database exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if cur.fetchone():
            print(f"Database '{db_name}' already exists.")
            return True
        
        # Create database
        cur.execute(f"CREATE DATABASE {db_name}")
        print(f"Created database '{db_name}'")
        return True
    except Exception as e:
        print(f"Error creating database '{db_name}': {str(e)}")
        return False

def create_user(conn, username, password):
    """Create a new PostgreSQL user if it doesn't exist"""
    try:
        cur = conn.cursor()
        
        # Check if user exists
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (username,))
        if cur.fetchone():
            print(f"User '{username}' already exists.")
            return True
        
        # Create user with password
        cur.execute(f"CREATE USER {username} WITH PASSWORD '{password}'")
        print(f"Created user '{username}'")
        return True
    except Exception as e:
        print(f"Error creating user '{username}': {str(e)}")
        return False

def grant_privileges(conn, username, db_name):
    """Grant all privileges on database to user"""
    try:
        cur = conn.cursor()
        cur.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {username}")
        print(f"Granted privileges on '{db_name}' to '{username}'")
        return True
    except Exception as e:
        print(f"Error granting privileges: {str(e)}")
        return False

def update_env_file(env_file, env_var, db_url):
    """Update environment variable in .env file"""
    try:
        if not os.path.exists(env_file):
            print(f"Warning: .env file does not exist: {env_file}")
            return False
        
        with open(env_file, 'r') as f:
            lines = f.readlines()
        
        updated = False
        new_lines = []
        for line in lines:
            if line.startswith(f"{env_var}="):
                new_lines.append(f"{env_var}={db_url}\n")
                updated = True
            else:
                new_lines.append(line)
        
        if not updated:
            new_lines.append(f"{env_var}={db_url}\n")
        
        with open(env_file, 'w') as f:
            f.writelines(new_lines)
        
        print(f"Updated {env_var} in {env_file}")
        return True
    except Exception as e:
        print(f"Error updating .env file: {str(e)}")
        return False

def main():
    """Main function to set up all databases"""
    print("=== Setting up local PostgreSQL databases for microservices ===")
    
    # Connect to PostgreSQL
    conn = connect_to_postgres()
    if not conn:
        print("Failed to connect to PostgreSQL. Make sure PostgreSQL is running.")
        return 1
    
    success = True
    
    # Setup databases for each service
    for service in SERVICES:
        print(f"\nSetting up database for {service['name']}...")
        
        # Create database
        if not create_database(conn, service['db_name']):
            success = False
            continue
        
        # Create user
        if not create_user(conn, service['user_name'], service['password']):
            success = False
            continue
        
        # Grant privileges
        if not grant_privileges(conn, service['user_name'], service['db_name']):
            success = False
            continue
        
        # Update .env file
        db_url = f"postgresql://{service['user_name']}:{service['password']}@{POSTGRES_HOST}:{POSTGRES_PORT}/{service['db_name']}"
        if not update_env_file(service['env_file'], service['env_var'], db_url):
            success = False
            continue
        
        # Also make sure DEBUG_MODE is set to false
        update_env_file(service['env_file'], "DEBUG_MODE", "false")
    
    conn.close()
    
    print("\n=== Summary ===")
    if success:
        print("All database setup operations completed successfully.")
        print("Now you can run the services with real database connections.")
    else:
        print("Some operations failed. Check the details above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
