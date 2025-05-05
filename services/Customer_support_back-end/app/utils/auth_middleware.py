from functools import wraps
from flask import request, jsonify, current_app
import requests
import os
import logging
from dotenv import load_dotenv
from .logger import log_auth_success, log_auth_failure, log_support_agent_action

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('auth_middleware')

# Get DEBUG_MODE from environment variable
DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            log_auth_failure("No authorization header", request.remote_addr, request.endpoint)
            return jsonify({"error": "No authorization header"}), 401
            
        if not auth_header.startswith('Bearer '):
            log_auth_failure("Invalid authorization format", request.remote_addr, request.endpoint)
            return jsonify({"error": "Invalid authorization format"}), 401
            
        token = auth_header.split(' ')[1]
        
        # For debugging purposes, log token information
        logger.info(f"Authenticating request with token: {token[:10]}...")
        
        # TEMPORARY TESTING MODE - for development only
        # This allows us to bypass auth service communication issues temporarily
        if DEBUG_MODE:
            logger.warning("DEBUG MODE ENABLED: Bypassing authentication verification")
            mock_user = {
                'id': 1,
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'user',
                'is_admin': False,
                'is_support_agent': False
            }
            request.user = mock_user
            log_auth_success(request.user['id'], request.endpoint)
            return f(*args, **kwargs)
            
        # Verify token with auth service
        auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5002')
        try:
            logger.info(f"Making request to {auth_service_url}/auth/verify")
            response = requests.get(
                f"{auth_service_url}/auth/verify",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            logger.info(f"Auth service response: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Invalid token response: {response.text}")
                log_auth_failure("Invalid token", request.remote_addr, request.endpoint)
                return jsonify({"error": "Invalid token"}), 401
                
            # Add user info to request context
            user_data = response.json().get('user')
            logger.info(f"Authenticated user: {user_data.get('email')}")
            request.user = user_data
            log_auth_success(request.user['id'], request.endpoint)
            return f(*args, **kwargs)
        except requests.exceptions.RequestException:
            log_auth_failure("Auth service unavailable", request.remote_addr, request.endpoint)
            return jsonify({"error": "Auth service unavailable"}), 503
            
    return decorated_function

def support_agent_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            log_auth_failure("No authorization header", request.remote_addr, request.endpoint)
            return jsonify({"error": "No authorization header"}), 401
            
        if not auth_header.startswith('Bearer '):
            log_auth_failure("Invalid authorization format", request.remote_addr, request.endpoint)
            return jsonify({"error": "Invalid authorization format"}), 401
            
        token = auth_header.split(' ')[1]
        
        # For debugging purposes, log token information
        logger.info(f"Authenticating support agent request with token: {token[:10]}...")
        
        # TEMPORARY TESTING MODE - for development only
        # This allows us to bypass auth service communication issues temporarily
        if DEBUG_MODE:
            logger.warning("DEBUG MODE ENABLED: Bypassing support agent authentication verification")
            mock_agent = {
                'id': 2,
                'email': 'support@example.com',
                'first_name': 'Support',
                'last_name': 'Agent',
                'role': 'support_agent',
                'is_admin': False,
                'is_support_agent': True
            }
            request.user = mock_agent
            log_auth_success(request.user['id'], request.endpoint)
            log_support_agent_action(request.user['id'], request.endpoint, 'debug_mode_access')
            return f(*args, **kwargs)
            
        # Verify token with auth service
        auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5002')
        try:
            logger.info(f"Making support agent request to {auth_service_url}/auth/verify")
            response = requests.get(
                f"{auth_service_url}/auth/verify",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            logger.info(f"Auth service support agent response: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Invalid support agent token response: {response.text}")
                log_auth_failure("Invalid token", request.remote_addr, request.endpoint)
                return jsonify({"error": "Invalid token"}), 401
            
            user = response.json().get('user')
            # Check if user is a support agent
            if not user.get('is_support_agent', False):
                logger.error(f"User is not a support agent: {user.get('email')}")
                log_auth_failure("Not a support agent", request.remote_addr, request.endpoint)
                return jsonify({"error": "Support agent access required"}), 403
                
            request.user = user
            log_auth_success(request.user['id'], request.endpoint)
            return f(*args, **kwargs)
        except requests.exceptions.RequestException:
            log_auth_failure("Auth service unavailable", request.remote_addr, request.endpoint)
            return jsonify({"error": "Auth service unavailable"}), 503
            
    return decorated_function