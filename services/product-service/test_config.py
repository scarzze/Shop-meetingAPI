#!/usr/bin/env python
"""Test script to verify Product Service configuration and database connectivity"""

import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('product_service_test')

def test_database_connection():
    """Test database connection and create database if it doesn't exist"""
    # Get database URL from environment or use default
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/product_service_db')
    sqlite_fallback = os.environ.get('SQLITE_DATABASE_URL', 'sqlite:///product_service.db')
    
    logger.info(f"Testing connection to: {database_url}")
    
    try:
        # Try PostgreSQL connection
        engine = create_engine(database_url)
        
        # Create database if it doesn't exist (for PostgreSQL)
        if not database_url.startswith('sqlite'):
            if not database_exists(engine.url):
                logger.info(f"Database does not exist. Creating: {database_url}")
                create_database(engine.url)
                logger.info("Database created successfully.")
            else:
                logger.info("Database already exists.")
        
        # Test connection
        connection = engine.connect()
        connection.close()
        logger.info("Successfully connected to the database!")
        return True, database_url
    
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
        logger.info(f"Trying SQLite fallback: {sqlite_fallback}")
        
        try:
            # Try SQLite fallback
            engine = create_engine(sqlite_fallback)
            connection = engine.connect()
            connection.close()
            logger.info("Successfully connected to SQLite fallback!")
            return True, sqlite_fallback
        except Exception as sqlite_error:
            logger.error(f"Failed to connect to SQLite fallback: {str(sqlite_error)}")
            return False, None

def update_env_file(database_url):
    """Update .env file with the correct database URL"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    
    # Read current .env file
    with open(env_path, 'r') as file:
        lines = file.readlines()
    
    # Update or add DATABASE_URL line
    updated = False
    new_lines = []
    for line in lines:
        if line.startswith('DATABASE_URL='):
            new_lines.append(f"DATABASE_URL={database_url}\n")
            updated = True
        else:
            new_lines.append(line)
    
    # Add DATABASE_URL if not found
    if not updated:
        new_lines.append(f"DATABASE_URL={database_url}\n")
    
    # Write updated .env file
    with open(env_path, 'w') as file:
        file.writelines(new_lines)
    
    logger.info(f"Updated .env file with DATABASE_URL={database_url}")

if __name__ == "__main__":
    success, db_url = test_database_connection()
    
    if success and db_url:
        logger.info("Database connection test successful!")
        update_env_file(db_url)
        sys.exit(0)
    else:
        logger.critical("Failed to connect to any database!")
        sys.exit(1)
