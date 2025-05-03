from functools import wraps
from flask import request, jsonify, current_app
import requests
import os
from dotenv import load_dotenv
from .logger import log_auth_success, log_auth_failure, log_support_agent_action

load_dotenv()

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
        
        # Verify token with auth service
        auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5002')
        try:
            response = requests.get(
                f"{auth_service_url}/auth/verify",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code != 200:
                log_auth_failure("Invalid token", request.remote_addr, request.endpoint)
                return jsonify({"error": "Invalid token"}), 401
                
            # Add user info to request context
            request.user = response.json().get('user')
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
        
        # Verify token with auth service
        auth_service_url = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5002')
        try:
            response = requests.get(
                f"{auth_service_url}/auth/verify",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code != 200:
                log_auth_failure("Invalid token", request.remote_addr, request.endpoint)
                return jsonify({"error": "Invalid token"}), 401
            
            user = response.json().get('user')
            # Check if user is a support agent
            if not user.get('is_support_agent', False):
                log_auth_failure("Not a support agent", request.remote_addr, request.endpoint)
                return jsonify({"error": "Support agent access required"}), 403
                
            request.user = user
            log_auth_success(request.user['id'], request.endpoint)
            return f(*args, **kwargs)
        except requests.exceptions.RequestException:
            log_auth_failure("Auth service unavailable", request.remote_addr, request.endpoint)
            return jsonify({"error": "Auth service unavailable"}), 503
            
    return decorated_function