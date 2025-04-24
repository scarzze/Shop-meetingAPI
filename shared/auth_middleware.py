from functools import wraps
from flask import request, jsonify
import requests
from flask import current_app

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401

        try:
            # Verify token with auth service
            auth_service_url = current_app.config.get('AUTH_SERVICE_URL', 'http://localhost:5001')
            response = requests.get(
                f'{auth_service_url}/auth/verify',
                headers={'Authorization': auth_header}
            )
            
            if response.status_code != 200:
                return jsonify({'error': 'Invalid or expired token'}), 401
            
            # Add user info to request context
            request.user = response.json()
            return f(*args, **kwargs)
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Auth service error: {str(e)}")
            return jsonify({'error': 'Authentication service unavailable'}), 503
        
    return decorated