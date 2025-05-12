from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from datetime import datetime, timedelta
from ..models.user import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Invalid or missing token"}), 401
    return decorated_function

def check_rate_limit(user):
    """Check if user has exceeded login attempts"""
    if not user.last_login_attempt:
        return True
        
    time_diff = datetime.utcnow() - user.last_login_attempt
    if user.login_attempts >= 5 and time_diff < timedelta(minutes=15):
        return False
    
    if time_diff >= timedelta(minutes=15):
        user.login_attempts = 0
    
    return True

def update_login_attempts(user, success=False):
    """Update user's login attempts"""
    if success:
        user.login_attempts = 0
    else:
        user.login_attempts += 1
    user.last_login_attempt = datetime.utcnow()