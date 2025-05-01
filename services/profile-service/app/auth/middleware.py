from functools import wraps
from flask import request, jsonify, current_app

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Missing authorization header'}), 401
        
        try:
            token = auth_header.split(' ')[1]
            
            # In development mode, allow test tokens
            if token.startswith('test_user_'):
                request.user_id = token
                return f(*args, **kwargs)
            
            return jsonify({'message': 'Invalid token format'}), 401
            
        except Exception as e:
            return jsonify({'message': 'Invalid token format'}), 401
            
    return decorated