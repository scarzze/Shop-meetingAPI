import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your_super_secret_jwt_key')
    DEBUG_MODE = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
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