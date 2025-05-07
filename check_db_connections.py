#!/usr/bin/env python
"""
Script to check database connections for all microservices
"""
import os
import sys
import subprocess
from dotenv import load_dotenv
import psycopg2
import requests

load_dotenv()

# Service information
SERVICES = [
    {
        "name": "Auth Service",
        "port": 5002,
        "db_env_var": "DATABASE_URL",
        "db_fallback": None,
        "health_endpoint": "/health"
    },
    {
        "name": "Profile Service",
        "port": 5003,
        "db_env_var": "DATABASE_URL",
        "db_fallback": None,
        "health_endpoint": "/health"
    },
    {
        "name": "Cart Service",
        "port": 5001,
        "db_env_var": "DATABASE_URI",
        "db_fallback": None,
        "health_endpoint": "/health"
    },
    {
        "name": "Order Service",
        "port": 5005,
        "db_env_var": "DATABASE_URL",
        "db_fallback": None,
        "health_endpoint": "/health"
    },
    {
        "name": "Customer Support Service",
        "port": 5004,
        "db_env_var": "DATABASE_URI",
        "db_fallback": "postgresql://victor:password123@localhost/customer_support_db",
        "health_endpoint": "/health"
    },
    {
        "name": "Product Service",
        "port": 5006,
        "db_env_var": "DATABASE_URL",
        "db_fallback": "postgresql://hosea:moringa001@localhost:5432/order_db",
        "health_endpoint": "/health"
    }
]

def test_database_connection(connection_string):
    """Test a PostgreSQL database connection"""
    if not connection_string or not connection_string.startswith('postgresql'):
        print(f"Invalid connection string: {connection_string}")
        return False
    
    try:
        conn = psycopg2.connect(connection_string)
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return False

def test_service_health(service):
    """Test if a service is running and healthy"""
    url = f"http://localhost:{service['port']}{service['health_endpoint']}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True
        print(f"Service health check failed with status code: {response.status_code}")
        return False
    except requests.RequestException as e:
        print(f"Service connection error: {str(e)}")
        return False

def main():
    """Main function to check all connections"""
    print("=== Checking Database Connections and Service Health ===")
    
    # Ensure DEBUG_MODE is disabled for service testing
    os.environ["DEBUG_MODE"] = "False"
    
    all_good = True
    
    for service in SERVICES:
        print(f"\nChecking {service['name']}...")
        
        # Check service health
        print(f"- Health check: ", end="")
        if test_service_health(service):
            print("OK")
        else:
            print("FAILED")
            all_good = False
        
        # Check database connection
        db_url = os.environ.get(service['db_env_var']) or service['db_fallback']
        print(f"- Database connection: ", end="")
        if db_url:
            if test_database_connection(db_url):
                print("OK")
            else:
                print("FAILED")
                all_good = False
        else:
            print("No database URL configured")
            all_good = False
    
    print("\n=== Summary ===")
    if all_good:
        print("All services are running and database connections are working.")
    else:
        print("Some services or database connections failed. Check the details above.")
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())
