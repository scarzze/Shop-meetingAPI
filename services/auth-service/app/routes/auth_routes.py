from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

from ..models.user import db, User
from ..utils.auth import check_rate_limit, update_login_attempts

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'password', 'first_name', 'last_name']):
        return jsonify({"error": "Missing required fields"}), 400
    
    try:
        # Validate email
        valid = validate_email(data['email'])
        email = valid.email
    except EmailNotValidError:
        return jsonify({"error": "Invalid email format"}), 400

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

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({"error": "Missing email or password"}), 400
    
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

@auth_bp.route('/verify', methods=['GET'])
@jwt_required()
def verify_token():
    """Verify a JWT token and return user info"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({"error": "User not found or inactive"}), 401
            
        return jsonify({
            "message": "Token is valid",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Get a new access token using a refresh token"""
    try:
        user_id = get_jwt_identity()
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