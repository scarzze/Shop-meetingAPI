import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your_super_secret_jwt_key')
    DEBUG_MODE = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
    
    # Set up database connection with fallback to SQLite in debug mode
    try:
        # First try the main database URL
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        
        # In debug mode, test the connection and fall back to SQLite if it fails
        if DEBUG_MODE:
            import sqlalchemy
            engine = sqlalchemy.create_engine(SQLALCHEMY_DATABASE_URI, connect_args={})
            connection = engine.connect()
            connection.close()
    except Exception as e:
        if DEBUG_MODE and os.environ.get('SQLITE_FALLBACK_URL'):
            print(f"Warning: Could not connect to PostgreSQL, falling back to SQLite: {str(e)}")
            SQLALCHEMY_DATABASE_URI = os.environ.get('SQLITE_FALLBACK_URL')
        else:
            # Keep the original URL in production, even if it causes an error
            print(f"Database connection issue: {str(e)}")
            
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Only require SSL in production mode, not in debug/development mode
    if DEBUG_MODE:
        SQLALCHEMY_ENGINE_OPTIONS = {}  # No SSL in debug mode
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {
            'connect_args': {
                'sslmode': 'require'
            }
        }
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your_super_secret_jwt_key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS settings
    CORS_ORIGINS = [
        'http://localhost:5000',  # Main application
        'http://localhost:5001',  # Cart service
        'http://localhost:5002',  # Auth service
        'http://localhost:5003',  # Profile service
        # Add production URLs here when deploying
    ]
    
    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day"
    RATELIMIT_STORAGE_URL = "memory://"  # Use Redis in production
    
    # Service URLs
    CART_SERVICE_URL = os.environ.get('CART_SERVICE_URL', 'http://localhost:5001')
    PROFILE_SERVICE_URL = os.environ.get('PROFILE_SERVICE_URL', 'http://localhost:5003')