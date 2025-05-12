import os
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

class Config:
    # Base configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ShopMeeting123!ProductServiceSecretKey')
    DEBUG = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
    
    # Database configuration with fallback mechanism
    try:
        # Try to connect to PostgreSQL first
        database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/product_service_db')
        use_sqlite_fallback = os.environ.get('SQLITE_FALLBACK', 'true').lower() == 'true'
        
        # Check if SQLite fallback should be used
        if use_sqlite_fallback:
            try:
                # Test PostgreSQL connection - this will be handled by SQLAlchemy
                # We just set up the config here, actual connection testing happens when app starts
                logger.info(f"Using database URL: {database_url}")
                SQLALCHEMY_DATABASE_URI = database_url
            except Exception as db_error:
                # Fall back to SQLite
                sqlite_url = os.environ.get('SQLITE_DATABASE_URL', 'sqlite:///product_service.db')
                logger.warning(f"Failed to configure PostgreSQL, falling back to SQLite: {sqlite_url}")
                SQLALCHEMY_DATABASE_URI = sqlite_url
        else:
            # Use PostgreSQL without testing
            SQLALCHEMY_DATABASE_URI = database_url
    except Exception as e:
        # If all else fails, use SQLite as last resort
        sqlite_fallback = 'sqlite:///product_service.db'
        logger.error(f"Database configuration error, using emergency SQLite fallback: {str(e)}")
        SQLALCHEMY_DATABASE_URI = sqlite_fallback
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'ShopMeeting123!SharedSecretKey')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Service URLs
    AUTH_SERVICE_URL = os.environ.get('AUTH_SERVICE_URL', 'http://localhost:5002')
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100
    
    # Debug flag
    DEBUG_MODE = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
