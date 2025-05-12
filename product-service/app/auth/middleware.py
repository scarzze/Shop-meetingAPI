from functools import wraps
from flask import request, jsonify, current_app
import requests
import logging

logger = logging.getLogger(__name__)

def auth_required(f):
    """Decorator to require authentication for endpoints"""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            logger.warning("No Authorization header provided")
            return jsonify({"error": "Authorization header is required"}), 401
            
        token = auth_header.split(' ')[1] if len(auth_header.split(' ')) > 1 else auth_header
        
        # Verify token with auth service
        try:
            auth_service_url = current_app.config.get('AUTH_SERVICE_URL', 'http://localhost:5002')
            response = requests.get(
                f"{auth_service_url}/auth/verify",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if response.status_code != 200:
                logger.warning(f"Token verification failed: {response.json().get('error', 'Unknown error')}")
                return jsonify({"error": "Invalid or expired token"}), 401
                
            # Attach user data to request
            request.user = response.json().get('user', {})
            logger.debug(f"User authenticated: {request.user.get('id')}")
            
            return f(*args, **kwargs)
        except requests.RequestException as e:
            logger.error(f"Error connecting to auth service: {str(e)}")
            
            # In debug mode, allow requests through with mock user data
            if current_app.config.get('DEBUG_MODE', False):
                logger.warning("DEBUG MODE: Bypassing authentication")
                request.user = {
                    'id': 'test-user-id',
                    'email': 'test@example.com',
                    'first_name': 'Test',
                    'last_name': 'User'
                }
                return f(*args, **kwargs)
                
            return jsonify({"error": "Authentication service unavailable"}), 503
            
    return decorated
