#!/usr/bin/env python3
"""
Database initialization script for PostgreSQL
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    """Create PostgreSQL database if it doesn't exist"""
    # Get database credentials from environment variables
    user = os.environ.get('POSTGRES_USER', 'hosea')
    password = os.environ.get('POSTGRES_PASSWORD', 'moringa001')
    host = 'localhost'
    port = 5432
    dbname = os.environ.get('POSTGRES_DB', 'product_service_db')
    
    logger.info(f"Checking if database '{dbname}' exists...")
    
    try:
        # Connect to PostgreSQL server (without specifying a database)
        conn = psycopg2.connect(
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        # Check if database exists
        cursor = conn.cursor()
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{dbname}'")
        exists = cursor.fetchone()
        
        if not exists:
            logger.info(f"Creating database '{dbname}'...")
            cursor.execute(f"CREATE DATABASE {dbname}")
            logger.info(f"Database '{dbname}' created successfully")
        else:
            logger.info(f"Database '{dbname}' already exists")
        
        cursor.close()
        conn.close()
        return True
    
    except psycopg2.Error as e:
        logger.error(f"Error creating PostgreSQL database: {str(e)}")
        return False

if __name__ == "__main__":
    if create_database():
        logger.info("Database initialization completed successfully")
        sys.exit(0)
    else:
        logger.error("Database initialization failed")
        sys.exit(1)
