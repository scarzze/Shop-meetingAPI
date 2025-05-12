import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    
    # Database settings
    DEBUG_MODE = os.environ.get('DEBUG_MODE', 'False').lower() == 'true'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {
            'sslmode': 'require'
        }
    }
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_VERIFY_CLAIMS = ['exp', 'iat'] if not os.environ.get('FLASK_ENV') == 'development' else []
    JWT_REQUIRED_CLAIMS = ['exp', 'iat'] if not os.environ.get('FLASK_ENV') == 'development' else []
    
    # Service URLs
    PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://localhost:5001')
    AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5002')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
    
    # Redis and Celery
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
    
    # Email Configuration
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    EMAIL_FROM = os.getenv('EMAIL_FROM', 'noreply@yourdomain.com')
    
    # CORS settings
    CORS_ORIGINS = [
        'http://localhost:3000',  # Frontend
        'http://localhost:5000',  # Profile service
        'http://localhost:5001',  # Cart service
        'http://localhost:5002',  # Auth service
    ]
    CORS_HEADERS = 'Content-Type'