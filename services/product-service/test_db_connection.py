"""
Test script to verify PostgreSQL database connection
"""
import os
import sys
import psycopg2
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    """Test connection to PostgreSQL database"""
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return False
    
    logger.info(f"Testing connection to: {database_url}")
    
    try:
        # Extract connection parameters from DATABASE_URL
        # Format: postgresql://username:password@host:port/dbname
        db_params = {}
        
        # Remove postgresql:// prefix
        conn_string = database_url.replace('postgresql://', '')
        
        # Split credentials and connection info
        if '@' in conn_string:
            credentials, conn_info = conn_string.split('@', 1)
            
            # Extract username and password
            if ':' in credentials:
                db_params['user'], db_params['password'] = credentials.split(':', 1)
            else:
                db_params['user'] = credentials
                
            # Extract host, port, and database name
            if '/' in conn_info:
                host_port, db_params['dbname'] = conn_info.split('/', 1)
                
                # Extract host and port
                if ':' in host_port:
                    db_params['host'], port = host_port.split(':', 1)
                    db_params['port'] = int(port)
                else:
                    db_params['host'] = host_port
        
        # Connect to the database
        logger.info(f"Connecting to PostgreSQL with params: {db_params}")
        conn = psycopg2.connect(**db_params)
        
        # Test the connection
        cursor = conn.cursor()
        cursor.execute('SELECT version();')
        db_version = cursor.fetchone()
        
        # Close the connection
        cursor.close()
        conn.close()
        
        logger.info(f"Connected successfully to PostgreSQL: {db_version[0]}")
        return True
        
    except psycopg2.Error as e:
        logger.error(f"Error connecting to PostgreSQL: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    # For local testing, you might want to set:
    # os.environ['DATABASE_URL'] = 'postgresql://postgres:postgres@localhost:5432/product_service'
    
    if test_connection():
        logger.info("Database connection test PASSED")
        sys.exit(0)
    else:
        logger.error("Database connection test FAILED")
        sys.exit(1)
