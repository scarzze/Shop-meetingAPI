from flask import Blueprint, request, jsonify
from ..models import Profile, db
from ..auth.middleware import auth_required
from ..utils.validators import validate_profile_data

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/', methods=['GET'])
@auth_required
def get_profile():
    """Get the p.rofile of the authenticated user"""
    user_id = request.user['id']
    profile = Profile.query.filter_by(user_id=user_id).first()
    
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
        
    return jsonify(profile.to_dict()), 200

@profile_bp.route('/', methods=['PUT', 'PATCH'])
@auth_required
def update_profile():
    """Update the authenticated user's profile"""
    user_id = request.user['id']
    profile = Profile.query.filter_by(user_id=user_id).first()
    
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
        
    data = request.get_json()
    validation_error = validate_profile_data(data)
    if validation_error:
        return jsonify({"error": validation_error}), 400
        
    # Update profile fields
    for key, value in data.items():
        if hasattr(profile, key):
            setattr(profile, key, value)
            
    try:
        db.session.commit()
        return jsonify(profile.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@profile_bp.route('/preferences', methods=['GET'])
@auth_required
def get_preferences():
    """Get user preferences"""
    user_id = request.user['id']
    profile = Profile.query.filter_by(user_id=user_id).first()
    
    if not profile:
        return jsonify({"error": "Profile not found"}), 404
        
    return jsonify(profile.preferences or {}), 200

@profile_bp.route('/preferences', methods=['PATCH'])
@auth_required
def update_preferences():
    """Update user preferences"""
    user_id = request.user['id']
    profile = Profile.query.filter_by(user_id=user_id).first()
    
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