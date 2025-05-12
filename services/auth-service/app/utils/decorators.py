from functools import wraps
from flask import request, jsonify, current_app
import requests
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Invalid or missing token"}), 401
    return decorated_function

def verify_auth_service(auth_service_url=None):
    """Decorator that verifies token with auth service"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({"error": "No authorization header"}), 401
                
            if not auth_header.startswith('Bearer '):
                return jsonify({"error": "Invalid authorization format"}), 401
                
            token = auth_header.split(' ')[1]
            
            # Verify with auth service
            service_url = auth_service_url or current_app.config['AUTH_SERVICE_URL']
            try:
                response = requests.get(
                    f"{service_url}/auth/verify",
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
    return decorator