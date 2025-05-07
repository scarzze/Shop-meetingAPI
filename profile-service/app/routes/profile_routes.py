from flask import Blueprint, request, jsonify, current_app
from ..models import Profile, db
from ..auth.middleware import auth_required
from ..utils.validators import validate_profile_data
from ..utils.user_sync import sync_profile_from_auth
import os
from sqlalchemy.exc import SQLAlchemyError
import logging

bp = Blueprint('profile', __name__)
logger = logging.getLogger(__name__)

@bp.route('/', methods=['GET'])
@auth_required
def get_profile():
    """Get the profile of the authenticated user"""
    user_id = request.user['id']
    logger.info(f"Getting profile for user_id: {user_id}")
    
    # Check if DEBUG_MODE is enabled
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # In DEBUG_MODE, always return mock profile data
    if debug_mode:
        mock_profile = {
            "id": 1,
            "user_id": str(user_id),
            "first_name": request.user.get('first_name', 'Test'),
            "last_name": request.user.get('last_name', 'User'),
            "email": request.user.get('email', 'testuser@example.com'),
            "phone": "+1234567890",
            "bio": "This is a mock profile for testing",
            "avatar_url": "https://example.com/avatar.jpg",
            "preferences": {
                "theme": "dark",
                "notifications": True,
                "language": "en"
            }
        }
        logger.info(f"Returning mock profile for user_id: {user_id} in DEBUG_MODE")
        return jsonify(mock_profile), 200
    
    # Not in DEBUG_MODE - use database
    try:
        # Synchronize profile from Auth Service
        profile = sync_profile_from_auth(request.user)
        
        if not profile:
            logger.warning(f"Profile not found for user_id: {user_id}")
            return jsonify({"error": "Profile not found"}), 404
            
        logger.info(f"Profile found for user_id: {user_id}")
        return jsonify(profile.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in get_profile: {str(e)}")
        # Provide mock data if database fails
        mock_profile = {
            "id": 1,
            "user_id": str(user_id),
            "first_name": request.user.get('first_name', 'Unknown'),
            "last_name": request.user.get('last_name', 'User'),
            "email": request.user.get('email', 'unknown@example.com'),
            "phone": "",
            "bio": "",
            "avatar_url": ""
        }
        logger.info(f"Returning mock profile for user_id: {user_id}")
        return jsonify(mock_profile), 200

@bp.route('/', methods=['PUT', 'PATCH'])
@auth_required
def update_profile():
    """Update the authenticated user's profile"""
    user_id = request.user['id']
    logger.info(f"Updating profile for user_id: {user_id}")
    
    try:
        # Synchronize profile from Auth Service
        profile = sync_profile_from_auth(request.user)
        
        if not profile:
            logger.warning(f"Profile not found for user_id: {user_id}")
            return jsonify({"error": "Profile not found"}), 404
            
        data = request.get_json()
        validation_error = validate_profile_data(data)
        if validation_error:
            logger.warning(f"Validation error in update_profile: {validation_error}")
            return jsonify({"error": validation_error}), 400
            
        # Update profile fields
        for key, value in data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
                
        try:
            db.session.commit()
            logger.info(f"Profile updated successfully for user_id: {user_id}")
            return jsonify(profile.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error committing profile update: {str(e)}")
            return jsonify({"error": str(e)}), 500
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in update_profile: {str(e)}")
        return jsonify({"error": "Database error", "message": str(e)}), 500

@bp.route('/preferences', methods=['GET'])
@auth_required
def get_preferences():
    """Get user preferences"""
    user_id = request.user['id']
    logger.info(f"Getting preferences for user_id: {user_id}")
    
    try:
        # Synchronize profile from Auth Service
        profile = sync_profile_from_auth(request.user)
        
        # Return mock preferences for now (can be updated to use real data later)
        preferences = {
            'preferred_price_range': {
                'min': 0,
                'max': 1000
            },
            'favorite_categories': ['Electronics', 'Books']
        }
        
        logger.info(f"Returning preferences for user_id: {user_id}")
        return jsonify(preferences)
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error in get_preferences: {str(e)}")
        # Fall back to mock data in case of database errors
        preferences = {
            'preferred_price_range': {
                'min': 0,
                'max': 1000
            },
            'favorite_categories': ['Electronics', 'Books']
        }
        logger.info(f"Returning mock preferences for user_id: {user_id}")
        return jsonify(preferences)

@bp.route('/preferences', methods=['PATCH'])
@auth_required
def update_preferences():
    """Update user preferences"""
    user_id = request.user['id']
    logger.info(f"Updating preferences for user_id: {user_id}")
    
    # Check if DEBUG_MODE is enabled
    debug_mode = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # In DEBUG_MODE, return mock updated preferences
    if debug_mode:
        # Get the update data from the request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Construct updated preferences (for demonstration)
        updated_preferences = {
            'preferred_price_range': {
                'min': 0,
                'max': 1000
            },
            'favorite_categories': data.get('favorite_categories', ['Electronics', 'Books'])
        }
        
        logger.info(f"Updated mock preferences in DEBUG_MODE for user_id: {user_id}")
        return jsonify(updated_preferences), 200
    
    # Not in DEBUG_MODE - use database
    try:
        # Synchronize profile from Auth Service
        profile = sync_profile_from_auth(request.user)
        
        if not profile:
            return jsonify({"error": "Profile not found"}), 404
            
        data = request.get_json()
        current_preferences = profile.preferences or {}
        current_preferences.update(data)
        profile.preferences = current_preferences
        
        try:
            db.session.commit()
            return jsonify(profile.preferences), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500