from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from ..models.user import User, db

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or not user.is_active:
                return jsonify({"error": "Admin access required"}), 403
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Invalid or missing token"}), 401
    return decorated_function

def shared_auth_middleware():
    """Middleware to be used by other services to validate JWT tokens"""
    def middleware():
        try:
            if 'Authorization' not in request.headers:
                return jsonify({"error": "No authorization header"}), 401
                
            auth_header = request.headers['Authorization']
            if not auth_header.startswith('Bearer '):
                return jsonify({"error": "Invalid authorization format"}), 401
                
            token = auth_header.split(' ')[1]
            # Verify token and get user
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user or not user.is_active:
                return jsonify({"error": "User not found or inactive"}), 401
                
            return None  # Authentication successful
        except Exception as e:
            return jsonify({"error": str(e)}), 401
    
    return middleware