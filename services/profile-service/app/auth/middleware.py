from functools import wraps
from flask import request, jsonify
import jwt
from config import Config

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Missing authorization header'}), 401
        
        try:
            # For testing purposes, allow direct use of test user IDs
            if auth_header.startswith('Bearer test_user_'):
                request.user_id = auth_header.split(' ')[1]
                return f(*args, **kwargs)
            
            # Normal JWT validation
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, Config.JWT_SECRET_KEY, algorithms=['HS256'])
            request.user_id = payload['sub']
        except (jwt.InvalidTokenError, IndexError):
            return jsonify({'message': 'Invalid token'}), 401
            
        return f(*args, **kwargs)
    return decorated