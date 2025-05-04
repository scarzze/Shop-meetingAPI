from functools import wraps
from flask import request, jsonify, current_app
import requests
from dotenv import load_dotenv
import os

load_dotenv()

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
        auth_service_url = current_app.config.get('AUTH_SERVICE_URL', 'http://localhost:5002')
        try:
            response = requests.get(
                f"{auth_service_url}/auth/verify",
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