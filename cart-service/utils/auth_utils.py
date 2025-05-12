import os
import jwt
import requests
from functools import wraps
from flask import request, jsonify

class AuthUtils:
    """
    Shared authentication utility for Shop Meeting API microservices.
    This allows services to communicate with the Auth Service securely
    and validates tokens without relying on DEBUG_MODE.
    """
    
    def __init__(self, auth_service_url=None, jwt_secret=None):
        self.auth_service_url = auth_service_url or os.getenv('AUTH_SERVICE_URL', 'http://localhost:5002')
        self.jwt_secret = jwt_secret or os.getenv('JWT_SECRET_KEY', 'your_super_secret_jwt_key')
        
        # Flag for using DEBUG_MODE - should be False in production
        self.debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
        
    def verify_token(self, token):
        """
        Verify a JWT token by either:
        1. Calling the Auth Service's /auth/verify endpoint (production)
        2. Directly decoding the token using JWT_SECRET_KEY (fallback) 
        3. Using a mock user if DEBUG_MODE is enabled
        
        Returns: User data dictionary if verified, None if invalid
        """
        if self.debug_mode:
            # In debug mode, return a mock user
            return {
                'id': 1,
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
                'role': 'user',
                'is_admin': False,
                'is_support_agent': False
            }
            
        # First try to verify with the Auth Service
        try:
            response = requests.get(
                f"{self.auth_service_url}/auth/verify",
                headers={'Authorization': f'Bearer {token}'},
                timeout=2  # Set a reasonable timeout
            )
            
            if response.status_code == 200:
                return response.json().get('user')
        except requests.exceptions.RequestException:
            # If Auth Service is unavailable, fall back to local verification
            pass
            
        # Fallback: Try to decode the token directly
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            user_id = payload.get('sub')
            
            # Minimal user info when using fallback method
            return {
                'id': user_id,
                'role': 'user'
            }
        except jwt.PyJWTError:
            return None
            
    def auth_required(self, f):
        """
        Decorator for endpoints that require authentication
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({"error": "No authorization header"}), 401
                
            if not auth_header.startswith('Bearer '):
                return jsonify({"error": "Invalid authorization format"}), 401
                
            token = auth_header.split(' ')[1]
            
            user = self.verify_token(token)
            if not user:
                return jsonify({"error": "Invalid token"}), 401
                
            # Add user info to request context
            request.user = user
            
            # For backward compatibility with existing code
            if isinstance(user, dict) and 'id' in user:
                request.user_id = user['id']
                
            return f(*args, **kwargs)
        return decorated_function
        
    def admin_required(self, f):
        """
        Decorator for endpoints that require admin privileges
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({"error": "No authorization header"}), 401
                
            if not auth_header.startswith('Bearer '):
                return jsonify({"error": "Invalid authorization format"}), 401
                
            token = auth_header.split(' ')[1]
            
            user = self.verify_token(token)
            if not user:
                return jsonify({"error": "Invalid token"}), 401
                
            if not user.get('is_admin', False):
                return jsonify({"error": "Admin access required"}), 403
                
            # Add user info to request context
            request.user = user
            
            # For backward compatibility with existing code
            if isinstance(user, dict) and 'id' in user:
                request.user_id = user['id']
                
            return f(*args, **kwargs)
        return decorated_function
        
    def support_agent_required(self, f):
        """
        Decorator for Customer Support Service endpoints
        """
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({"error": "No authorization header"}), 401
                
            if not auth_header.startswith('Bearer '):
                return jsonify({"error": "Invalid authorization format"}), 401
                
            token = auth_header.split(' ')[1]
            
            user = self.verify_token(token)
            if not user:
                return jsonify({"error": "Invalid token"}), 401
                
            if not user.get('is_support_agent', False):
                return jsonify({"error": "Support agent access required"}), 403
                
            # Add user info to request context
            request.user = user
            
            # For backward compatibility with existing code
            if isinstance(user, dict) and 'id' in user:
                request.user_id = user['id']
                
            return f(*args, **kwargs)
        return decorated_function

# Create a singleton instance
auth_utils = AuthUtils()

# Export decorators for easy import by services
auth_required = auth_utils.auth_required
admin_required = auth_utils.admin_required
support_agent_required = auth_utils.support_agent_required
