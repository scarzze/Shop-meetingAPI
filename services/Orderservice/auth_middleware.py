from functools import wraps
from flask import request, jsonify
import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5002')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('auth_middleware')

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "No authorization header"}), 401
            
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Invalid authorization format"}), 401
            
        token = auth_header.split(' ')[1]
        
        # For debugging purposes, log token information
        logger.info(f"Authenticating request with token: {token[:10]}...")
        
        # TEMPORARY TESTING MODE - for development only
        # This allows us to bypass auth service communication issues temporarily
        if DEBUG_MODE:
            logger.warning("DEBUG MODE ENABLED: Bypassing authentication verification")
            request.user = {
                'id': 1,  # Use a simple numeric ID for order service
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'user',
                'is_admin': False
            }
            return f(*args, **kwargs)
            
        # Verify token with auth service
        try:
            logger.info(f"Making request to {AUTH_SERVICE_URL}/auth/verify")
            response = requests.get(
                f"{AUTH_SERVICE_URL}/auth/verify",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            logger.info(f"Auth service response: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Invalid token response: {response.text}")
                return jsonify({"error": "Invalid token"}), 401
                
            # Add user info to request context
            user_data = response.json().get('user')
            logger.info(f"Authenticated user: {user_data.get('email')}")
            request.user = user_data
            return f(*args, **kwargs)
        except requests.exceptions.RequestException:
            return jsonify({"error": "Auth service unavailable"}), 503
            
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "No authorization header"}), 401
            
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Invalid authorization format"}), 401
            
        token = auth_header.split(' ')[1]
        
        # For debugging purposes, log token information
        logger.info(f"Authenticating admin request with token: {token[:10]}...")
        
        # TEMPORARY TESTING MODE - for development only
        # This allows us to bypass auth service communication issues temporarily
        if DEBUG_MODE:
            logger.warning("DEBUG MODE ENABLED: Bypassing admin authentication verification")
            request.user = {
                'id': 1,  # Use a simple numeric ID for order service
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_admin': True
            }
            return f(*args, **kwargs)
            
        # Verify token with auth service
        try:
            logger.info(f"Making admin request to {AUTH_SERVICE_URL}/auth/verify")
            response = requests.get(
                f"{AUTH_SERVICE_URL}/auth/verify",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            logger.info(f"Auth service admin response: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Invalid admin token response: {response.text}")
                return jsonify({"error": "Invalid token"}), 401
            
            user = response.json().get('user')
            # Check if user is admin (you might want to add an is_admin field to your user model)
            if not user.get('is_admin', False):
                return jsonify({"error": "Admin access required"}), 403
                
            request.user = user
            return f(*args, **kwargs)
        except requests.exceptions.RequestException:
            return jsonify({"error": "Auth service unavailable"}), 503
            
    return decorated_function