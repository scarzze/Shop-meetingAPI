from functools import wraps
from flask import request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://localhost:5002')

def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "No authorization header"}), 401
            
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Invalid authorization format"}), 401
            
        token = auth_header.split(' ')[1]
        
        # Verify token with auth service
        try:
            response = requests.get(
                f"{AUTH_SERVICE_URL}/auth/verify",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code != 200:
                return jsonify({"error": "Invalid token"}), 401
                
            # Add user info to request context
            request.user = response.json().get('user')
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
        
        # Verify token with auth service
        try:
            response = requests.get(
                f"{AUTH_SERVICE_URL}/auth/verify",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code != 200:
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