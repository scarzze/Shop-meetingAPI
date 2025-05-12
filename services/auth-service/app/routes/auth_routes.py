from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from email_validator import validate_email, EmailNotValidError
import os

from ..models.user import db, User
from ..utils.auth import check_rate_limit, update_login_attempts

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

@auth_bp.route('/register', methods=['POST'])  # Now becomes /api/v1/auth/register
def register():
    data = request.get_json()
    debug_mode = current_app.config.get('DEBUG_MODE', False)
    
    if not all(k in data for k in ['email', 'password', 'first_name', 'last_name']):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        # Validate email
        valid = validate_email(data['email'])
        email = valid.email
    except EmailNotValidError:
        return jsonify({"error": "Invalid email format"}), 400

    # In DEBUG_MODE, provide a mock response
    if debug_mode:
        # Check if it's the test user
        if email == "test@example.com":
            return jsonify({"error": "Email already registered"}), 409
        
        # Validate password
        if len(data['password']) < 8:
            return jsonify({"error": "Password must be at least 8 characters long"}), 400
            
        # Return success response
        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": 999,
                "email": email,
                "first_name": data['first_name'],
                "last_name": data['last_name'],
                "created_at": datetime.utcnow().isoformat()
            }
        }), 201
    
    # Not in DEBUG_MODE - use database
    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409
    
    # Validate password
    if len(data['password']) < 8:
        return jsonify({"error": "Password must be at least 8 characters long"}), 400
    
    # Create new user
    user = User(
        email=email,
        first_name=data['first_name'],
        last_name=data['last_name']
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])  # Now becomes /api/v1/auth/login
def login():
    data = request.get_json()
    debug_mode = current_app.config.get('DEBUG_MODE', False)
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({"error": "Missing email or password"}), 400
        
    # In DEBUG_MODE, provide mock test credentials
    if debug_mode:
        # Check against test users from memory
        # newuser@example.com with password: password123
        if data['email'] == "newuser@example.com" and data['password'] == "password123":
            access_token = create_access_token(identity="test_user_id")
            refresh_token = create_refresh_token(identity="test_user_id")
            
            return jsonify({
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": 1,
                    "email": "newuser@example.com",
                    "first_name": "Test",
                    "last_name": "User",
                    "role": "user"
                }
            }), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    
    # Not in DEBUG_MODE - use database
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.is_active:
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Check rate limiting
    if not check_rate_limit(user):
        return jsonify({
            "error": "Too many login attempts. Please try again later.",
            "retry_after": "15 minutes"
        }), 429
    
    if not user.check_password(data['password']):
        update_login_attempts(user, success=False)
        db.session.commit()
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Successful login
    update_login_attempts(user, success=True)
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict()
    }), 200

@auth_bp.route('/verify', methods=['GET'])  # Now becomes /api/v1/auth/verify
@jwt_required()
def verify_token():
    """Verify a JWT token and return user info"""
    debug_mode = current_app.config.get('DEBUG_MODE', False)

    try:
        user_id = get_jwt_identity()
        
        # In DEBUG_MODE, provide mock response
        if debug_mode:
            # For test user
            if user_id == "test_user_id":
                return jsonify({
                    "message": "Token is valid",
                    "user": {
                        "id": 1,
                        "email": "newuser@example.com",
                        "first_name": "Test",
                        "last_name": "User",
                        "role": "user"
                    }
                }), 200
        
        # Not in DEBUG_MODE - use database
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({"error": "User not found or inactive"}), 401
            
        return jsonify({
            "message": "Token is valid",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@auth_bp.route('/refresh', methods=['POST'])  # Now becomes /api/v1/auth/refresh
@jwt_required(refresh=True)
def refresh_token():
    """Get a new access token using a refresh token"""
    debug_mode = current_app.config.get('DEBUG_MODE', False)
    
    try:
        user_id = get_jwt_identity()
        
        # In DEBUG_MODE, provide mock response
        if debug_mode:
            # For test user
            if user_id == "test_user_id":
                access_token = create_access_token(identity="test_user_id")
                return jsonify({
                    "access_token": access_token,
                    "message": "Token refreshed successfully"
                }), 200
                
        # Not in DEBUG_MODE - use database
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({"error": "User not found or inactive"}), 401
            
        access_token = create_access_token(identity=user.id)
        return jsonify({
            "access_token": access_token,
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 401