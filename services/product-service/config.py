import os
from datetime import timedelta

class Config:
    # Base configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'ShopMeeting123!ProductServiceSecretKey')
    DEBUG = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'postgresql://hosea:moringa001@localhost:5432/order_db'
    )
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
